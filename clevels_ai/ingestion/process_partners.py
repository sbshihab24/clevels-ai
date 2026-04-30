# clevels_ai/ingestion/process_partners.py
import pandas as pd
from ..config import settings
from ..logger import logger
from pathlib import Path

def convert_partners_xlsx_to_csv():
    xlsx = Path(settings.PARTNERS_XLSX_PATH)
    csv = Path(settings.PARTNERS_CSV_PATH)
    if not xlsx.exists():
        logger.warning("Partners xlsx not found at %s", xlsx)
        return
    df = pd.read_excel(xlsx)
    # minimal cleanup: ensure lowercase columns
    df.columns = [c.strip() for c in df.columns]
    df.to_csv(csv, index=False, encoding="utf-8")
    logger.info("Saved partners CSV at %s", csv)

if __name__ == "__main__":
    convert_partners_xlsx_to_csv()
