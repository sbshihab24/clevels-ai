# clevels_ai/ingestion/process_documents.py
from ..config import settings
from ..embeddings import embed_texts
from ..vectorstore import upsert
from ..parsers.parse_pdf import extract_text_from_pdf
from ..parsers.parse_docx import extract_text_from_docx
from pathlib import Path
import os

DOC_ROOT = Path("data/documents")

def chunk_text(text: str, size: int = 1500):
    text = text.strip()
    return [text[i:i+size] for i in range(0, len(text), size)]

def ingest_namespace(namespace: str):
    folder = DOC_ROOT / namespace
    if not folder.exists():
        return
    docs = []
    for p in folder.iterdir():
        if p.suffix.lower() in [".pdf"]:
            txt = extract_text_from_pdf(str(p))
        elif p.suffix.lower() in [".docx"]:
            txt = extract_text_from_docx(str(p))
        elif p.suffix.lower() in [".txt",".md"]:
            txt = p.read_text(encoding="utf-8")
        else:
            continue
        chunks = chunk_text(txt)
        for i, c in enumerate(chunks):
            docs.append({"id": f"{p.stem}-{i}", "text": c, "source": str(p)})
    if not docs:
        return
    texts = [d["text"] for d in docs]
    embs = embed_texts(texts)
    upsert(namespace, docs, embs)

def ingest_all():
    for ns in ["concierge","legal","wellbeing"]:
        ingest_namespace(ns)

if __name__ == "__main__":
    ingest_all()
