# clevels_ai/utils.py
import re
import unicodedata

def clean_text(text: str) -> str:
    if not text:
        return ""
    text = unicodedata.normalize("NFKD", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def detect_language(text: str) -> str:
    if not text:
        return "en"
    low = text.lower()
    ro_markers = ["ă","â","î","ș","ţ","ș","ț","româ","bucharest".lower()]
    # simple check for Romanian diacritics or keywords
    if any(m in low for m in ro_markers):
        return "ro"
    return "en"
