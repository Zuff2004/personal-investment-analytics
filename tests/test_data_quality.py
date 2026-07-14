import pandas as pd

from src.quality.data_quality import (
    validate_missing_prices,
    validate_sell_consistency,
    validate_transaction_values,
)


def test_detect_sell_without_position():
    transactions = pd.DataFrame(
        [
            {
                "transaction_id": 1,
                "date": "2024-01-01",
                "ticker": "BBAS3",
                "transaction_type": "SELL",
                "quantity": 10,
                "price": 30,
                "net_value": 300,
            }
        ]
    )

    issues = validate_sell_consistency(transactions)

    assert len(issues) == 1
    assert issues[0]["category"] == "Sell without position"
    assert issues[0]["severity"] == "ERROR"


def test_detect_sell_exceeds_position():
    transactions = pd.DataFrame(
        [
            {
                "transaction_id": 1,
                "date": "2024-01-01",
                "ticker": "PETR4",
                "transaction_type": "BUY",
                "quantity": 10,
                "price": 30,
                "net_value": 300,
            },
            {
                "transaction_id": 2,
                "date": "2024-01-02",
                "ticker": "PETR4",
                "transaction_type": "SELL",
                "quantity": 15,
                "price": 35,
                "net_value": 525,
            },
        ]
    )

    issues = validate_sell_consistency(transactions)

    assert len(issues) == 1
    assert issues[0]["category"] == "Sell exceeds position"
    assert issues[0]["severity"] == "ERROR"


def test_detect_missing_price():
    transactions = pd.DataFrame(
        [
            {
                "transaction_id": 1,
                "date": "2024-01-01",
                "ticker": "PETR4",
                "transaction_type": "BUY",
                "quantity": 10,
                "price": 30,
                "net_value": 300,
            }
        ]
    )

    latest_prices = pd.DataFrame(columns=["ticker", "close_price"])

    issues = validate_missing_prices(transactions, latest_prices)

    assert len(issues) == 1
    assert issues[0]["category"] == "Missing market price"
    assert issues[0]["severity"] == "WARNING"


def test_valid_transaction_has_no_value_issue():
    transactions = pd.DataFrame(
        [
            {
                "transaction_id": 1,
                "date": "2024-01-01",
                "ticker": "PETR4",
                "transaction_type": "BUY",
                "quantity": 10,
                "price": 30,
                "net_value": 300,
            }
        ]
    )

    issues = validate_transaction_values(transactions)

    assert issues == []
