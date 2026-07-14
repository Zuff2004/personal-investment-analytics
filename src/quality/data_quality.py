from __future__ import annotations

import pandas as pd

from src.database.connection import fetch_dataframe


def fetch_all_transactions() -> pd.DataFrame:
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
        ORDER BY t.date ASC, t.transaction_id ASC
        """
    )


def fetch_latest_prices() -> pd.DataFrame:
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


def fetch_income_events() -> pd.DataFrame:
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


def _issue(
    severity: str,
    category: str,
    message: str,
    ticker: str | None = None,
    transaction_id: int | None = None,
    suggested_fix: str | None = None,
) -> dict:
    return {
        "severity": severity,
        "category": category,
        "ticker": ticker,
        "transaction_id": transaction_id,
        "message": message,
        "suggested_fix": suggested_fix,
    }


def validate_transaction_values(transactions: pd.DataFrame) -> list[dict]:
    issues: list[dict] = []

    if transactions.empty:
        return issues

    for _, row in transactions.iterrows():
        transaction_id = int(row["transaction_id"])
        ticker = row["ticker"]

        quantity = row["quantity"]
        price = row["price"]
        net_value = row["net_value"]

        if pd.isna(ticker) or str(ticker).strip() == "":
            issues.append(
                _issue(
                    severity="ERROR",
                    category="Missing ticker",
                    message="Transaction has no ticker.",
                    transaction_id=transaction_id,
                    suggested_fix="Edit or remove the transaction and assign a valid ticker.",
                )
            )

        if pd.isna(quantity) or float(quantity) <= 0:
            issues.append(
                _issue(
                    severity="ERROR",
                    category="Invalid quantity",
                    ticker=ticker,
                    transaction_id=transaction_id,
                    message="Transaction quantity must be positive.",
                    suggested_fix="Check the quantity entered for this transaction.",
                )
            )

        if row["transaction_type"] in {"BUY", "SELL"}:
            if pd.isna(price) or float(price) <= 0:
                issues.append(
                    _issue(
                        severity="ERROR",
                        category="Invalid price",
                        ticker=ticker,
                        transaction_id=transaction_id,
                        message="Buy/sell transaction price must be positive.",
                        suggested_fix="Check the price entered for this transaction.",
                    )
                )

        if pd.isna(net_value):
            issues.append(
                _issue(
                    severity="ERROR",
                    category="Missing net value",
                    ticker=ticker,
                    transaction_id=transaction_id,
                    message="Transaction has no net value.",
                    suggested_fix="Re-save the transaction so the system can calculate net value.",
                )
            )

    return issues


def validate_sell_consistency(transactions: pd.DataFrame) -> list[dict]:
    """
    Detect SELL transactions without enough previous position.

    Uses chronological average-cost style position tracking, but only validates quantity.
    """
    issues: list[dict] = []

    if transactions.empty:
        return issues

    buy_sell = transactions[
        transactions["transaction_type"].isin(["BUY", "SELL"])
    ].copy()

    if buy_sell.empty:
        return issues

    buy_sell["date"] = pd.to_datetime(buy_sell["date"])
    buy_sell = buy_sell.sort_values(["ticker", "date", "transaction_id"])

    for ticker, ticker_transactions in buy_sell.groupby("ticker"):
        position = 0.0

        for _, row in ticker_transactions.iterrows():
            transaction_type = row["transaction_type"]
            quantity = float(row["quantity"])
            transaction_id = int(row["transaction_id"])

            if transaction_type == "BUY":
                position += quantity

            elif transaction_type == "SELL":
                if position <= 0:
                    issues.append(
                        _issue(
                            severity="ERROR",
                            category="Sell without position",
                            ticker=ticker,
                            transaction_id=transaction_id,
                            message=(
                                f"SELL transaction for {ticker} has no previous open position."
                            ),
                            suggested_fix=(
                                "Add the missing BUY/TRANSFER_IN transaction before this sale, "
                                "or check whether the ticker/date is wrong."
                            ),
                        )
                    )

                elif quantity > position:
                    issues.append(
                        _issue(
                            severity="ERROR",
                            category="Sell exceeds position",
                            ticker=ticker,
                            transaction_id=transaction_id,
                            message=(
                                f"SELL quantity for {ticker} exceeds current position. "
                                f"Current position before sale: {position}, sale quantity: {quantity}."
                            ),
                            suggested_fix=(
                                "Check the sale quantity or add missing previous purchases/transfers."
                            ),
                        )
                    )

                position -= quantity

    return issues


def validate_missing_prices(
    transactions: pd.DataFrame,
    latest_prices: pd.DataFrame,
) -> list[dict]:
    issues: list[dict] = []

    if transactions.empty:
        return issues

    traded_tickers = set(
        transactions.loc[
            transactions["transaction_type"].isin(["BUY", "SELL"]),
            "ticker",
        ].dropna()
    )

    priced_tickers = set(latest_prices["ticker"].dropna()) if not latest_prices.empty else set()

    missing = sorted(traded_tickers - priced_tickers)

    for ticker in missing:
        issues.append(
            _issue(
                severity="WARNING",
                category="Missing market price",
                ticker=ticker,
                message=f"{ticker} has transactions but no saved market price.",
                suggested_fix="Open the Portfolio page to auto-update prices, or fetch it manually in Market Data.",
            )
        )

    return issues


def validate_income_events(
    transactions: pd.DataFrame,
    income_events: pd.DataFrame,
) -> list[dict]:
    issues: list[dict] = []

    if income_events.empty:
        return issues

    traded_tickers = set(transactions["ticker"].dropna()) if not transactions.empty else set()

    for _, row in income_events.iterrows():
        ticker = row["ticker"]
        income_id = int(row["income_id"])

        if pd.isna(row["net_amount"]) or float(row["net_amount"]) < 0:
            issues.append(
                _issue(
                    severity="ERROR",
                    category="Invalid income amount",
                    ticker=ticker,
                    message=f"Income event #{income_id} has invalid net amount.",
                    suggested_fix="Check the income event amount.",
                )
            )

        if ticker not in traded_tickers:
            issues.append(
                _issue(
                    severity="INFO",
                    category="Income without transaction",
                    ticker=ticker,
                    message=(
                        f"Income event for {ticker} exists, but no buy/sell transaction was found."
                    ),
                    suggested_fix=(
                        "This may be fine for transferred assets, but consider adding an initial position."
                    ),
                )
            )

    return issues


def run_data_quality_checks() -> pd.DataFrame:
    transactions = fetch_all_transactions()
    latest_prices = fetch_latest_prices()
    income_events = fetch_income_events()

    issues: list[dict] = []

    issues.extend(validate_transaction_values(transactions))
    issues.extend(validate_sell_consistency(transactions))
    issues.extend(validate_missing_prices(transactions, latest_prices))
    issues.extend(validate_income_events(transactions, income_events))

    if not issues:
        return pd.DataFrame(
            columns=[
                "severity",
                "category",
                "ticker",
                "transaction_id",
                "message",
                "suggested_fix",
            ]
        )

    return pd.DataFrame(issues)


def summarize_issues(issues: pd.DataFrame) -> dict:
    if issues.empty:
        return {
            "total": 0,
            "errors": 0,
            "warnings": 0,
            "info": 0,
        }

    return {
        "total": int(len(issues)),
        "errors": int((issues["severity"] == "ERROR").sum()),
        "warnings": int((issues["severity"] == "WARNING").sum()),
        "info": int((issues["severity"] == "INFO").sum()),
    }
