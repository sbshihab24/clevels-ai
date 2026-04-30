# clevels_ai/config.py
from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    OPENAI_CHAT_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    GOOGLE_MAPS_API_KEY: Optional[str] = None
    PARTNERS_XLSX_PATH: str = "data/documents/concierge/partners.xlsx"
    PARTNERS_CSV_PATH: str = "data/documents/concierge/partners.csv"
    VECTOR_INDEX_PATH: str = "data/vectors/vectors.faiss"
    VECTOR_META_PATH: str = "data/vectors/vectors.json"
    CACHE_TTL_DAYS: int = 7
    CONFIDENCE_THRESHOLD: float = 0.65
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "forbid"

    def ensure_paths(self):
        Path("data").mkdir(parents=True, exist_ok=True)
        Path("data/documents/concierge").mkdir(parents=True, exist_ok=True)
        Path("data/documents/legal").mkdir(parents=True, exist_ok=True)
        Path("data/documents/wellbeing").mkdir(parents=True, exist_ok=True)
        Path("data/vectors").mkdir(parents=True, exist_ok=True)

settings = Settings()
try:
    settings.ensure_paths()
except Exception:
    pass
