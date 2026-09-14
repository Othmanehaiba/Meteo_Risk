"""Acces a PostgreSQL pour le dashboard."""

import os

from sqlalchemy import create_engine


def get_engine():
    """Construit l'engine SQLAlchemy depuis DATABASE_URL."""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL est requis")
    return create_engine(database_url)
