import spacy
from collections import Counter
from spacy.matcher import Matcher
from yake import KeywordExtractor
from patterns import patterns  # Import from patterns.py

# Initialize YAKE (lightweight, ~1MB)
kw_extractor = KeywordExtractor(lan="en", n=3, top=10, dedupLim=0.9)

def analyze_prompt(prompt):
    # Lazy-load spaCy to avoid memory issues
    nlp = None
    matcher = None
    doc = None
    try:
        nlp = spacy.load("en_core_web_sm", disable=["ner"])  # Enable parser for noun_chunks, disable ner
        matcher = Matcher(nlp.vocab)
        # Load patterns from patterns.py
        for intent, pats in patterns.items():
            matcher.add(intent, pats)
        doc = nlp(prompt.lower())
    except Exception as e:
        print(f"Failed to load spaCy: {e}. Falling back to keyword-based analysis.")

    # Process prompt
    if doc:
        noun_chunks = [chunk.lemma_ for chunk in doc.noun_chunks if not chunk.root.is_stop]
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        pattern_matches = matcher(doc)
        intents = list({nlp.vocab.strings[match_id] for match_id, _, _ in pattern_matches})
    else:
        noun_chunks = []
        entities = []
        intents = []

    # Keywords: Noun chunks + entities + YAKE
    yake_keywords = kw_extractor.extract_keywords(prompt)
    keywords = list(set(noun_chunks + [kw[0] for kw in yake_keywords] + [ent[0] for ent in entities]))
    keywords = [{"term": kw, "score": next((s[1] for s in yake_keywords if s[0] == kw), 1.0)} for kw in keywords]

    # Goals: Use spaCy if available, else simple parsing
    goals = []
    if doc:
        for sent in doc.sents:
            root = sent.root
            if root.pos_ == "VERB":
                objs = [child.text for child in root.children if child.dep_ in ["dobj", "attr"]]
                mods = [child.text for child in root.children if child.dep_ in ["advmod", "amod"]]
                goals.append({"action": root.lemma_, "object": " ".join(objs), "modifiers": mods})
    if not goals:
        # Simple fallback: Extract verb + object from prompt
        prompt_lower = prompt.lower()
        words = prompt_lower.split()
        for i, word in enumerate(words):
            if word in {"calculate", "search", "write", "explain", "analyze", "generate", "find", "solve", "sing"}:  # Added "sing" for creative prompts
                action = word
                obj = " ".join(words[i+1:]) if i+1 < len(words) else "query"
                goals.append({"action": action, "object": obj, "modifiers": []})
                break
        else:
            goals = [{"action": "answer", "object": "query", "modifiers": []}]

    return {"intents": intents or ["question_answering"], "keywords": keywords, "goals": goals}

if __name__ == "__main__":
    prompt = None
    while(prompt != "exit"):
        print("Enter a prompt:", end=" ")
        prompt = input()
        result = analyze_prompt(prompt)
        print(result)
