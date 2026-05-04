import spacy
from collections import Counter
import re

# Load Chinese spaCy model
nlp = spacy.load("zh_core_web_sm")

# Define the entities we actually care about for telecom/SEO analysis
TOPIC_MAPPING = {
    "ORG": "電信與組織 (ORG)",
    "GPE": "國家與城市 (GPE)",
    "PERSON": "人物 (PERSON)",
    "MONEY": "價格與金錢 (MONEY)",
    "PRODUCT": "產品方案 (PRODUCT)",
    "DATE": "時間與日期 (DATE)",
    "CARDINAL": "數據與數字 (CARDINAL)"
}

def extract_entities(text: str):
    """Extract named entities from text, return list of (text, readable_label) tuples"""
    doc = nlp(text[:5000])  # Limit to avoid memory issues
    entities = []
    
    for ent in doc.ents:
        term = ent.text.strip()
        
        # --- THE BOUNCER: Filter out the junk ---
        
        # 1. Ignore pure numbers (blocks "10", "500") 
        if term.isnumeric():
            continue
            
        # 2. Ignore single characters (blocks "i", "2", "的")
        if len(term) < 2:
            continue
            
        # 3. Ignore HTML code leftovers (blocks "th>", "<br")
        if "<" in term or ">" in term:
            continue

        # 4. NEW: Block Mojibake / Encoding Garbage (¡, ¼, ¶, æ, å, ç, etc.)
        # This regex looks for extended Latin characters that usually indicate corrupted Chinese
        if re.search(r'[\u0080-\u00FF]', term):
            continue

        # 5. NEW: Block terms with stray symbols, code snippets, or weird punctuation
        # This blocks things like $container, ~$3, or terms with pipes | and brackets
        if re.search(r'[\$\|\~\{\}\[\]\(\)]', term) or "container" in term:
            continue
            
        # ----------------------------------------

        # Only keep useful entities
        if ent.label_ in TOPIC_MAPPING:
            readable_label = TOPIC_MAPPING[ent.label_]
            entities.append((term, readable_label))             
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