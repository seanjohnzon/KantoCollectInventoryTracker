"""Database configuration and helpers."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.models import Base


def get_database_url() -> str:
    """
    Build the SQLite database URL.

    Returns:
        str: SQLAlchemy database URL.
    """
    db_path = os.getenv("KANTO_DB_PATH")
    if db_path:
        return f"sqlite+pysqlite:///{db_path}"
    root = Path(__file__).resolve().parents[1]
    return f"sqlite+pysqlite:///{root / 'data' / 'inventory.db'}"


def _ensure_sqlite_dir(database_url: str) -> None:
    """
    Ensure the directory for the SQLite database exists.

    Args:
        database_url (str): SQLAlchemy database URL.
    """
    if database_url.startswith("sqlite") and "///" in database_url:
        raw_path = database_url.split("///", 1)[1]
        if raw_path:
            Path(raw_path).expanduser().parent.mkdir(parents=True, exist_ok=True)


def get_engine(database_url: str | None = None) -> Engine:
    """
    Create a SQLAlchemy engine.

    Args:
        database_url (str | None): Override database URL when provided.

    Returns:
        Engine: SQLAlchemy engine instance.
    """
    resolved_url = database_url or get_database_url()
    _ensure_sqlite_dir(resolved_url)
    connect_args = {"check_same_thread": False} if resolved_url.startswith("sqlite") else {}
    return create_engine(resolved_url, future=True, connect_args=connect_args)


def create_db_and_tables(engine: Engine) -> None:
    """
    Create database tables if they do not exist.

    Args:
        engine (Engine): SQLAlchemy engine.
    """
    Base.metadata.create_all(engine)


def get_session_factory(engine: Engine) -> sessionmaker[Session]:
    """
    Build a session factory bound to the provided engine.

    Args:
        engine (Engine): SQLAlchemy engine.

    Returns:
        sessionmaker[Session]: SQLAlchemy session factory.
    """
    return sessionmaker(bind=engine, class_=Session, expire_on_commit=False)


def get_session(session_factory: sessionmaker[Session]) -> Generator[Session, None, None]:
    """
    Provide a SQLAlchemy session generator.

    Args:
        session_factory (sessionmaker[Session]): Session factory.

    Yields:
        Session: SQLAlchemy session.
    """
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
