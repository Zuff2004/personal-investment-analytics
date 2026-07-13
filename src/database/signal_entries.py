from datetime import date

from src.database.connection import get_connection
from src.database.manual_entries import get_or_create_asset, get_or_create_strategy


def save_multi_leg_signal(
    signal_date: date,
    strategy_name: str,
    signal: str,
    signal_strength: float,
    suggested_action: str,
    legs: list[dict],
    asset_type: str = "Stock",
    currency: str = "BRL",
    notes: str | None = None,
) -> int:
    """
    Save a strategy signal with multiple legs.

    This supports:
    - single asset signals;
    - pair trading signals;
    - rotation signals;
    - rebalance signals.
    """
    if not legs:
        raise ValueError("At least one signal leg is required.")

    strategy_id = get_or_create_strategy(
        name=strategy_name,
        strategy_type="PAIR_TRADING",
    )

    primary_ticker = legs[0]["ticker"]

    primary_asset_id = get_or_create_asset(
        ticker=primary_ticker,
        asset_type=asset_type,
        currency=currency,
    )

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO signals (
                strategy_id, date, asset_id, signal,
                signal_strength, suggested_action, target_weight,
                executed, notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                strategy_id,
                signal_date.isoformat(),
                primary_asset_id,
                signal,
                signal_strength,
                suggested_action,
                None,
                0,
                notes,
            ),
        )

        signal_id = int(cursor.lastrowid)

        for leg in legs:
            asset_id = get_or_create_asset(
                ticker=leg["ticker"],
                asset_type=asset_type,
                currency=currency,
            )

            connection.execute(
                """
                INSERT INTO signal_legs (
                    signal_id, asset_id, leg_action,
                    target_weight, suggested_quantity, suggested_price,
                    score, notes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    signal_id,
                    asset_id,
                    leg["action"],
                    leg.get("target_weight"),
                    leg.get("suggested_quantity"),
                    leg.get("suggested_price"),
                    leg.get("score"),
                    leg.get("notes"),
                ),
            )

        return signal_id
