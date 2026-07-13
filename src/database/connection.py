from pathlib import Path
import sqlite3

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "data" / "database" / "investment_analytics.db"
SCHEMA_PATH = PROJECT_ROOT / "src" / "database" / "schema.sql"


def get_connection() -> sqlite3.Connection:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON;")

    return connection


def initialize_database() -> None:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Schema file not found: {SCHEMA_PATH}")

    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")

    with get_connection() as connection:
        connection.executescript(schema_sql)


def fetch_dataframe(query: str, params: tuple = ()) -> pd.DataFrame:
    with get_connection() as connection:
        return pd.read_sql_query(query, connection, params=params)
