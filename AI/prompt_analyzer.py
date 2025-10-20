import spacy
from collections import Counter

nlp = spacy.load("en_core_web_sm")  # Load once at module level

def analyze_prompt(prompt):
    doc = nlp(prompt.lower())
    
    # Keywords: Top nouns/verbs via frequency, excluding stops
    keywords = [token.lemma_ for token in doc if token.pos_ in ["NOUN", "VERB"] and not token.is_stop]
    keywords = list(Counter(keywords).keys())[:5]  # Top 5 unique
    
    # Intent: Rule-based (e.g., check for computation words)
    intent = "knowledge_query"
    if any(word in keywords for word in ["calculate", "compute", "reason"]):
        intent = "computation"
    elif any(word in keywords for word in ["search", "find", "web"]):
        intent = "web_search"
    
    # Goal: Extract root verb + direct object
    goal = next((f"{token.lemma_} {child.text}" for token in doc if token.dep_ == "ROOT" and token.pos_ == "VERB" for child in token.children if child.dep_ == "dobj"), "answer query")
    
    return {"intent": intent, "keywords": keywords, "goal": goal}

# Example usage
print("Enter a prompt:", end=" ")
prompt = input()
result = analyze_prompt(prompt)
print(result)
