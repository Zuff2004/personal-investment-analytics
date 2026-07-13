from datetime import date
from pathlib import Path
import sys

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.database.connection import fetch_dataframe, initialize_database
from src.database.manual_entries import (
    add_income_event,
    add_market_price,
    add_strategy,
    add_transaction,
)


st.set_page_config(
    page_title="Manual Entry",
    page_icon="✍️",
    layout="wide",
)


initialize_database()


st.title("Manual Entry")
st.caption(
    "Enter real investment events manually. The system calculates derived values "
    "such as gross value, estimated costs, net value and later portfolio analytics."
)


tab_transaction, tab_income, tab_price, tab_strategy, tab_recent = st.tabs(
    [
        "Add Transaction",
        "Add Income",
        "Add Market Price",
        "Add Strategy",
        "Recent Entries",
    ]
)


with tab_transaction:
    st.subheader("Add Buy/Sell Transaction")

    with st.form("transaction_form"):
        col1, col2, col3 = st.columns(3)

        transaction_date = col1.date_input("Date", value=date.today())
        transaction_type = col2.selectbox("Transaction Type", ["BUY", "SELL"])
        ticker = col3.text_input("Ticker", placeholder="PETR4").upper()

        col4, col5, col6 = st.columns(3)

        asset_type = col4.selectbox(
            "Asset Type",
            ["Stock", "ETF", "Fund", "Crypto", "Bond", "Other"],
        )
        quantity = col5.number_input("Quantity", min_value=0.0, step=1.0)
        price = col6.number_input("Price", min_value=0.0, step=0.01)

        col7, col8, col9 = st.columns(3)

        broker_name = col7.text_input("Broker", value="Manual Broker")
        account_name = col8.text_input("Account", value="Main Account")
        currency = col9.selectbox("Currency", ["BRL", "USD", "EUR"])

        with st.expander("Cost assumptions"):
            c1, c2 = st.columns(2)
            fee_rate_pct = c1.number_input(
                "Estimated fee rate (%)",
                min_value=0.0,
                step=0.001,
                format="%.4f",
            )
            tax_rate_pct = c2.number_input(
                "Estimated transaction tax rate (%)",
                min_value=0.0,
                step=0.001,
                format="%.4f",
            )

        strategy_name = st.text_input(
            "Strategy, optional",
            placeholder="Manual Value Trade",
        )
        notes = st.text_area("Notes", placeholder="Why did you make this transaction?")

        submitted = st.form_submit_button("Save Transaction")

        if submitted:
            if not ticker:
                st.error("Ticker is required.")
            elif quantity <= 0 or price <= 0:
                st.error("Quantity and price must be positive.")
            else:
                transaction_id = add_transaction(
                    transaction_date=transaction_date,
                    ticker=ticker,
                    asset_type=asset_type,
                    transaction_type=transaction_type,
                    quantity=quantity,
                    price=price,
                    broker_name=broker_name,
                    account_name=account_name,
                    currency=currency,
                    fee_rate_pct=fee_rate_pct,
                    tax_rate_pct=tax_rate_pct,
                    strategy_name=strategy_name or None,
                    notes=notes or None,
                )

                st.success(f"Transaction saved successfully. ID: {transaction_id}")


with tab_income:
    st.subheader("Add Income Event")

    with st.form("income_form"):
        col1, col2, col3 = st.columns(3)

        income_date = col1.date_input("Income Date", value=date.today())
        income_type = col2.selectbox(
            "Income Type",
            ["DIVIDEND", "JCP", "STOCK_LENDING", "INTEREST", "COUPON"],
        )
        ticker = col3.text_input("Income Ticker", placeholder="ITUB4").upper()

        col4, col5, col6 = st.columns(3)

        asset_type = col4.selectbox(
            "Income Asset Type",
            ["Stock", "ETF", "Fund", "Bond", "Other"],
        )
        net_amount = col5.number_input(
            "Net Amount Received",
            min_value=0.0,
            step=0.01,
        )
        withholding_tax_rate_pct = col6.number_input(
            "Withholding Tax Rate (%)",
            min_value=0.0,
            max_value=99.99,
            step=0.01,
        )

        col7, col8, col9 = st.columns(3)

        broker_name = col7.text_input("Income Broker", value="Manual Broker")
        account_name = col8.text_input("Income Account", value="Main Account")
        currency = col9.selectbox("Income Currency", ["BRL", "USD", "EUR"])

        related_quantity = st.number_input(
            "Related Quantity, optional",
            min_value=0.0,
            step=1.0,
        )
        notes = st.text_area("Income Notes")

        submitted = st.form_submit_button("Save Income Event")

        if submitted:
            if not ticker:
                st.error("Ticker is required.")
            elif net_amount <= 0:
                st.error("Net amount must be positive.")
            else:
                income_id = add_income_event(
                    income_date=income_date,
                    ticker=ticker,
                    asset_type=asset_type,
                    income_type=income_type,
                    net_amount=net_amount,
                    broker_name=broker_name,
                    account_name=account_name,
                    currency=currency,
                    withholding_tax_rate_pct=withholding_tax_rate_pct,
                    related_quantity=related_quantity if related_quantity > 0 else None,
                    notes=notes or None,
                )

                st.success(f"Income event saved successfully. ID: {income_id}")


with tab_price:
    st.subheader("Add Manual Market Price")

    with st.form("price_form"):
        col1, col2, col3 = st.columns(3)

        price_date = col1.date_input("Price Date", value=date.today())
        ticker = col2.text_input("Price Ticker", placeholder="PETR4").upper()
        close_price = col3.number_input("Close Price", min_value=0.0, step=0.01)

        col4, col5, col6 = st.columns(3)

        asset_type = col4.selectbox(
            "Price Asset Type",
            ["Stock", "ETF", "Fund", "Crypto", "Bond", "Other"],
        )
        currency = col5.selectbox("Price Currency", ["BRL", "USD", "EUR"])
        source = col6.text_input("Source", value="manual")

        submitted = st.form_submit_button("Save Market Price")

        if submitted:
            if not ticker:
                st.error("Ticker is required.")
            elif close_price <= 0:
                st.error("Close price must be positive.")
            else:
                price_id = add_market_price(
                    price_date=price_date,
                    ticker=ticker,
                    asset_type=asset_type,
                    close_price=close_price,
                    currency=currency,
                    source=source,
                )

                st.success(f"Market price saved successfully. ID: {price_id}")


with tab_strategy:
    st.subheader("Add Strategy")

    with st.form("strategy_form"):
        name = st.text_input("Strategy Name", placeholder="ON/PN Relative Value")
        strategy_type = st.selectbox(
            "Strategy Type",
            [
                "Manual",
                "Momentum",
                "Mean Reversion",
                "Dividend",
                "Z-Score",
                "Relative Value",
                "Other",
            ],
        )
        asset_universe = st.text_input(
            "Asset Universe",
            placeholder="Brazilian equities, ON/PN pairs, ETFs...",
        )
        description = st.text_area("Description")

        submitted = st.form_submit_button("Save Strategy")

        if submitted:
            if not name:
                st.error("Strategy name is required.")
            else:
                strategy_id = add_strategy(
                    name=name,
                    description=description or None,
                    strategy_type=strategy_type,
                    asset_universe=asset_universe or None,
                )

                st.success(f"Strategy saved successfully. ID: {strategy_id}")


with tab_recent:
    st.subheader("Recent Transactions")

    transactions = fetch_dataframe(
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
        ORDER BY t.date DESC, t.transaction_id DESC
        LIMIT 20
        """
    )

    st.dataframe(transactions, width="stretch")

    st.subheader("Recent Income Events")

    income = fetch_dataframe(
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
        ORDER BY i.date DESC, i.income_id DESC
        LIMIT 20
        """
    )

    st.dataframe(income, width="stretch")

    st.subheader("Recent Market Prices")

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
        LIMIT 20
        """
    )

    st.dataframe(prices, width="stretch")

    st.subheader("Strategies")

    strategies = fetch_dataframe(
        """
        SELECT
            strategy_id,
            name,
            strategy_type,
            asset_universe,
            active,
            created_at,
            description
        FROM strategies
        ORDER BY strategy_id DESC
        """
    )

    st.dataframe(strategies, width="stretch")
