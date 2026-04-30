# clevels_ai/db.py
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings
from .logger import logger
import os

Base = declarative_base()
engine = create_engine(settings.DB_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Partner(Base):
    __tablename__ = "partners"
    id = Column(Integer, primary_key=True, index=True)
    partner_id = Column(String, unique=True, index=True)
    name = Column(String)
    address = Column(String)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    partner_status = Column(Boolean, default=False)
    curated_category = Column(String, nullable=True)
    quality_tags = Column(String, nullable=True)  # comma-separated
    perks = Column(String, nullable=True)
    corporate_code = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    extra = Column(JSON, nullable=True)

def init_db():
    # Create folders if needed
    db_path = settings.DB_URL.replace("sqlite:///", "") if settings.DB_URL.startswith("sqlite:///") else None
    if db_path:
        db_dir = os.path.dirname(db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    logger.info("Initialized database and tables.")
