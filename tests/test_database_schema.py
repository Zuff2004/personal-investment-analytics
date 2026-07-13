from pathlib import Path


def test_schema_file_exists():
    project_root = Path(__file__).resolve().parents[1]
    schema_path = project_root / "src" / "database" / "schema.sql"

    assert schema_path.exists()


def test_schema_contains_core_tables():
    project_root = Path(__file__).resolve().parents[1]
    schema_path = project_root / "src" / "database" / "schema.sql"

    schema = schema_path.read_text(encoding="utf-8").lower()

    required_tables = [
        "assets",
        "accounts",
        "transactions",
        "income_events",
        "strategies",
        "signals",
        "trades",
        "trade_legs",
        "realized_gains",
        "loss_carryforward",
        "market_prices",
        "backtests",
        "backtest_results",
        "reports",
    ]

    for table in required_tables:
        assert table in schema
