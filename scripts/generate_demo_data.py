from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEMO_DATA_DIR = PROJECT_ROOT / "demo_data"


def generate_demo_transactions() -> pd.DataFrame:
    data = [
        {
            "date": "2024-01-10",
            "account": "Demo Broker",
            "ticker": "PETR4",
            "asset_type": "Stock",
            "transaction_type": "BUY",
            "quantity": 100,
            "price": 32.50,
            "fees": 2.50,
            "taxes": 0.00,
            "currency": "BRL",
            "strategy": "Manual Value Trade",
            "notes": "Initial demo position",
        },
        {
            "date": "2024-02-15",
            "account": "Demo Broker",
            "ticker": "ITUB4",
            "asset_type": "Stock",
            "transaction_type": "BUY",
            "quantity": 80,
            "price": 28.10,
            "fees": 2.00,
            "taxes": 0.00,
            "currency": "BRL",
            "strategy": "Dividend Strategy",
            "notes": "Demo dividend-oriented purchase",
        },
        {
            "date": "2024-03-20",
            "account": "Demo Broker",
            "ticker": "PETR4",
            "asset_type": "Stock",
            "transaction_type": "SELL",
            "quantity": 40,
            "price": 36.20,
            "fees": 2.20,
            "taxes": 0.00,
            "currency": "BRL",
            "strategy": "Manual Value Trade",
            "notes": "Partial profit-taking demo trade",
        },
        {
            "date": "2024-04-05",
            "account": "Demo Broker",
            "ticker": "ITUB4",
            "asset_type": "Stock",
            "transaction_type": "DIVIDEND",
            "quantity": 80,
            "price": 0.35,
            "fees": 0.00,
            "taxes": 0.00,
            "currency": "BRL",
            "strategy": "Dividend Strategy",
            "notes": "Demo dividend income",
        },
        {
            "date": "2024-05-12",
            "account": "Demo Broker",
            "ticker": "BOVA11",
            "asset_type": "ETF",
            "transaction_type": "BUY",
            "quantity": 20,
            "price": 124.30,
            "fees": 1.80,
            "taxes": 0.00,
            "currency": "BRL",
            "strategy": "Benchmark Allocation",
            "notes": "Demo ETF allocation",
        },
        {
            "date": "2024-06-18",
            "account": "Demo Broker",
            "ticker": "PETR4",
            "asset_type": "Stock",
            "transaction_type": "STOCK_LENDING",
            "quantity": 60,
            "price": 0.12,
            "fees": 0.00,
            "taxes": 0.00,
            "currency": "BRL",
            "strategy": "Manual Value Trade",
            "notes": "Demo stock lending income",
        },
    ]

    return pd.DataFrame(data)


def generate_demo_prices() -> pd.DataFrame:
    data = [
        {"date": "2024-06-30", "ticker": "PETR4", "close_price": 37.10, "currency": "BRL"},
        {"date": "2024-06-30", "ticker": "ITUB4", "close_price": 31.40, "currency": "BRL"},
        {"date": "2024-06-30", "ticker": "BOVA11", "close_price": 129.80, "currency": "BRL"},
    ]

    return pd.DataFrame(data)


def main() -> None:
    DEMO_DATA_DIR.mkdir(parents=True, exist_ok=True)

    transactions = generate_demo_transactions()
    prices = generate_demo_prices()

    transactions.to_csv(DEMO_DATA_DIR / "sample_transactions.csv", index=False)
    prices.to_csv(DEMO_DATA_DIR / "sample_prices.csv", index=False)

    print("Demo data generated successfully.")
    print(f"Transactions: {DEMO_DATA_DIR / 'sample_transactions.csv'}")
    print(f"Prices: {DEMO_DATA_DIR / 'sample_prices.csv'}")


if __name__ == "__main__":
    main()
