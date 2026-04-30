# clevels_ai/parsers/parse_pdf.py
import pdfplumber
from pathlib import Path

def extract_text_from_pdf(path: str) -> str:
    path = Path(path)
    out = []
    with pdfplumber.open(str(path)) as pdf:
        for p in pdf.pages:
            txt = p.extract_text()
            if txt:
                out.append(txt)
    return "\n".join(out)
