from pathlib import Path

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEMO_TRANSACTIONS_PATH = PROJECT_ROOT / "demo_data" / "sample_transactions.csv"
DEMO_PRICES_PATH = PROJECT_ROOT / "demo_data" / "sample_prices.csv"


st.set_page_config(
    page_title="Personal Investment Analytics",
    page_icon="📈",
    layout="wide",
)


@st.cache_data
def load_demo_transactions() -> pd.DataFrame:
    return pd.read_csv(DEMO_TRANSACTIONS_PATH, parse_dates=["date"])


@st.cache_data
def load_demo_prices() -> pd.DataFrame:
    return pd.read_csv(DEMO_PRICES_PATH, parse_dates=["date"])


def calculate_basic_metrics(transactions: pd.DataFrame) -> dict:
    buys = transactions[transactions["transaction_type"] == "BUY"].copy()
    sells = transactions[transactions["transaction_type"] == "SELL"].copy()
    dividends = transactions[transactions["transaction_type"] == "DIVIDEND"].copy()
    stock_lending = transactions[transactions["transaction_type"] == "STOCK_LENDING"].copy()

    invested_capital = (buys["quantity"] * buys["price"] + buys["fees"]).sum()
    sell_proceeds = (sells["quantity"] * sells["price"] - sells["fees"]).sum()
    dividend_income = (dividends["quantity"] * dividends["price"]).sum()
    stock_lending_income = (stock_lending["quantity"] * stock_lending["price"]).sum()
    total_fees = transactions["fees"].sum()

    return {
        "invested_capital": invested_capital,
        "sell_proceeds": sell_proceeds,
        "dividend_income": dividend_income,
        "stock_lending_income": stock_lending_income,
        "total_fees": total_fees,
    }


def calculate_demo_positions(transactions: pd.DataFrame, prices: pd.DataFrame) -> pd.DataFrame:
    buys = transactions[transactions["transaction_type"] == "BUY"].copy()
    sells = transactions[transactions["transaction_type"] == "SELL"].copy()

    buy_qty = buys.groupby("ticker")["quantity"].sum()
    sell_qty = sells.groupby("ticker")["quantity"].sum()

    positions = pd.DataFrame({
        "quantity": buy_qty.sub(sell_qty, fill_value=0)
    }).reset_index()

    buy_cost = buys.assign(total_cost=buys["quantity"] * buys["price"] + buys["fees"])
    cost_basis = buy_cost.groupby("ticker")["total_cost"].sum().reset_index()

    positions = positions.merge(cost_basis, on="ticker", how="left")
    positions = positions.merge(prices[["ticker", "close_price"]], on="ticker", how="left")

    positions["average_cost_demo"] = positions["total_cost"] / positions["quantity"]
    positions["market_value"] = positions["quantity"] * positions["close_price"]
    positions["unrealized_pnl_demo"] = positions["market_value"] - positions["total_cost"]

    return positions


def main() -> None:
    st.title("Personal Investment Analytics & Strategy Platform")
    st.caption(
        "Local Python-based platform for portfolio tracking, tax-aware analytics, "
        "signal generation, backtesting and automated reporting."
    )

    transactions = load_demo_transactions()
    prices = load_demo_prices()

    metrics = calculate_basic_metrics(transactions)
    positions = calculate_demo_positions(transactions, prices)

    st.subheader("Demo Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Invested Capital", f"R$ {metrics['invested_capital']:,.2f}")
    col2.metric("Sell Proceeds", f"R$ {metrics['sell_proceeds']:,.2f}")
    col3.metric("Dividend Income", f"R$ {metrics['dividend_income']:,.2f}")
    col4.metric("Stock Lending Income", f"R$ {metrics['stock_lending_income']:,.2f}")

    st.divider()

    st.subheader("Current Demo Positions")
    st.dataframe(positions, use_container_width=True)

    st.subheader("Demo Transactions")
    st.dataframe(transactions, use_container_width=True)

    st.subheader("Demo Prices")
    st.dataframe(prices, use_container_width=True)

    st.info(
        "This dashboard uses fictitious demo data. Real financial data should remain local "
        "and must not be committed to GitHub."
    )


if __name__ == "__main__":
    main()
