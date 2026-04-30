# clevels_ai/parsers/parse_xlsx.py
import pandas as pd
from pathlib import Path

def extract_text_from_xlsx(path: str) -> str:
    df = pd.read_excel(path)
    return df.to_csv(index=False)
