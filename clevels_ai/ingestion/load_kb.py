# clevels_ai/ingestion/load_kb.py
from .process_partners import convert_partners_xlsx_to_csv
from .process_documents import ingest_all
from ..logger import logger

def build_kb_all():
    convert_partners_xlsx_to_csv()
    ingest_all()
    logger.info("KB build complete")

if __name__ == "__main__":
    build_kb_all()
