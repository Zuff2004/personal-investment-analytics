from pathlib import Path
import sys

import plotly.express as px
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.database.connection import fetch_dataframe, initialize_database
from src.market_data.market_data_service import update_prices_for_tracked_assets
from src.portfolio.positions import calculate_positions_from_database


st.set_page_config(
    page_title="Portfolio",
    page_icon="📊",
    layout="wide",
)


initialize_database()


st.title("Portfolio")
st.caption(
    "Portfolio positions, average cost, realized PnL, unrealized PnL and income summary."
)


with st.spinner("Checking market prices..."):
    update_result = update_prices_for_tracked_assets(max_age_hours=12)

if update_result["updated"]:
    updated_tickers = [item["ticker"] for item in update_result["updated"]]
    st.success(
        f"Updated prices for {len(updated_tickers)} asset(s): "
        f"{', '.join(updated_tickers)}"
    )

if update_result["errors"]:
    st.warning("Some prices could not be updated.")
    st.dataframe(update_result["errors"], width="stretch")


try:
    positions, income_summary, summary = calculate_positions_from_database()

except ValueError as error:
    st.error("Portfolio calculation could not be completed because some transactions are inconsistent.")

    st.warning(str(error))

    st.markdown(
        """
        This usually happens when there is a SELL transaction without a previous BUY transaction
        for the same asset, or when the sold quantity is larger than the current position.

        To fix it, check whether:
        - the original BUY transaction was entered;
        - the ticker was typed correctly;
        - the sale quantity is correct;
        - the transaction dates are correct;
        - the asset was transferred from another broker and needs an initial position entry.
        """
    )

    st.subheader("Recent Buy/Sell Transactions")

    recent_transactions = fetch_dataframe(
        """
        SELECT
            t.transaction_id,
            t.date,
            a.ticker,
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
        ORDER BY t.date DESC, t.transaction_id DESC
        LIMIT 50
        """
    )

    st.dataframe(recent_transactions, width="stretch")

    st.stop()


st.subheader("Portfolio Summary")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Market Value", f"R$ {summary['total_market_value']:,.2f}")
col2.metric("Cost Basis", f"R$ {summary['total_cost_basis']:,.2f}")
col3.metric("Total PnL", f"R$ {summary['total_pnl']:,.2f}")
col4.metric("Total Return", f"{summary['total_return_pct']:,.2f}%")

col5, col6, col7 = st.columns(3)

col5.metric("Realized PnL", f"R$ {summary['total_realized_pnl']:,.2f}")
col6.metric("Unrealized PnL", f"R$ {summary['total_unrealized_pnl']:,.2f}")
col7.metric("Income", f"R$ {summary['total_income']:,.2f}")


st.divider()


if positions.empty:
    st.info(
        "No transactions available yet. Add transactions in Manual Entry. "
        "When you open this page, prices for tracked assets will be updated automatically."
    )
else:
    st.subheader("Current Positions")

    st.dataframe(positions, width="stretch")

    missing_prices = positions[positions["latest_price"].isna()]

    if not missing_prices.empty:
        st.warning(
            "Some assets do not have market prices yet. You can force an update in the Market Data page."
        )
        st.dataframe(missing_prices[["ticker", "quantity"]], width="stretch")

    st.subheader("Portfolio Charts")

    chart_positions = positions.dropna(subset=["market_value"]).copy()

    if not chart_positions.empty:
        col_a, col_b = st.columns(2)

        fig_allocation = px.pie(
            chart_positions,
            names="ticker",
            values="market_value",
            title="Allocation by Market Value",
        )
        col_a.plotly_chart(fig_allocation, width="stretch")

        fig_unrealized = px.bar(
            chart_positions,
            x="ticker",
            y="unrealized_pnl",
            title="Unrealized PnL by Asset",
            text_auto=".2f",
        )
        col_b.plotly_chart(fig_unrealized, width="stretch")

        fig_return = px.bar(
            chart_positions,
            x="ticker",
            y="unrealized_return_pct",
            title="Unrealized Return by Asset (%)",
            text_auto=".2f",
        )
        st.plotly_chart(fig_return, width="stretch")


st.divider()


st.subheader("Income Summary")

if income_summary.empty:
    st.info("No income events available yet.")
else:
    st.dataframe(income_summary, width="stretch")

    fig_income = px.bar(
        income_summary,
        x="ticker",
        y="total_net_income",
        title="Net Income by Asset",
        text_auto=".2f",
    )
    st.plotly_chart(fig_income, width="stretch")
