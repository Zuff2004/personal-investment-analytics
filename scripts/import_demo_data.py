from pathlib import Path
import sqlite3

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "data" / "database" / "investment_analytics.db"
TRANSACTIONS_PATH = PROJECT_ROOT / "demo_data" / "sample_transactions.csv"
PRICES_PATH = PROJECT_ROOT / "demo_data" / "sample_prices.csv"


def get_connection() -> sqlite3.Connection:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DATABASE_PATH)


def load_demo_files() -> tuple[pd.DataFrame, pd.DataFrame]:
    if not TRANSACTIONS_PATH.exists():
        raise FileNotFoundError(f"Missing file: {TRANSACTIONS_PATH}")

    if not PRICES_PATH.exists():
        raise FileNotFoundError(f"Missing file: {PRICES_PATH}")

    transactions = pd.read_csv(TRANSACTIONS_PATH)
    prices = pd.read_csv(PRICES_PATH)

    return transactions, prices


def insert_assets(connection: sqlite3.Connection, transactions: pd.DataFrame, prices: pd.DataFrame) -> None:
    tickers_from_transactions = transactions[["ticker", "asset_type", "currency"]].drop_duplicates()
    tickers_from_prices = prices[["ticker", "currency"]].drop_duplicates()
    tickers_from_prices["asset_type"] = "Unknown"

    assets = pd.concat(
        [tickers_from_transactions, tickers_from_prices],
        ignore_index=True,
    ).drop_duplicates(subset=["ticker"])

    for _, row in assets.iterrows():
        connection.execute(
            """
            INSERT OR IGNORE INTO assets (
                ticker, name, asset_type, currency, country, exchange, sector
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["ticker"],
                row["ticker"],
                row.get("asset_type", "Unknown"),
                row["currency"],
                "Brazil",
                "B3",
                None,
            ),
        )


def insert_accounts(connection: sqlite3.Connection, transactions: pd.DataFrame) -> None:
    accounts = transactions[["account", "currency"]].drop_duplicates()

    for _, row in accounts.iterrows():
        connection.execute(
            """
            INSERT OR IGNORE INTO accounts (
                broker_name, account_name, currency, country
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                row["account"],
                "Main Account",
                row["currency"],
                "Brazil",
            ),
        )


def get_asset_id(connection: sqlite3.Connection, ticker: str) -> int:
    result = connection.execute(
        "SELECT asset_id FROM assets WHERE ticker = ?",
        (ticker,),
    ).fetchone()

    if result is None:
        raise ValueError(f"Asset not found: {ticker}")

    return int(result[0])


def get_account_id(connection: sqlite3.Connection, broker_name: str) -> int:
    result = connection.execute(
        "SELECT account_id FROM accounts WHERE broker_name = ?",
        (broker_name,),
    ).fetchone()

    if result is None:
        raise ValueError(f"Account not found: {broker_name}")

    return int(result[0])


def insert_transactions(connection: sqlite3.Connection, transactions: pd.DataFrame) -> None:
    for _, row in transactions.iterrows():
        asset_id = get_asset_id(connection, row["ticker"])
        account_id = get_account_id(connection, row["account"])

        quantity = float(row["quantity"])
        price = float(row["price"])
        fees = float(row["fees"])
        taxes = float(row["taxes"])
        gross_value = quantity * price

        if row["transaction_type"] in ["BUY"]:
            net_value = gross_value + fees + taxes
        elif row["transaction_type"] in ["SELL"]:
            net_value = gross_value - fees - taxes
        else:
            net_value = gross_value - taxes

        connection.execute(
            """
            INSERT INTO transactions (
                date, account_id, asset_id, transaction_type,
                quantity, price, gross_value, fees, taxes,
                net_value, currency, notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["date"],
                account_id,
                asset_id,
                row["transaction_type"],
                quantity,
                price,
                gross_value,
                fees,
                taxes,
                net_value,
                row["currency"],
                row.get("notes", None),
            ),
        )


def insert_market_prices(connection: sqlite3.Connection, prices: pd.DataFrame) -> None:
    for _, row in prices.iterrows():
        asset_id = get_asset_id(connection, row["ticker"])

        connection.execute(
            """
            INSERT OR REPLACE INTO market_prices (
                asset_id, date, close_price, currency, source
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                asset_id,
                row["date"],
                float(row["close_price"]),
                row["currency"],
                "demo_data",
            ),
        )


def main() -> None:
    transactions, prices = load_demo_files()

    with get_connection() as connection:
        insert_assets(connection, transactions, prices)
        insert_accounts(connection, transactions)
        insert_transactions(connection, transactions)
        insert_market_prices(connection, prices)

    print("Demo data imported successfully into SQLite database.")
    print(f"Database path: {DATABASE_PATH}")


if __name__ == "__main__":
    main()
