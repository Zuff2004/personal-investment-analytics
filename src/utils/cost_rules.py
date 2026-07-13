from dataclasses import dataclass


@dataclass
class TransactionCostResult:
    gross_value: float
    estimated_fees: float
    estimated_taxes: float
    net_value: float


def calculate_transaction_values(
    transaction_type: str,
    quantity: float,
    price: float,
    fee_rate_pct: float = 0.0,
    tax_rate_pct: float = 0.0,
) -> TransactionCostResult:
    """
    Calculate gross value, estimated fees, estimated taxes and net value.

    The fee and tax rates are configurable assumptions. The user enters only the
    transaction event, while the system calculates derived values.
    """
    transaction_type = transaction_type.upper()

    if quantity <= 0:
        raise ValueError("Quantity must be positive.")

    if price <= 0:
        raise ValueError("Price must be positive.")

    if fee_rate_pct < 0:
        raise ValueError("Fee rate cannot be negative.")

    if tax_rate_pct < 0:
        raise ValueError("Tax rate cannot be negative.")

    gross_value = quantity * price
    estimated_fees = gross_value * (fee_rate_pct / 100)
    estimated_taxes = gross_value * (tax_rate_pct / 100)

    if transaction_type == "BUY":
        net_value = gross_value + estimated_fees + estimated_taxes
    elif transaction_type == "SELL":
        net_value = gross_value - estimated_fees - estimated_taxes
    else:
        raise ValueError("Transaction type must be BUY or SELL.")

    return TransactionCostResult(
        gross_value=round(gross_value, 6),
        estimated_fees=round(estimated_fees, 6),
        estimated_taxes=round(estimated_taxes, 6),
        net_value=round(net_value, 6),
    )


def calculate_income_values(
    net_amount: float,
    withholding_tax_rate_pct: float = 0.0,
) -> tuple[float, float, float]:
    """
    Calculate gross income and withholding tax from a net amount received.

    Returns:
        gross_amount, tax_withheld, net_amount
    """
    if net_amount < 0:
        raise ValueError("Net amount cannot be negative.")

    if withholding_tax_rate_pct < 0 or withholding_tax_rate_pct >= 100:
        raise ValueError("Withholding tax rate must be between 0 and 100.")

    tax_rate = withholding_tax_rate_pct / 100

    if tax_rate == 0:
        gross_amount = net_amount
        tax_withheld = 0.0
    else:
        gross_amount = net_amount / (1 - tax_rate)
        tax_withheld = gross_amount - net_amount

    return (
        round(gross_amount, 6),
        round(tax_withheld, 6),
        round(net_amount, 6),
    )
