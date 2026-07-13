import pandas as pd
import pytest

from src.portfolio.positions import calculate_positions_from_transactions


def test_average_cost_and_realized_pnl():
    transactions = pd.DataFrame(
        [
            {
                "date": "2024-01-01",
                "ticker": "PETR4",
                "transaction_type": "BUY",
                "quantity": 100,
                "price": 10,
                "gross_value": 1000,
                "fees": 1,
                "taxes": 0,
                "net_value": 1001,
                "currency": "BRL",
            },
            {
                "date": "2024-02-01",
                "ticker": "PETR4",
                "transaction_type": "SELL",
                "quantity": 40,
                "price": 12,
                "gross_value": 480,
                "fees": 1,
                "taxes": 0,
                "net_value": 479,
                "currency": "BRL",
            },
        ]
    )

    latest_prices = pd.DataFrame(
        [
            {
                "ticker": "PETR4",
                "price_date": "2024-03-01",
                "close_price": 11,
                "currency": "BRL",
                "source": "test",
            }
        ]
    )

    positions = calculate_positions_from_transactions(
        transactions=transactions,
        latest_prices=latest_prices,
    )

    petr4 = positions.iloc[0]

    assert petr4["ticker"] == "PETR4"
    assert petr4["quantity"] == 60

    assert pytest.approx(petr4["average_cost"], 0.0001) == 10.01
    assert pytest.approx(petr4["remaining_cost_basis"], 0.0001) == 600.6
    assert pytest.approx(petr4["realized_pnl"], 0.0001) == 78.6
    assert pytest.approx(petr4["market_value"], 0.0001) == 660
    assert pytest.approx(petr4["unrealized_pnl"], 0.0001) == 59.4


def test_cannot_sell_more_than_position():
    transactions = pd.DataFrame(
        [
            {
                "date": "2024-01-01",
                "ticker": "PETR4",
                "transaction_type": "BUY",
                "quantity": 10,
                "price": 10,
                "gross_value": 100,
                "fees": 0,
                "taxes": 0,
                "net_value": 100,
                "currency": "BRL",
            },
            {
                "date": "2024-02-01",
                "ticker": "PETR4",
                "transaction_type": "SELL",
                "quantity": 20,
                "price": 12,
                "gross_value": 240,
                "fees": 0,
                "taxes": 0,
                "net_value": 240,
                "currency": "BRL",
            },
        ]
    )

    latest_prices = pd.DataFrame()

    with pytest.raises(ValueError):
        calculate_positions_from_transactions(
            transactions=transactions,
            latest_prices=latest_prices,
        )
