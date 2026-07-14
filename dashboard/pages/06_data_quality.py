from pathlib import Path
import sys

import plotly.express as px
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.database.connection import fetch_dataframe, initialize_database
from src.quality.data_quality import run_data_quality_checks, summarize_issues


st.set_page_config(
    page_title="Data Quality",
    page_icon="🧪",
    layout="wide",
)


initialize_database()


st.title("Data Quality")
st.caption(
    "Detect inconsistent transactions, missing prices and data issues before they affect portfolio calculations."
)


issues = run_data_quality_checks()
summary = summarize_issues(issues)


st.subheader("Quality Summary")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Issues", summary["total"])
col2.metric("Errors", summary["errors"])
col3.metric("Warnings", summary["warnings"])
col4.metric("Info", summary["info"])


st.divider()


if issues.empty:
    st.success("No data quality issues found.")
else:
    st.subheader("Detected Issues")

    severity_filter = st.multiselect(
        "Severity",
        options=["ERROR", "WARNING", "INFO"],
        default=["ERROR", "WARNING", "INFO"],
    )

    filtered = issues[issues["severity"].isin(severity_filter)].copy()

    st.dataframe(filtered, width="stretch")

    st.subheader("Issues by Category")

    category_counts = (
        filtered.groupby(["severity", "category"])
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )

    if not category_counts.empty:
        fig = px.bar(
            category_counts,
            x="category",
            y="count",
            color="severity",
            title="Data Quality Issues by Category",
            text_auto=True,
        )

        st.plotly_chart(fig, width="stretch")

    st.info(
        "ERROR issues should be fixed before relying on portfolio calculations. "
        "WARNING issues may be acceptable depending on the situation."
    )


st.divider()


st.subheader("Recent Buy/Sell Transactions")

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
    WHERE t.transaction_type IN ('BUY', 'SELL')
    ORDER BY t.date DESC, t.transaction_id DESC
    LIMIT 100
    """
)

st.dataframe(transactions, width="stretch")


st.subheader("Latest Market Prices")

prices = fetch_dataframe(
    """
    SELECT
        p.price_id,
        p.date,
        a.ticker,
        p.close_price,
        p.currency,
        p.source,
        p.retrieved_at
    FROM market_prices p
    LEFT JOIN assets a ON p.asset_id = a.asset_id
    ORDER BY p.date DESC, p.price_id DESC
    LIMIT 100
    """
)

st.dataframe(prices, width="stretch")
