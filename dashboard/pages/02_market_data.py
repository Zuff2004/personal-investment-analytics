from pathlib import Path
import sys

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.database.connection import fetch_dataframe, initialize_database
from src.market_data.yahoo_provider import fetch_latest_price, fetch_price_history
from src.market_data.market_data_service import fetch_and_save_latest_price


st.set_page_config(
    page_title="Market Data",
    page_icon="🌎",
    layout="wide",
)


initialize_database()


st.title("Market Data")
st.caption(
    "Fetch latest and historical market prices automatically. Manual prices should be used only as fallback or override."
)


tab_latest, tab_history, tab_saved = st.tabs(
    ["Latest Price", "Price History", "Saved Prices"]
)


with tab_latest:
    st.subheader("Fetch Latest Price")

    with st.form("latest_price_form"):
        col1, col2, col3, col4 = st.columns(4)

        ticker = col1.text_input("Ticker", placeholder="PETR4").upper()
        country = col2.selectbox("Country", ["Brazil", "United States", "Germany", "Other"])
        currency = col3.selectbox("Currency", ["BRL", "USD", "EUR"])
        asset_type = col4.selectbox("Asset Type", ["Stock", "ETF", "Fund", "Crypto", "Bond", "Other"])

        submitted = st.form_submit_button("Fetch Latest Price")

        if submitted:
            if not ticker:
                st.error("Ticker is required.")
            else:
                try:
                    latest = fetch_latest_price(
                        ticker=ticker,
                        country=country,
                        currency=currency,
                    )

                    st.success("Latest price fetched successfully.")

                    st.write(
                        {
                            "ticker": latest.ticker,
                            "provider_ticker": latest.provider_ticker,
                            "date": latest.date,
                            "close_price": latest.close_price,
                            "currency": latest.currency,
                            "source": latest.source,
                        }
                    )

                    price_id = fetch_and_save_latest_price(
                        ticker=ticker,
                        asset_type=asset_type,
                        country=country,
                        currency=currency,
                    )

                    st.info(f"Latest price saved to database. Price ID: {price_id}")

                except Exception as error:
                    st.error(f"Could not fetch latest price: {error}")


with tab_history:
    st.subheader("Fetch Price History")

    with st.form("history_form"):
        col1, col2, col3, col4 = st.columns(4)

        ticker = col1.text_input("History Ticker", placeholder="PETR4").upper()
        country = col2.selectbox(
            "History Country",
            ["Brazil", "United States", "Germany", "Other"],
        )
        period = col3.selectbox(
            "Period",
            ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"],
            index=3,
        )
        interval = col4.selectbox(
            "Interval",
            ["1d", "1wk", "1mo"],
            index=0,
        )

        submitted = st.form_submit_button("Fetch History")

        if submitted:
            if not ticker:
                st.error("Ticker is required.")
            else:
                try:
                    history = fetch_price_history(
                        ticker=ticker,
                        country=country,
                        period=period,
                        interval=interval,
                    )

                    st.success("Price history fetched successfully.")
                    st.dataframe(history.tail(100), width="stretch")

                    chart_data = history[["date", "close_price"]].copy()
                    chart_data = chart_data.set_index("date")

                    st.line_chart(chart_data, width="stretch")

                except Exception as error:
                    st.error(f"Could not fetch price history: {error}")


with tab_saved:
    st.subheader("Saved Market Prices")

    prices = fetch_dataframe(
        """
        SELECT
            p.price_id,
            p.date,
            a.ticker,
            p.close_price,
            p.currency,
            p.source
        FROM market_prices p
        LEFT JOIN assets a ON p.asset_id = a.asset_id
        ORDER BY p.date DESC, p.price_id DESC
        LIMIT 100
        """
    )

    st.dataframe(prices, width="stretch")
