from pathlib import Path
import sqlite3


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "data" / "database" / "investment_analytics.db"
SCHEMA_PATH = PROJECT_ROOT / "src" / "database" / "schema.sql"


def initialize_database() -> None:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Schema file not found: {SCHEMA_PATH}")

    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.executescript(schema_sql)

    print(f"Database initialized successfully at: {DATABASE_PATH}")


if __name__ == "__main__":
    initialize_database()
