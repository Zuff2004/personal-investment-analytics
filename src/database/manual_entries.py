from datetime import date, datetime
import sqlite3

from src.database.connection import get_connection
from src.utils.cost_rules import (
    calculate_income_values,
    calculate_transaction_values,
)


def get_or_create_asset(
    ticker: str,
    asset_type: str,
    currency: str,
    name: str | None = None,
    country: str | None = None,
    exchange: str | None = None,
    sector: str | None = None,
) -> int:
    ticker = ticker.upper().strip()

    with get_connection() as connection:
        existing = connection.execute(
            "SELECT asset_id FROM assets WHERE ticker = ?",
            (ticker,),
        ).fetchone()

        if existing:
            return int(existing["asset_id"])

        cursor = connection.execute(
            """
            INSERT INTO assets (
                ticker, name, asset_type, currency, country, exchange, sector
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ticker,
                name or ticker,
                asset_type,
                currency,
                country,
                exchange,
                sector,
            ),
        )

        return int(cursor.lastrowid)


def get_or_create_account(
    broker_name: str,
    account_name: str,
    currency: str,
    country: str | None = None,
) -> int:
    broker_name = broker_name.strip()
    account_name = account_name.strip()

    with get_connection() as connection:
        existing = connection.execute(
            """
            SELECT account_id
            FROM accounts
            WHERE broker_name = ? AND account_name = ? AND currency = ?
            """,
            (broker_name, account_name, currency),
        ).fetchone()

        if existing:
            return int(existing["account_id"])

        cursor = connection.execute(
            """
            INSERT INTO accounts (
                broker_name, account_name, currency, country
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                broker_name,
                account_name,
                currency,
                country,
            ),
        )

        return int(cursor.lastrowid)


def get_or_create_strategy(
    name: str,
    description: str | None = None,
    strategy_type: str | None = None,
    asset_universe: str | None = None,
) -> int:
    name = name.strip()

    with get_connection() as connection:
        existing = connection.execute(
            "SELECT strategy_id FROM strategies WHERE name = ?",
            (name,),
        ).fetchone()

        if existing:
            return int(existing["strategy_id"])

        cursor = connection.execute(
            """
            INSERT INTO strategies (
                name, description, strategy_type, asset_universe, active, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                description,
                strategy_type,
                asset_universe,
                1,
                date.today().isoformat(),
            ),
        )

        return int(cursor.lastrowid)


def add_transaction(
    transaction_date: date,
    ticker: str,
    asset_type: str,
    transaction_type: str,
    quantity: float,
    price: float,
    broker_name: str,
    account_name: str,
    currency: str,
    fee_rate_pct: float = 0.0,
    tax_rate_pct: float = 0.0,
    strategy_name: str | None = None,
    notes: str | None = None,
) -> int:
    transaction_type = transaction_type.upper()

    if transaction_type not in {"BUY", "SELL"}:
        raise ValueError("Transaction type must be BUY or SELL.")

    asset_id = get_or_create_asset(
        ticker=ticker,
        asset_type=asset_type,
        currency=currency,
    )

    account_id = get_or_create_account(
        broker_name=broker_name,
        account_name=account_name,
        currency=currency,
    )

    if strategy_name:
        get_or_create_strategy(name=strategy_name)

    values = calculate_transaction_values(
        transaction_type=transaction_type,
        quantity=quantity,
        price=price,
        fee_rate_pct=fee_rate_pct,
        tax_rate_pct=tax_rate_pct,
    )

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO transactions (
                date, account_id, asset_id, transaction_type,
                quantity, price, gross_value, fees, taxes,
                net_value, currency, notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                transaction_date.isoformat(),
                account_id,
                asset_id,
                transaction_type,
                quantity,
                price,
                values.gross_value,
                values.estimated_fees,
                values.estimated_taxes,
                values.net_value,
                currency,
                notes,
            ),
        )

        return int(cursor.lastrowid)


def add_income_event(
    income_date: date,
    ticker: str,
    asset_type: str,
    income_type: str,
    net_amount: float,
    broker_name: str,
    account_name: str,
    currency: str,
    withholding_tax_rate_pct: float = 0.0,
    related_quantity: float | None = None,
    notes: str | None = None,
) -> int:
    income_type = income_type.upper()

    if income_type not in {"DIVIDEND", "JCP", "STOCK_LENDING", "INTEREST", "COUPON"}:
        raise ValueError("Invalid income type.")

    asset_id = get_or_create_asset(
        ticker=ticker,
        asset_type=asset_type,
        currency=currency,
    )

    account_id = get_or_create_account(
        broker_name=broker_name,
        account_name=account_name,
        currency=currency,
    )

    gross_amount, tax_withheld, net_amount = calculate_income_values(
        net_amount=net_amount,
        withholding_tax_rate_pct=withholding_tax_rate_pct,
    )

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO income_events (
                date, account_id, asset_id, income_type,
                gross_amount, tax_withheld, net_amount,
                currency, related_quantity, notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                income_date.isoformat(),
                account_id,
                asset_id,
                income_type,
                gross_amount,
                tax_withheld,
                net_amount,
                currency,
                related_quantity,
                notes,
            ),
        )

        return int(cursor.lastrowid)


def add_market_price(
    price_date: date,
    ticker: str,
    asset_type: str,
    close_price: float,
    currency: str,
    source: str = "manual",
) -> int:
    asset_id = get_or_create_asset(
        ticker=ticker,
        asset_type=asset_type,
        currency=currency,
    )

    retrieved_at = datetime.now().isoformat(timespec="seconds")

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT OR REPLACE INTO market_prices (
                asset_id, date, close_price, currency, source, retrieved_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                asset_id,
                price_date.isoformat(),
                close_price,
                currency,
                source,
                retrieved_at,
            ),
        )

        return int(cursor.lastrowid)
def add_strategy(
    name: str,
    description: str | None,
    strategy_type: str | None,
    asset_universe: str | None,
) -> int:
    return get_or_create_strategy(
        name=name,
        description=description,
        strategy_type=strategy_type,
        asset_universe=asset_universe,
    )
