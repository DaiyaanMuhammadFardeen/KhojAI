import re
from typing import List, Tuple, Dict
from rank_bm25 import BM25Okapi

# Initialize NLTK with proper error handling
NLTK_READY = False
wordnet = None
word_tokenize = None
stopwords = None

try:
    import nltk

    # Download required data first
    print("📦 Checking NLTK data...")
    nltk.download('wordnet', quiet=True)
    nltk.download('omw-1.4', quiet=True)
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    try:
        nltk.download('punkt_tab', quiet=True)  # For newer NLTK versions
    except:
        pass

    # Now import after downloads
    from nltk.corpus import wordnet
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords

    # Test if it works
    wordnet.synsets('test')
    word_tokenize('test')
    stopwords.words('english')

    NLTK_READY = True
    print("✅ NLTK initialized successfully")

except Exception as e:
    print(f"⚠️  NLTK not available: {e}")
    print("   Falling back to basic tokenization")
    NLTK_READY = False

# Optional: Load spaCy only if available
SPACY_AVAILABLE = False
nlp = None
try:
    import spacy

    nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
    print("✅ spaCy loaded successfully")
except (ImportError, OSError):
    print("⚠️  spaCy not available")


def expand_keywords_wordnet(keywords: List[str], max_synonyms: int = 2) -> List[str]:
    """
    Expand keywords using WordNet synonyms.
    Falls back to original keywords if NLTK unavailable.
    """
    if not NLTK_READY or wordnet is None:
        return keywords

    expanded = set(kw.lower() for kw in keywords)

    try:
        for keyword in keywords:
            synonym_count = 0
            for syn in wordnet.synsets(keyword.lower()):
                if synonym_count >= max_synonyms:
                    break

                for lemma in syn.lemmas():
                    lemma_name = lemma.name().replace('_', ' ').lower()

                    if lemma_name != keyword.lower() and len(lemma_name.split()) <= 2:
                        expanded.add(lemma_name)
                        synonym_count += 1

                        if synonym_count >= max_synonyms:
                            break
    except Exception as e:
        print(f"⚠️  WordNet expansion failed: {e}")
        return keywords

    expanded_list = list(expanded)
    if len(expanded_list) > len(keywords):
        print(f"📝 Expanded {len(keywords)} keywords to {len(expanded_list)} terms")
    return expanded_list


def extract_entities_from_keywords(keywords: List[str]) -> List[str]:
    """
    Extract named entities and key terms from keywords using spaCy NER.
    Falls back to original keywords if spaCy unavailable.
    """
    if not SPACY_AVAILABLE or nlp is None:
        return keywords

    try:
        text = " ".join(keywords)
        doc = nlp(text)

        entities = [ent.text.lower() for ent in doc.ents]
        key_terms = [token.lemma_.lower() for token in doc
                     if token.pos_ in ['NOUN', 'PROPN', 'VERB']
                     and not token.is_stop
                     and len(token.text) > 2]

        all_terms = list(set(entities + key_terms + [kw.lower() for kw in keywords]))
        print(f"🔍 Extracted {len(all_terms)} key terms using NER")
        return all_terms
    except Exception as e:
        print(f"⚠️  NER extraction failed: {e}")
        return keywords


def split_sentences(content: str) -> List[str]:
    """Split content into sentences."""
    content = re.sub(r'<[^>]*>', ' ', content)
    content = re.sub(r'\s+', ' ', content).strip()

    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s', content)
    return [s.strip() for s in sentences if len(s.strip()) >= 5]


def tokenize_text(text: str, remove_stopwords_flag: bool = True) -> List[str]:
    """
    Tokenize text and optionally remove stopwords.
    Falls back to simple split if NLTK unavailable.
    """
    if not NLTK_READY or word_tokenize is None:
        # Fallback: simple tokenization
        tokens = re.findall(r'\b\w+\b', text.lower())
        if remove_stopwords_flag:
            # Basic stopwords
            basic_stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                               'of', 'with', 'is', 'are', 'was', 'were', 'be', 'been', 'being'}
            tokens = [t for t in tokens if t not in basic_stopwords]
        return tokens

    try:
        tokens = word_tokenize(text.lower())

        if remove_stopwords_flag:
            stop_words = set(stopwords.words('english'))
            tokens = [t for t in tokens if t.isalnum() and t not in stop_words]
        else:
            tokens = [t for t in tokens if t.isalnum()]

        return tokens
    except Exception as e:
        print(f"⚠️  Tokenization failed, using fallback: {e}")
        tokens = re.findall(r'\b\w+\b', text.lower())
        return tokens


def calculate_entity_overlap(sentence: str, keywords: List[str]) -> int:
    """
    Calculate overlap between sentence entities and keyword entities.
    Returns 0 if spaCy unavailable.
    """
    if not SPACY_AVAILABLE or nlp is None:
        return 0

    try:
        sent_doc = nlp(sentence)
        keyword_doc = nlp(" ".join(keywords))

        sent_entities = {ent.text.lower() for ent in sent_doc.ents}
        keyword_entities = {ent.text.lower() for ent in keyword_doc.ents}

        return len(sent_entities.intersection(keyword_entities))
    except Exception as e:
        return 0


def extract_relevant_information(
        content: str,
        keywords: List[str],
        top_n: int = 10,
        use_expansion: bool = True,
        use_ner: bool = True,
        expansion_weight: float = 0.5,
        bm25_weight: float = 1.0,
        keyword_weight: float = 2.0,
        entity_weight: float = 1.5
) -> List[Tuple[str, float, Dict]]:
    """
    Extract most relevant sentences using BM25, WordNet expansion, and optional NER.

    Args:
        content: Full text content
        keywords: Original search keywords
        top_n: Number of top sentences to return
        use_expansion: Whether to use WordNet keyword expansion (requires NLTK)
        use_ner: Whether to use Named Entity Recognition (requires spaCy)
        expansion_weight: Weight for expanded keywords (0-1)
        bm25_weight: Weight for BM25 score
        keyword_weight: Weight for original keyword matches
        entity_weight: Weight for entity matches

    Returns:
        List of (sentence, score, metadata) tuples
    """
    # Split content into sentences
    sentences = split_sentences(content)
    print(f"📄 Split content into {len(sentences)} sentences")

    if not sentences:
        return []

    # Prepare keywords
    original_keywords_set = set(kw.lower() for kw in keywords)
    expanded_keywords = keywords.copy()

    # Expand keywords using WordNet
    if use_expansion and NLTK_READY:
        expanded_keywords = expand_keywords_wordnet(keywords, max_synonyms=2)
    elif use_expansion and not NLTK_READY:
        print("⚠️  Keyword expansion skipped (NLTK not available)")

    # Extract entities from keywords using NER
    key_terms = keywords
    if use_ner and SPACY_AVAILABLE:
        key_terms = extract_entities_from_keywords(keywords)
    elif use_ner and not SPACY_AVAILABLE:
        print("⚠️  NER skipped (spaCy not available)")

    # Tokenize sentences for BM25
    tokenized_sentences = [tokenize_text(sent) for sent in sentences]

    # Combine all search terms
    all_search_terms = list(set(
        [kw.lower() for kw in keywords] +
        [kw.lower() for kw in expanded_keywords] +
        [term.lower() for term in key_terms]
    ))
    tokenized_query = tokenize_text(" ".join(all_search_terms))

    print(f"🔎 Searching with {len(tokenized_query)} query terms")

    # Calculate BM25 scores
    try:
        bm25 = BM25Okapi(tokenized_sentences)
        bm25_scores = bm25.get_scores(tokenized_query)
    except Exception as e:
        print(f"⚠️  BM25 scoring failed: {e}")
        return []

    # Calculate combined scores
    results = []
    for i, (sentence, bm25_score) in enumerate(zip(sentences, bm25_scores)):
        sentence_lower = sentence.lower()

        # Count original keyword matches
        original_matches = sum(1 for kw in original_keywords_set if kw in sentence_lower)

        # Count expanded keyword matches
        expanded_matches = sum(
            1 for kw in expanded_keywords
            if kw.lower() not in original_keywords_set and kw.lower() in sentence_lower
        )

        # Calculate entity overlap
        entity_overlap = 0
        if use_ner and SPACY_AVAILABLE:
            entity_overlap = calculate_entity_overlap(sentence, keywords)

        # Combine scores
        final_score = (
                bm25_score * bm25_weight +
                original_matches * keyword_weight +
                expanded_matches * expansion_weight +
                entity_overlap * entity_weight
        )

        metadata = {
            'bm25_score': round(bm25_score, 3),
            'original_matches': original_matches,
            'expanded_matches': expanded_matches,
            'entity_overlap': entity_overlap,
            'sentence_length': len(sentence.split())
        }

        results.append((sentence, final_score, metadata))

    # Sort and filter
    results.sort(key=lambda x: x[1], reverse=True)
    filtered_results = [(s, score, meta) for s, score, meta in results if score > 0]

    print(f"✅ Found {len(filtered_results)} relevant sentences (returning top {top_n})")

    return filtered_results[:top_n]
# Example usage
if __name__ == "__main__":
    content = """
    Apple Inc. released the iPhone 15 in September 2023. The device features an advanced camera system.
    The new model has improved battery life compared to previous versions.
    Tim Cook, CEO of Apple, announced the product at a special event in Cupertino, California.
    The smartphone includes the latest A17 Pro chip for enhanced performance.
    Microsoft is also competing in the mobile market with Surface devices.
    The iPhone 15 Pro Max offers the best camera capabilities in the lineup.
    Android phones from Samsung continue to be popular alternatives.
    The new iPhone supports USB-C charging, replacing the Lightning port.
    Photography enthusiasts praise the improved low-light performance of the camera.
    Apple's ecosystem integration makes the iPhone attractive to existing Mac users.
    """

    keywords = ["iPhone 15", "camera", "features"]

    print("\n" + "=" * 80)
    print("TESTING RELEVANCE EXTRACTION")
    print("=" * 80)
    print(f"NLTK Ready: {NLTK_READY}")
    print(f"spaCy Available: {SPACY_AVAILABLE}")
    print("=" * 80)

    # Try full-featured version
    print("\n📊 FULL-FEATURED VERSION")
    print("-" * 80)

    results = extract_relevant_information(
        content,
        keywords,
        top_n=5,
        use_expansion=True,
        use_ner=True
    )

    for i, (sentence, score, metadata) in enumerate(results, 1):
        print(f"\n{i}. [Score: {score:.2f}]")
        print(f"   {sentence[:100]}...")
        print(f"   📊 BM25={metadata['bm25_score']}, "
              f"Keywords={metadata['original_matches']}, "
              f"Expanded={metadata['expanded_matches']}, "
              f"Entities={metadata['entity_overlap']}")