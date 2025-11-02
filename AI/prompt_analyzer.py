# prompt_analyzer.py
# ------------------------------------------------------------
# A lightweight, production-ready prompt analyzer.
# • spaCy (en_core_web_sm) for linguistic parsing
# • YAKE for unsupervised keyword extraction
# • Matcher patterns (from patterns.py) for intent detection
# • Structured goal extraction (action-object-modifiers)
# • Optional debug / timing utilities
# ------------------------------------------------------------

import time
from typing import List, Dict, Any

import spacy
from spacy.matcher import Matcher
from yake import KeywordExtractor
from colorama import Fore, Style, init

# ------------------------------------------------------------------
# Optional: import user-defined intent patterns (patterns.py)
# ------------------------------------------------------------------
try:
    from patterns import patterns  # dict: intent_name -> list[pattern]
except Exception:  # pragma: no cover
    patterns = {}

# ------------------------------------------------------------------
# Global initialisation (done once at import time)
# ------------------------------------------------------------------
init(autoreset=True)                                 # colour output
nlp = spacy.load("en_core_web_sm", disable=["ner"])  # fast, no NER needed
matcher = Matcher(nlp.vocab)
for intent_name, intent_patterns in patterns.items():
    matcher.add(intent_name, intent_patterns)

kw_extractor = KeywordExtractor(lan="en", n=3, top=10, dedupLim=0.9)


# ------------------------------------------------------------------
# Helper utilities (debug / timing)
# ------------------------------------------------------------------
def _debug(msg: str, colour: str = Fore.CYAN) -> None:
    print(colour + f"[DEBUG] {msg}" + Style.RESET_ALL)


def _time_step(label: str, func, *args, **kwargs):
    start = time.perf_counter()
    result = func(*args, **kwargs)
    duration = (time.perf_counter() - start) * 1000
    print(Fore.YELLOW + f"⏱ {label}: {duration:.2f} ms" + Style.RESET_ALL)
    return result


# ------------------------------------------------------------------
# Core analysis function
# ------------------------------------------------------------------
def analyze_prompt(prompt: str, debug: bool = False) -> Dict[str, Any]:
    """
    Analyse a user prompt and return a structured JSON-compatible dict.

    Returns
    -------
    {
        "intents":   List[str] | "No intent found",
        "keywords":  List[Dict["term": str, "score": float]],
        "goals":     List[Dict["action": str, "object": str, "modifiers": List[str]]]
    }
    """
    total_start = time.perf_counter()
    if debug:
        _debug(f"Analysing: '{prompt}'", Fore.MAGENTA)

    # --------------------------------------------------------------
    # 1. spaCy parsing (fallback-safe)
    # --------------------------------------------------------------
    doc = None
    try:
        doc = _time_step("spaCy processing", nlp, prompt.lower())
    except Exception as e:  # pragma: no cover
        if debug:
            print(Fore.RED + f"[ERROR] spaCy failed: {e}" + Style.RESET_ALL)

    # --------------------------------------------------------------
    # 2. Intent detection via Matcher
    # --------------------------------------------------------------
    intents: List[str] = []
    if doc:
        matches = _time_step("Intent matching", matcher, doc)
        intents = list({nlp.vocab.strings[mid] for mid, _, _ in matches})

    # --------------------------------------------------------------
    # 3. Keyword extraction (YAKE + noun chunks + entities)
    # --------------------------------------------------------------
    yake_kws = _time_step("YAKE extraction", kw_extractor.extract_keywords, prompt)

    # noun chunks (lemmatised, stop-word free)
    noun_chunks: List[str] = []
    if doc:
        noun_chunks = [
            chunk.lemma_ for chunk in doc.noun_chunks
            if not chunk.root.is_stop
        ]

    # merge everything, keep best YAKE score
    seen = set()
    keywords: List[Dict[str, Any]] = []
    for term in noun_chunks + [kw[0] for kw in yake_kws]:
        if term not in seen:
            seen.add(term)
            score = next((s for t, s in yake_kws if t == term), 1.0)
            keywords.append({"term": term, "score": score})

    # --------------------------------------------------------------
    # 4. Goal extraction (root verb + direct object + modifiers)
    # --------------------------------------------------------------
    goals: List[Dict[str, Any]] = []
    if doc:
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
    # Fallback: simple keyword-based goal if parsing failed
    if not goals:
        words = prompt.lower().split()
        action_verbs = {
            "calculate", "compute", "search", "find", "write",
            "explain", "analyze", "generate", "solve", "sing"
        }
        for i, w in enumerate(words):
            if w in action_verbs:
                goals.append({
                    "action": w,
                    "object": " ".join(words[i + 1 :]) or "query",
                    "modifiers": []
                })
                break
        else:
            goals.append({
                "action": "answer",
                "object": "query",
                "modifiers": []
            })

    # --------------------------------------------------------------
    # 5. Finalise result
    # --------------------------------------------------------------
    total_time = (time.perf_counter() - total_start) * 1000
    if debug:
        print(Fore.MAGENTA + f"Total analysis: {total_time:.2f} ms" + Style.RESET_ALL)

    return {
        "intents": intents or "No intent found",
        "keywords": sorted(keywords, key=lambda x: x["score"]),
        "goals": goals
    }


# ------------------------------------------------------------------
# Pretty printer (optional, for CLI testing)
# ------------------------------------------------------------------
def _pretty_print(result: Dict[str, Any]) -> None:
    print(Fore.CYAN + "\n" + "=" * 60)
    print(Fore.MAGENTA + " INTENT ANALYSIS RESULT ".center(60))
    print(Fore.CYAN + "=" * 60 + Style.RESET_ALL)

    # Intents
    print(Fore.YELLOW + "\nIntents:" + Style.RESET_ALL)
    if result["intents"] == "No intent found":
        print(Fore.RED + "  No intents detected." + Style.RESET_ALL)
    else:
        for i in result["intents"]:
            print(Fore.GREEN + f"  {i}" + Style.RESET_ALL)

    # Keywords
    print(Fore.YELLOW + "\nKeywords:" + Style.RESET_ALL)
    if not result["keywords"]:
        print(Fore.RED + "  None" + Style.RESET_ALL)
    else:
        print(Fore.CYAN + f"{'#':<3}{'Term':<30}{'Score':<8}" + Style.RESET_ALL)
        print(Fore.CYAN + "-" * 42 + Style.RESET_ALL)
        for idx, kw in enumerate(result["keywords"], 1):
            print(Fore.WHITE + f"{idx:<3}{kw['term']:<30}{kw['score']:<8.4f}" + Style.RESET_ALL)

    # Goals
    print(Fore.YELLOW + "\nGoals:" + Style.RESET_ALL)
    for i, g in enumerate(result["goals"], 1):
        print(Fore.WHITE + f" {i}. Action: " + Fore.GREEN + g["action"])
        print(Fore.WHITE + f"    Object : " + Fore.CYAN + (g["object"] or "—"))
        print(Fore.WHITE + f"    Mods   : " + Fore.MAGENTA + (", ".join(g["modifiers"]) if g["modifiers"] else "—"))
        print()

    print(Fore.CYAN + "=" * 60 + "\n" + Style.RESET_ALL)


# ------------------------------------------------------------------
# CLI entry-point (for local testing)
# ------------------------------------------------------------------
if __name__ == "__main__":
    print(Fore.CYAN + "Prompt Analyzer – type 'exit' to quit.\n" + Style.RESET_ALL)
    while True:
        user_input = input(Fore.YELLOW + "Prompt > " + Style.RESET_ALL).strip()
        if user_input.lower() == "exit":
            print(Fore.CYAN + "Bye!" + Style.RESET_ALL)
            break
        res = analyze_prompt(user_input, debug=True)
        _pretty_print(res)
