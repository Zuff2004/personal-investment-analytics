from src.utils.cost_rules import (
    calculate_income_values,
    calculate_transaction_values,
)


def test_buy_transaction_values():
    result = calculate_transaction_values(
        transaction_type="BUY",
        quantity=100,
        price=10,
        fee_rate_pct=0.1,
        tax_rate_pct=0.2,
    )

    assert result.gross_value == 1000
    assert result.estimated_fees == 1
    assert result.estimated_taxes == 2
    assert result.net_value == 1003


def test_sell_transaction_values():
    result = calculate_transaction_values(
        transaction_type="SELL",
        quantity=100,
        price=10,
        fee_rate_pct=0.1,
        tax_rate_pct=0.2,
    )

    assert result.gross_value == 1000
    assert result.estimated_fees == 1
    assert result.estimated_taxes == 2
    assert result.net_value == 997


def test_income_without_withholding_tax():
    gross, tax, net = calculate_income_values(
        net_amount=100,
        withholding_tax_rate_pct=0,
    )

    assert gross == 100
    assert tax == 0
    assert net == 100


def test_income_with_withholding_tax():
    gross, tax, net = calculate_income_values(
        net_amount=85,
        withholding_tax_rate_pct=15,
    )

    assert round(gross, 2) == 100
    assert round(tax, 2) == 15
    assert net == 85
