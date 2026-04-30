# clevels_ai/parsers/parse_docx.py
from docx import Document
from pathlib import Path

def extract_text_from_docx(path: str) -> str:
    doc = Document(path)
    paragraphs = [p.text for p in doc.paragraphs if p.text]
    return "\n".join(paragraphs)
