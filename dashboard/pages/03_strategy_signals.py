from datetime import date
from pathlib import Path
import sys

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.database.connection import fetch_dataframe, initialize_database
from src.database.signal_entries import save_multi_leg_signal
from src.strategies.pair_trading_zscore import generate_pair_trading_zscore_signal


st.set_page_config(
    page_title="Strategy Signals",
    page_icon="🧠",
    layout="wide",
)


initialize_database()


st.title("Strategy Signals")
st.caption(
    "Generate current signals from configured strategies. "
    "The first supported strategy is pair trading based on price-ratio z-score."
)


tab_pair, tab_saved = st.tabs(["Pair Trading Z-Score", "Saved Signals"])


with tab_pair:
    st.subheader("Generate Pair Trading Signal")

    with st.form("pair_trading_form"):
        col1, col2, col3 = st.columns(3)

        asset_a = col1.text_input("Asset A", placeholder="PETR3").upper()
        asset_b = col2.text_input("Asset B", placeholder="PETR4").upper()
        strategy_name = col3.text_input(
            "Strategy Name",
            value="Pair Trading Z-Score",
        )

        col4, col5, col6 = st.columns(3)

        country = col4.selectbox("Country", ["Brazil", "United States", "Germany", "Other"])
        period = col5.selectbox("Period", ["6mo", "1y", "2y", "5y"], index=1)
        rolling_window = col6.number_input(
            "Rolling Window",
            min_value=20,
            max_value=252,
            value=60,
            step=5,
        )

        col7, col8, col9 = st.columns(3)

        entry_zscore = col7.number_input(
            "Entry Z-Score",
            min_value=0.5,
            max_value=5.0,
            value=2.0,
            step=0.1,
        )
        exit_zscore = col8.number_input(
            "Exit Z-Score",
            min_value=0.0,
            max_value=2.0,
            value=0.5,
            step=0.1,
        )
        save_signal = col9.checkbox("Save generated signal", value=True)

        submitted = st.form_submit_button("Generate Signal")

        if submitted:
            if not asset_a or not asset_b:
                st.error("Both assets are required.")
            elif asset_a == asset_b:
                st.error("Asset A and Asset B must be different.")
            else:
                try:
                    generated_signal = generate_pair_trading_zscore_signal(
                        asset_a=asset_a,
                        asset_b=asset_b,
                        strategy_name=strategy_name,
                        country=country,
                        period=period,
                        rolling_window=int(rolling_window),
                        entry_zscore=float(entry_zscore),
                        exit_zscore=float(exit_zscore),
                    )

                    st.success("Signal generated successfully.")

                    col_a, col_b, col_c = st.columns(3)

                    col_a.metric("Signal", generated_signal.signal)
                    col_b.metric("Z-Score", f"{generated_signal.zscore:.2f}")
                    col_c.metric("Ratio", f"{generated_signal.ratio:.4f}")

                    st.write(
                        {
                            "date": generated_signal.date,
                            "strategy": generated_signal.strategy_name,
                            "asset_a": generated_signal.asset_a,
                            "asset_b": generated_signal.asset_b,
                            "notes": generated_signal.notes,
                        }
                    )

                    legs_df = pd.DataFrame(
                        [
                            {
                                "ticker": leg.ticker,
                                "action": leg.action,
                                "rationale": leg.rationale,
                            }
                            for leg in generated_signal.legs
                        ]
                    )

                    st.subheader("Signal Legs")
                    st.dataframe(legs_df, width="stretch")

                    if save_signal:
                        signal_id = save_multi_leg_signal(
                            signal_date=date.fromisoformat(generated_signal.date),
                            strategy_name=generated_signal.strategy_name,
                            signal=generated_signal.signal,
                            signal_strength=abs(generated_signal.zscore),
                            suggested_action=generated_signal.signal,
                            legs=[
                                {
                                    "ticker": leg.ticker,
                                    "action": leg.action,
                                    "score": generated_signal.zscore,
                                    "notes": leg.rationale,
                                }
                                for leg in generated_signal.legs
                            ],
                            notes=generated_signal.notes,
                        )

                        st.info(f"Signal saved to database. Signal ID: {signal_id}")

                except Exception as error:
                    st.error(f"Could not generate signal: {error}")


with tab_saved:
    st.subheader("Saved Signals")

    signals = fetch_dataframe(
        """
        SELECT
            s.signal_id,
            s.date,
            st.name AS strategy,
            a.ticker AS primary_ticker,
            s.signal,
            s.signal_strength,
            s.suggested_action,
            s.executed,
            s.notes
        FROM signals s
        LEFT JOIN strategies st ON s.strategy_id = st.strategy_id
        LEFT JOIN assets a ON s.asset_id = a.asset_id
        ORDER BY s.date DESC, s.signal_id DESC
        LIMIT 100
        """
    )

    st.dataframe(signals, width="stretch")

    st.subheader("Saved Signal Legs")

    signal_legs = fetch_dataframe(
        """
        SELECT
            sl.signal_leg_id,
            sl.signal_id,
            a.ticker,
            sl.leg_action,
            sl.target_weight,
            sl.suggested_quantity,
            sl.suggested_price,
            sl.score,
            sl.notes
        FROM signal_legs sl
        LEFT JOIN assets a ON sl.asset_id = a.asset_id
        ORDER BY sl.signal_id DESC, sl.signal_leg_id ASC
        LIMIT 200
        """
    )

    st.dataframe(signal_legs, width="stretch")
