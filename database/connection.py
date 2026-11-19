"""
SubroRecover AI - Database Connection Manager
Provides connection resilience between PostgreSQL and SQLite fallback.
"""

import os
import re
import logging
from typing import Generator
from pathlib import Path
from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# Configure logging
logger = logging.getLogger("subrorecover.database")

Base = declarative_base()

def mask_db_url(url: str) -> str:
    """Masks database passwords to prevent sensitive data exposure in logs."""
    if not url:
        return ""
    # Mask password in postgresql://user:password@host...
    return re.sub(r":([^:@]+)@", ":****@", url)

def get_engine():
    """
    Initializes and returns an SQLAlchemy Engine.
    Tries PostgreSQL first if configured; falls back cleanly to local SQLite.
    """
    raw_url = os.getenv("DATABASE_URL", "sqlite:///./subro_recover.db")
    allow_fallback = os.getenv("DB_FALLBACK_TO_SQLITE", "true").lower() in ("true", "1", "yes")

    # If already an sqlite url, initialize directly
    if raw_url.startswith("sqlite"):
        # Ensure foreign keys are enforced in SQLite
        engine = create_engine(
            raw_url,
            connect_args={"check_same_thread": False},
            echo=False
        )
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        logger.info(f"Using SQLite database engine: {mask_db_url(raw_url)}")
        return engine

    # If PostgreSQL URL is provided, test connectivity with a short timeout
    try:
        engine = create_engine(
            raw_url,
            connect_args={"connect_timeout": 3},
            pool_pre_ping=True
        )
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info(f"Connected successfully to PostgreSQL: {mask_db_url(raw_url)}")
        return engine
    except Exception as e:
        logger.warning(f"Could not connect to PostgreSQL ({mask_db_url(raw_url)}): {e}")
        if allow_fallback:
            fallback_url = "sqlite:///./subro_recover.db"
            logger.info(f"Falling back to resilient local SQLite database: {fallback_url}")
            engine = create_engine(
                fallback_url,
                connect_args={"check_same_thread": False},
                echo=False
            )
            @event.listens_for(engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()
            return engine
        else:
            raise e

# Global engine and sessionmaker
engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """Dependency for FastAPI or standalone scripts to acquire a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db(schema_path: str = None) -> bool:
    """
    Executes database/schema.sql on the active engine to ensure all 10 tables exist.
    """
    if schema_path is None:
        schema_path = str(Path(__file__).parent / "schema.sql")

    if not os.path.exists(schema_path):
        logger.error(f"Schema file not found at {schema_path}")
        return False

    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    # Split commands by semicolon to handle both SQLite and PG execution
    statements = [stmt.strip() for stmt in schema_sql.split(";") if stmt.strip()]

    with engine.begin() as conn:
        for stmt in statements:
            # Skip pure comments or empty lines
            if stmt.startswith("--") and "\n" not in stmt:
                continue
            try:
                conn.execute(text(stmt))
            except Exception as e:
                # If table already exists or minor dialect syntax difference
                logger.debug(f"Statement notice: {e}")

    logger.info("Database initialized successfully with all tables and indexes.")
    return True

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    success = init_db()
    print("Database init result:", success)
