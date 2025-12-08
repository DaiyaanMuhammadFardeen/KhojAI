# prompt_analyzer_llm.py
# Clean, fast, ROCm-friendly version – works perfectly with ollama-rocm

import json
import time
import threading
import hashlib
import asyncio
from typing import List, Dict, Any
from colorama import Fore, Style, init

import ollama
from keybert import KeyBERT
import spacy
from spacy.matcher import Matcher

# Try importing user-defined intent patterns
try:
    from patterns import patterns  # dict: intent_name -> list[pattern]
except Exception:
    patterns = {}

# Simple in-memory cache for LLM responses
_llm_response_cache = {}

init(autoreset=True)

# ———————————————————————— CONFIG ————————————————————————
MODEL_NAME = "gemma3:270m"        # change to gemma3, llama3.2, phi4, etc.
MAX_SEARCH_QUERIES = 5
TOP_KEYWORDS = 10

# Fixed intent list (add your own if you have patterns.py, otherwise this is used)
INTENT_LIST = [
    "question_answering", "web_search", "code_generation", "code_debugging",
    "write_content", "summarize", "translate", "analyze_data", "math_calculation",
    "comparison", "creative_writing", "opinion", "casual_chat", "other"
]

# —————————————————— LAZY SINGLETONS (no double init!) ——————————————————
_ollama_client = None
_kw_model = None
_nlp = None
_matcher = None
_lock = threading.Lock()

def get_ollama():
    global _ollama_client
    if _ollama_client is None:
        with _lock:
            if _ollama_client is None:
                print(Fore.CYAN + "[INFO] Connecting to Ollama..." + Style.RESET_ALL)
                _ollama_client = ollama.Client()  # connects to localhost:11434
                # Simple health check
                try:
                    _ollama_client.list()
                    print(Fore.GREEN + f"[OK] Ollama ready → {MODEL_NAME}" + Style.RESET_ALL)
                except Exception as e:
                    print(Fore.RED + f"[ERROR] Cannot reach Ollama: {e}" + Style.RESET_ALL)
                    _ollama_client = None
    return _ollama_client

def get_keybert():
    global _kw_model
    if _kw_model is None:
        with _lock:
            if _kw_model is None:
                print(Fore.CYAN + "[INFO] Loading KeyBERT..." + Style.RESET_ALL)
                _kw_model = KeyBERT("all-MiniLM-L6-v2")
                print(Fore.GREEN + "[OK] KeyBERT ready" + Style.RESET_ALL)
    return _kw_model

def get_spacy_pipeline():
    """Lazily initialize and cache spaCy pipeline + matcher."""
    global _nlp, _matcher
    if _nlp is None:
        with _lock:
            if _nlp is None:
                print(Fore.CYAN + "[INFO] Loading spaCy model..." + Style.RESET_ALL)
                _nlp = spacy.load("en_core_web_sm", disable=["ner"])
                _matcher = Matcher(_nlp.vocab)
                for intent_name, intent_patterns in patterns.items():
                    _matcher.add(intent_name, intent_patterns)
                print(Fore.GREEN + "[OK] spaCy initialized." + Style.RESET_ALL)
    return _nlp, _matcher

# Warm-up in background (only once)
threading.Thread(target=lambda: (get_ollama(), get_keybert(), get_spacy_pipeline()), daemon=True).start()
time.sleep(0.1)  # let thread start


def _hash_prompt(prompt: str, keywords: List[Dict], intents: List[str]) -> str:
    """Create a hash of the prompt and context for caching."""
    content = f"{prompt}|{json.dumps(keywords)}|{json.dumps(intents)}"
    return hashlib.md5(content.encode()).hexdigest()

# ———————————————————————— MAIN ANALYZER ————————————————————————
async def analyze_prompt(prompt: str, debug: bool = False) -> Dict[str, Any]:
    start_time = time.perf_counter()

    # Clean prompt
    cleaned = prompt.strip()
    if cleaned.lower().startswith(("user:", "ai:")):
        cleaned = cleaned.split(":", 1)[1].strip()

    # 1. Intent detection using spaCy patterns (legacy approach) and KeyBERT keywords (fast & deterministic)
    # Run both operations concurrently for better performance
    
    async def get_spacy_results():
        nlp, matcher = get_spacy_pipeline()
        doc = nlp(cleaned.lower())
        matches = matcher(doc)
        intents = list({nlp.vocab.strings[mid] for mid, _, _ in matches}) or ["casual_chat"]
        return nlp, doc, intents
    
    async def get_keybert_results():
        kw_model = get_keybert()
        if kw_model:
            raw_kws = kw_model.extract_keywords(
                cleaned,
                keyphrase_ngram_range=(1, 3),
                stop_words="english",
                use_mmr=True,
                diversity=0.5,
                top_n=20
            )
            keywords = [{"term": k, "score": round(s, 4)} for k, s in raw_kws][:TOP_KEYWORDS]
            return keywords
        else:
            return []
    
    # Run both operations concurrently
    spacy_task = get_spacy_results()
    keybert_task = get_keybert_results()
    
    # Wait for results
    nlp, doc, intents = await spacy_task
    keywords = await keybert_task

    # 3. LLM call for search queries only (single, safe, no double client)
    client = get_ollama()
    if not client:
        raise RuntimeError("Ollama not available")

    # Check cache first
    cache_key = _hash_prompt(cleaned, keywords, intents)
    if cache_key in _llm_response_cache:
        if debug:
            print(Fore.CYAN + "[CACHE HIT] Using cached LLM response" + Style.RESET_ALL)
        data = _llm_response_cache[cache_key]
    else:
        system_prompt = f'''You are a precise search query generator. Return ONLY valid JSON with this EXACT structure:

{{
  "search_queries": ["query1", "query2", "query3"]
}}

CRITICAL INSTRUCTIONS:
1. Respond ONLY with the pure JSON object, nothing else
2. DO NOT include markdown code blocks (no ```json ... ```)
3. ALL keys must be strings in double quotes
4. ALL values must be proper JSON types
5. search_queries must be an array of 3-5 strings
6. Keywords for context: {json.dumps([k["term"] for k in keywords])}
7. Intents for context: {json.dumps(intents)}
Respond ONLY with the JSON object:'''

        try:
            response = client.chat(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": f"Generate search queries for: {cleaned}"}
                ],
                options={
                    "temperature": 0.0,
                    "num_predict": 500,
                }
            )
            raw_json = response["message"]["content"].strip()

            # Clean possible markdown
            if raw_json.startswith("```"):
                raw_json = raw_json.split("```", 2)[1]
                if raw_json.lower().startswith("json"):
                    raw_json = raw_json[4:]

            data = json.loads(raw_json)
            
            # Cache the response
            _llm_response_cache[cache_key] = data
            
            # Limit cache size to prevent memory issues
            if len(_llm_response_cache) > 1000:
                # Remove oldest entries
                oldest_keys = list(_llm_response_cache.keys())[:100]
                for key in oldest_keys:
                    del _llm_response_cache[key]

        except Exception as e:
            if debug:
                print(Fore.RED + f"LLM failed: {e}" + Style.RESET_ALL)
            # Minimal fallback so it never crashes
            data = {
                "search_queries": [cleaned] if len(cleaned.split()) > 3 else [f"what is {cleaned}"]
            }

    # Generate goals using rule-based approach (similar to legacy)
    goals = []
    for sent in doc.sents:
        root = sent.root
        if root.pos_ == "VERB":
            objs = [c.text for c in root.children if c.dep_ in ("dobj", "attr")]
            mods = [c.text for c in root.children if c.dep_ in ("advmod", "amod")]
            goals.append({
                "action": root.lemma_,
                "object": " ".join(objs),
                "modifiers": mods
            })
    
    if not goals:  # fallback
        words = cleaned.lower().split()
        action_verbs = {"calculate", "compute", "search", "find", "write",
                        "explain", "analyze", "generate", "solve", "sing"}
        question_words = {"what", "how", "why", "when", "where", "who", "which"}
        
        # Check for question words first
        if any(word in words for word in question_words):
            goals.append({"action": "answer", "object": "query", "modifiers": []})
        else:
            for i, w in enumerate(words):
                if w in action_verbs:
                    goals.append({
                        "action": w,
                        "object": " ".join(words[i + 1:]) or "query",
                        "modifiers": []
                    })
                    break
            if not goals:
                goals.append({"action": "answer", "object": "query", "modifiers": []})

    # Final result (exact same format as your legacy version)
    result = {
        "intents": intents,
        "keywords": keywords or [{"term": w, "score": 1.0} for w in cleaned.split()[:8]],
        "goals": goals,
        "search_queries": data.get("search_queries", [cleaned])[:MAX_SEARCH_QUERIES],
        "message": f"**Intent:** {intents}\n"
                  f"**Keywords:** {', '.join(k['term'] for k in keywords)}\n"
                  f"**Goals:** {goals}"
    }

    if debug:
        print(Fore.MAGENTA + f"Total time: {(time.perf_counter()-start_time)*1000:.1f} ms" + Style.RESET_ALL)

    return result


# ———————————————————————— PRETTY PRINTER ————————————————————————
def _pretty_print(res: Dict[str, Any]):
    print(Fore.CYAN + "\n" + "="*60)
    print(Fore.MAGENTA + " PROMPT ANALYSIS RESULT ".center(60))
    print(Fore.CYAN + "="*60)

    print(Fore.YELLOW + "\nIntents:" + Style.RESET_ALL)
    for i in res["intents"]: print(Fore.GREEN + f"  → {i}")

    print(Fore.YELLOW + "\nKeywords:" + Style.RESET_ALL)
    for i, k in enumerate(res["keywords"], 1):
        print(Fore.WHITE + f"{i:2d}. {k['term']:<25} {k['score']:.4f}")

    print(Fore.YELLOW + "\nGoals:" + Style.RESET_ALL)
    for g in res["goals"]:
        print(Fore.GREEN + f" • {g['action']} → {g['object'] or '—'}")
        if g["modifiers"]:
            print(Fore.MAGENTA + f"    ↳ {', '.join(g['modifiers'])}")

    print(Fore.YELLOW + "\nSearch Queries:" + Style.RESET_ALL)
    for q in res["search_queries"]:
        print(Fore.CYAN + f"  • {q}")

    print(Fore.CYAN + "="*60 + "\n")


# ———————————————————————— CLI ————————————————————————
if __name__ == "__main__":
    import asyncio
    
    async def main():
        print(Fore.CYAN + "Hybrid Prompt Analyzer (spaCy + KeyBERT + Ollama) – type 'exit' to quit\n")
        while True:
            try:
                user_input = input(Fore.YELLOW + "Prompt > " + Style.RESET_ALL).strip()
                if user_input.lower() in {"exit", "quit"}:
                    break
                if not user_input:
                    continue

                result = await analyze_prompt(user_input, debug=True)
                _pretty_print(result)

            except KeyboardInterrupt:
                print("\n" + Fore.CYAN + "Bye!" + Style.RESET_ALL)
                break
            except Exception as e:
                print(Fore.RED + f"Unexpected error: {e}")
    
    asyncio.run(main())
