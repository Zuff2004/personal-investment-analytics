from __future__ import annotations

import pandas as pd

from src.database.connection import fetch_dataframe


def fetch_transactions_from_database() -> pd.DataFrame:
    return fetch_dataframe(
        """
        SELECT
            t.transaction_id,
            t.date,
            a.ticker,
            a.asset_type,
            t.transaction_type,
            t.quantity,
            t.price,
            t.gross_value,
            t.fees,
            t.taxes,
            t.net_value,
            t.currency,
            t.notes
        FROM transactions t
        LEFT JOIN assets a ON t.asset_id = a.asset_id
        WHERE t.transaction_type IN ('BUY', 'SELL')
        ORDER BY t.date ASC, t.transaction_id ASC
        """
    )


def fetch_latest_prices_from_database() -> pd.DataFrame:
    return fetch_dataframe(
        """
        SELECT
            a.ticker,
            p.date AS price_date,
            p.close_price,
            p.currency,
            p.source,
            p.retrieved_at
        FROM market_prices p
        LEFT JOIN assets a ON p.asset_id = a.asset_id
        INNER JOIN (
            SELECT
                asset_id,
                MAX(date) AS latest_date
            FROM market_prices
            GROUP BY asset_id
        ) latest
            ON p.asset_id = latest.asset_id
            AND p.date = latest.latest_date
        ORDER BY a.ticker
        """
    )


def fetch_income_from_database() -> pd.DataFrame:
    return fetch_dataframe(
        """
        SELECT
            i.income_id,
            i.date,
            a.ticker,
            i.income_type,
            i.gross_amount,
            i.tax_withheld,
            i.net_amount,
            i.currency,
            i.related_quantity,
            i.notes
        FROM income_events i
        LEFT JOIN assets a ON i.asset_id = a.asset_id
        ORDER BY i.date ASC, i.income_id ASC
        """
    )


def calculate_positions_from_transactions(
    transactions: pd.DataFrame,
    latest_prices: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate long-only positions using average cost.

    Rules:
    - BUY increases quantity and cost basis.
    - SELL reduces quantity using the current average cost.
    - SELL realized PnL = net sale proceeds - cost basis sold.
    - Remaining cost basis = remaining quantity * average cost.
    """
    if transactions.empty:
        return pd.DataFrame(
            columns=[
                "ticker",
                "quantity",
                "average_cost",
                "remaining_cost_basis",
                "realized_pnl",
                "latest_price",
                "price_date",
                "market_value",
                "unrealized_pnl",
                "unrealized_return_pct",
            ]
        )

    required_columns = {
        "date",
        "ticker",
        "transaction_type",
        "quantity",
        "net_value",
    }

    missing_columns = required_columns - set(transactions.columns)

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    transactions = transactions.copy()
    transactions["date"] = pd.to_datetime(transactions["date"])
    transactions["transaction_type"] = transactions["transaction_type"].str.upper()
    transactions = transactions.sort_values(["ticker", "date"])

    position_records: list[dict] = []

    for ticker, ticker_transactions in transactions.groupby("ticker"):
        quantity = 0.0
        cost_basis = 0.0
        realized_pnl = 0.0

        for _, row in ticker_transactions.iterrows():
            transaction_type = row["transaction_type"]
            transaction_quantity = float(row["quantity"])
            net_value = float(row["net_value"])

            if transaction_quantity <= 0:
                raise ValueError(f"Quantity must be positive for {ticker}.")

            if transaction_type == "BUY":
                quantity += transaction_quantity
                cost_basis += net_value

            elif transaction_type == "SELL":
                if quantity <= 0:
                    raise ValueError(
                        f"Cannot sell {ticker}: no open position available."
                    )

                if transaction_quantity > quantity:
                    raise ValueError(
                        f"Cannot sell {transaction_quantity} of {ticker}. "
                        f"Current position is {quantity}."
                    )

                average_cost_before_sale = cost_basis / quantity
                sold_cost_basis = average_cost_before_sale * transaction_quantity
                sale_proceeds = net_value

                realized_pnl += sale_proceeds - sold_cost_basis

                quantity -= transaction_quantity
                cost_basis -= sold_cost_basis

            else:
                raise ValueError(f"Unsupported transaction type: {transaction_type}")

        average_cost = cost_basis / quantity if quantity > 0 else 0.0

        position_records.append(
            {
                "ticker": ticker,
                "quantity": round(quantity, 6),
                "average_cost": round(average_cost, 6),
                "remaining_cost_basis": round(cost_basis, 6),
                "realized_pnl": round(realized_pnl, 6),
            }
        )

    positions = pd.DataFrame(position_records)

    if latest_prices.empty:
        positions["latest_price"] = pd.NA
        positions["price_date"] = pd.NA
        positions["market_value"] = pd.NA
        positions["unrealized_pnl"] = pd.NA
        positions["unrealized_return_pct"] = pd.NA
        return positions

    prices = latest_prices.copy()
    prices = prices[["ticker", "price_date", "close_price"]].rename(
        columns={"close_price": "latest_price"}
    )

    positions = positions.merge(prices, on="ticker", how="left")

    positions["market_value"] = positions["quantity"] * positions["latest_price"]
    positions["unrealized_pnl"] = (
        positions["market_value"] - positions["remaining_cost_basis"]
    )

    positions["unrealized_return_pct"] = (
        positions["unrealized_pnl"] / positions["remaining_cost_basis"]
    ) * 100

    numeric_columns = [
        "market_value",
        "unrealized_pnl",
        "unrealized_return_pct",
    ]

    for column in numeric_columns:
        positions[column] = positions[column].round(6)

    return positions


def calculate_income_summary(income: pd.DataFrame) -> pd.DataFrame:
    if income.empty:
        return pd.DataFrame(
            columns=[
                "ticker",
                "total_gross_income",
                "total_tax_withheld",
                "total_net_income",
            ]
        )

    return (
        income.groupby("ticker")
        .agg(
            total_gross_income=("gross_amount", "sum"),
            total_tax_withheld=("tax_withheld", "sum"),
            total_net_income=("net_amount", "sum"),
        )
        .reset_index()
    )


def calculate_portfolio_summary(
    positions: pd.DataFrame,
    income: pd.DataFrame,
) -> dict:
    if positions.empty:
        total_market_value = 0.0
        total_cost_basis = 0.0
        total_realized_pnl = 0.0
        total_unrealized_pnl = 0.0
    else:
        total_market_value = positions["market_value"].fillna(0).sum()
        total_cost_basis = positions["remaining_cost_basis"].fillna(0).sum()
        total_realized_pnl = positions["realized_pnl"].fillna(0).sum()
        total_unrealized_pnl = positions["unrealized_pnl"].fillna(0).sum()

    total_income = 0.0 if income.empty else income["net_amount"].fillna(0).sum()

    total_pnl = total_realized_pnl + total_unrealized_pnl + total_income

    total_return_pct = (
        (total_pnl / total_cost_basis) * 100 if total_cost_basis > 0 else 0.0
    )

    return {
        "total_market_value": round(total_market_value, 2),
        "total_cost_basis": round(total_cost_basis, 2),
        "total_realized_pnl": round(total_realized_pnl, 2),
        "total_unrealized_pnl": round(total_unrealized_pnl, 2),
        "total_income": round(total_income, 2),
        "total_pnl": round(total_pnl, 2),
        "total_return_pct": round(total_return_pct, 2),
    }


def calculate_positions_from_database() -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    transactions = fetch_transactions_from_database()
    latest_prices = fetch_latest_prices_from_database()
    income = fetch_income_from_database()

    positions = calculate_positions_from_transactions(
        transactions=transactions,
        latest_prices=latest_prices,
    )

    income_summary = calculate_income_summary(income)
    summary = calculate_portfolio_summary(positions, income)

    return positions, income_summary, summary
