"""
backend/app/database.py - Database Engine and Session Management
SQLAlchemy ORM setup for HealthSaathi AI using SQLite.
Supports parameterized queries, transaction safety, and schema auto-creation.
"""

import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# Database path: root health_copilot.db or backend-local
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(BASE_DIR)

# Prefer root health_copilot.db if exists, otherwise workspace root
DB_PATH = os.environ.get("HEALTH_DB_PATH", os.path.join(ROOT_DIR, "health_copilot.db"))
UPLOAD_DIR = os.path.join(ROOT_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

# Enable foreign key enforcement and WAL mode in SQLite for concurrency and integrity
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency that yields a SQLAlchemy database session and ensures cleanup."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initializes tables using SQLAlchemy metadata."""
    try:
        from backend.app import models
    except ImportError:
        from . import models
    Base.metadata.create_all(bind=engine)
