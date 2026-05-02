import spacy
from collections import Counter

# Load Chinese spaCy model
nlp = spacy.load("zh_core_web_sm")

def extract_entities(text: str):
    """Extract named entities from text, return list of (text, label) tuples"""
    doc = nlp(text[:5000])  # Limit to avoid memory issues
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    return entities


def count_entities(entities: list):
    """Return total count of entities"""
    return len(entities)


def cluster_entities_by_label(entities: list):
    """Group entities by their label type (ORG, PERSON, GPE, etc.)"""
    label_counts = Counter(label for _, label in entities)
    return dict(label_counts)


def get_top_entities(entities: list, top_n: int = 10):
    """Return the most frequent entity texts"""
    text_counts = Counter(text for text, _ in entities)
    return text_counts.most_common(top_n)