# prompt_analyzer.py
# ------------------------------------------------------------
# A lightweight, production-ready prompt analyzer.
# • spaCy (en_core_web_sm) for linguistic parsing (lazy-loaded)
# • YAKE for unsupervised keyword extraction (lazy-loaded)
# • Matcher patterns (from patterns.py) for intent detection
# • Structured goal extraction (action-object-modifiers)
# • Optional debug / timing utilities
# ------------------------------------------------------------

# NOTE: This is now the LEGACY analyzer. The new hybrid analyzer is in prompt_analyzer_llm.py
# This file is maintained for backward compatibility and as fallback option.

import torch
import time
from typing import List, Dict, Any
from colorama import Fore, Style, init
import threading

# ------------------------------------------------------------
# Optional: pre-initialize CUDA (non-blocking)
# ------------------------------------------------------------
try:
    torch.cuda.set_device(0)
except Exception:
    pass  # fallback to CPU if no GPU available

# ------------------------------------------------------------
# Colorama setup
# ------------------------------------------------------------
init(autoreset=True)

# ------------------------------------------------------------
# Try importing user-defined intent patterns
# ------------------------------------------------------------
try:
    from patterns import patterns  # dict: intent_name -> list[pattern]
except Exception:
    patterns = {}

# Define intents that require web search
SEARCH_REQUIRED_INTENTS = ["web_search", "question_answering", "explanation", "research", "translation"]

# ------------------------------------------------------------
# Lazy-loaded global references
# ------------------------------------------------------------
_nlp = None
_matcher = None
_kw_extractor = None


def get_spacy_pipeline():
    """Lazily initialize and cache spaCy pipeline + matcher."""
    global _nlp, _matcher
    if _nlp is None:
        import spacy
        from spacy.matcher import Matcher

        print(Fore.CYAN + "[INFO] Loading spaCy model..." + Style.RESET_ALL)
        _nlp = spacy.load("en_core_web_sm", disable=["ner"])
        _matcher = Matcher(_nlp.vocab)
        for intent_name, intent_patterns in patterns.items():
            _matcher.add(intent_name, intent_patterns)
        print(Fore.GREEN + "[OK] spaCy initialized." + Style.RESET_ALL)
    return _nlp, _matcher


def get_kw_extractor():
    """Lazily initialize and cache YAKE keyword extractor."""
    global _kw_extractor
    if _kw_extractor is None:
        from yake import KeywordExtractor
        print(Fore.CYAN + "[INFO] Initializing YAKE..." + Style.RESET_ALL)
        _kw_extractor = KeywordExtractor(lan="en", n=3, top=10, dedupLim=0.9)
        print(Fore.GREEN + "[OK] YAKE ready." + Style.RESET_ALL)
    return _kw_extractor


# Optional background warm-up (won't block startup)
def warm_up():
    try:
        get_spacy_pipeline()
        get_kw_extractor()
    except Exception as e:
        print(Fore.RED + f"[WARN] Warm-up failed: {e}" + Style.RESET_ALL)


threading.Thread(target=warm_up, daemon=True).start()


# ------------------------------------------------------------
# Helper utilities
# ------------------------------------------------------------
def _debug(msg: str, colour: str = Fore.CYAN) -> None:
    print(colour + f"[DEBUG] {msg}" + Style.RESET_ALL)


def _time_step(label: str, func, *args, **kwargs):
    start = time.perf_counter()
    result = func(*args, **kwargs)
    duration = (time.perf_counter() - start) * 1000
    print(Fore.YELLOW + f"⏱ {label}: {duration:.2f} ms" + Style.RESET_ALL)
    return result


# ------------------------------------------------------------
# Core analysis function
# ------------------------------------------------------------
def analyze_legacy(prompt: str, debug: bool = False) -> Dict[str, Any]:
    """Legacy spaCy/YAKE-based analyzer."""
    total_start = time.perf_counter()
    if debug:
        _debug(f"Analysing (legacy): '{prompt}'", Fore.MAGENTA)

    # Clean the prompt to remove conversation prefixes like "USER: " or "AI: "
    cleaned_prompt = prompt
    if prompt.startswith("USER: ") or prompt.startswith("AI: "):
        cleaned_prompt = prompt.split(": ", 1)[1] if ": " in prompt else prompt
    
    nlp, matcher = get_spacy_pipeline()
    kw_extractor = get_kw_extractor()

    # --------------------------------------------------------------
    # 1. spaCy parsing
    # --------------------------------------------------------------
    try:
        doc = _time_step("spaCy processing", nlp, cleaned_prompt.lower())
    except Exception as e:
        if debug:
            print(Fore.RED + f"[ERROR] spaCy failed: {e}" + Style.RESET_ALL)
        return {"error": str(e)}

    # --------------------------------------------------------------
    # 2. Intent detection
    # --------------------------------------------------------------
    matches = _time_step("Intent matching", matcher, doc)
    intents = list({nlp.vocab.strings[mid] for mid, _, _ in matches}) or ["No intent found"]

    # --------------------------------------------------------------
    # 3. Keyword extraction (only from the cleaned prompt)
    # --------------------------------------------------------------
    yake_kws = _time_step("YAKE extraction", kw_extractor.extract_keywords, cleaned_prompt)
    noun_chunks = [chunk.lemma_ for chunk in doc.noun_chunks if not chunk.root.is_stop]
    seen = set()
    keywords = []
    for term in noun_chunks + [kw[0] for kw in yake_kws]:
        if term not in seen:
            seen.add(term)
            score = next((s for t, s in yake_kws if t == term), 1.0)
            keywords.append({"term": term, "score": score})

    # --------------------------------------------------------------
    # 4. Goal extraction
    # --------------------------------------------------------------
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
        words = cleaned_prompt.lower().split()
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

    # --------------------------------------------------------------
    # 5. Generate search queries (based only on the cleaned prompt)
    # --------------------------------------------------------------
    search_queries = []
    # Generate more effective search queries
    keyword_terms = [k["term"] for k in keywords[:5]]
    
    # For question answering, create more targeted queries
    if "question_answering" in intents:
        # Create specific queries focused on the key information needed
        if keyword_terms:
            # Try combinations that are more likely to find specific answers
            search_queries.append(" ".join(keyword_terms[:3]))  # e.g., "chief advisor bangladesh government"
            search_queries.append(f"who is {' '.join(keyword_terms[:2])}")  # e.g., "who is chief advisor bangladesh"
            search_queries.append(f"{keyword_terms[0]} {keyword_terms[2]}")  # e.g., "July Revolution chief advisor"
            
        # Add the original question without the "Tell me" part for better search results
        if cleaned_prompt.lower().startswith("tell me"):
            search_queries.append(cleaned_prompt[8:])  # Remove "Tell me "
        else:
            search_queries.append(cleaned_prompt)
    elif "translation" in intents:
        # For translation tasks, focus on language pairs and context
        if keyword_terms:
            search_queries.append(" ".join(keyword_terms[:3]))
            search_queries.append(f"translate {' '.join(keyword_terms[:3])}")
            search_queries.append(f"meaning {' '.join(keyword_terms[:2])}")
            
        # Add the original prompt
        search_queries.append(cleaned_prompt)
    else:
        # Add the original prompt as the first query
        search_queries.append(cleaned_prompt)
        
        # Add keyword combinations
        if keyword_terms:
            # Add a simple combination of top keywords
            search_queries.append(" ".join(keyword_terms[:3]))
            
            # Add individual important keywords
            for term in keyword_terms[:3]:
                if term not in search_queries:
                    search_queries.append(term)
        
        # Add intent-based queries for non-question intents
        for intent in intents[:2]:
            if intent not in ["question_answering", "translation"] and keyword_terms:  # Skip for question answering and translation
                intent_query = f"{intent} {' '.join(keyword_terms[:3])}"
                if len(intent_query) < 100:  # Only add if not too long
                    search_queries.append(intent_query)
    
    # Deduplicate while preserving order and reasonable length
    seen_queries = set()
    unique_queries = []
    for q in search_queries:
        # Check if query is valid (not empty, not too long)
        if q and len(q.strip()) > 0 and len(q) < 150:
            clean_q = q.strip()
            if clean_q not in seen_queries:
                seen_queries.add(clean_q)
                unique_queries.append(clean_q)
    search_queries = unique_queries[:5]

    total_time = (time.perf_counter() - total_start) * 1000
    if debug:
        print(Fore.MAGENTA + f"Total analysis: {total_time:.2f} ms" + Style.RESET_ALL)

    return {
        "intents": intents,
        "keywords": sorted(keywords, key=lambda x: x["score"]),
        "goals": goals,
        "search_queries": search_queries,
        "message": f"**Intent:** {intents}\n"
                   f"**Keywords:** {', '.join([k['term'] for k in sorted(keywords, key=lambda x: x['score'], reverse=True)])}\n"
                   f"**Goals:** {', '.join(map(str, goals)) if goals else 'None'}"
    }


# ------------------------------------------------------------
# Pretty printer for CLI testing
# ------------------------------------------------------------
def _pretty_print(result: Dict[str, Any]) -> None:
    print(Fore.CYAN + "\n" + "=" * 60)
    print(Fore.MAGENTA + " INTENT ANALYSIS RESULT ".center(60))
    print(Fore.CYAN + "=" * 60 + Style.RESET_ALL)

    print(Fore.YELLOW + "\nIntents:" + Style.RESET_ALL)
    for i in result.get("intents", []):
        print(Fore.GREEN + f"  {i}" + Style.RESET_ALL)

    print(Fore.YELLOW + "\nKeywords:" + Style.RESET_ALL)
    kws = result.get("keywords", [])
    if not kws:
        print(Fore.RED + "  None" + Style.RESET_ALL)
    else:
        print(Fore.CYAN + f"{'#':<3}{'Term':<30}{'Score':<8}" + Style.RESET_ALL)
        print(Fore.CYAN + "-" * 42 + Style.RESET_ALL)
        for idx, kw in enumerate(kws, 1):
            print(Fore.WHITE + f"{idx:<3}{kw['term']:<30}{kw['score']:<8.4f}" + Style.RESET_ALL)

    print(Fore.YELLOW + "\nGoals:" + Style.RESET_ALL)
    for i, g in enumerate(result.get("goals", []), 1):
        print(Fore.WHITE + f" {i}. Action: " + Fore.GREEN + str(g['action']))
        print(Fore.WHITE + f"    Object : " + Fore.CYAN + (g['object'] or '—'))
        print(Fore.WHITE + f"    Mods   : " + Fore.MAGENTA + (", ".join(g['modifiers']) if g['modifiers'] else "—"))
        print()

    print(Fore.CYAN + "=" * 60 + "\n" + Style.RESET_ALL)


# ------------------------------------------------------------
# Public API function
# ------------------------------------------------------------
def analyze_prompt(prompt: str, debug: bool = False) -> Dict[str, Any]:
    """Public API function - now uses hybrid analyzer with fallback to legacy."""
    try:
        # Try to import and use the new hybrid analyzer
        from prompt_analyzer_llm import analyze_prompt as hybrid_analyze_prompt
        import asyncio
        
        # Check if we're already in an async context
        try:
            # Try to get the running event loop
            loop = asyncio.get_running_loop()
            # If we're in an async context, we can't use run_until_complete directly
            # Instead, we'll create a separate thread to run the async function
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, hybrid_analyze_prompt(prompt, debug))
                return future.result()
        except RuntimeError:
            # No event loop running, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(hybrid_analyze_prompt(prompt, debug))
    except Exception as e:
        # Fallback to legacy analyzer
        if debug:
            print(Fore.RED + f"[WARN] Hybrid analyzer failed, falling back to legacy: {e}" + Style.RESET_ALL)
        return analyze_legacy(prompt, debug)


async def analyze_prompt_async(prompt: str, debug: bool = False) -> Dict[str, Any]:
    """Async version of analyze_prompt for use in async contexts."""
    try:
        # Try to import and use the new hybrid analyzer
        from prompt_analyzer_llm import analyze_prompt as hybrid_analyze_prompt
        # Since we're already in an async context, we can directly await the async function
        return await hybrid_analyze_prompt(prompt, debug)
    except Exception as e:
        # Fallback to legacy analyzer
        if debug:
            print(Fore.RED + f"[WARN] Hybrid analyzer failed, falling back to legacy: {e}" + Style.RESET_ALL)
        return analyze_legacy(prompt, debug)

# ------------------------------------------------------------
# CLI entry-point
# ------------------------------------------------------------
if __name__ == "__main__":
    print(Fore.CYAN + "Prompt Analyzer – type 'exit' to quit.\n" + Style.RESET_ALL)
    while True:
        user_input = input(Fore.YELLOW + "Prompt > " + Style.RESET_ALL).strip()
        if user_input.lower() == "exit":
            print(Fore.CYAN + "Bye!" + Style.RESET_ALL)
            break
        res = analyze_prompt(user_input, debug=True)
        _pretty_print(res)