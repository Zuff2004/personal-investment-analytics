from dataclasses import dataclass

import pandas as pd

from src.market_data.yahoo_provider import fetch_price_history


@dataclass
class SignalLeg:
    ticker: str
    action: str
    rationale: str


@dataclass
class PairTradingSignal:
    strategy_name: str
    asset_a: str
    asset_b: str
    signal: str
    zscore: float
    ratio: float
    date: str
    legs: list[SignalLeg]
    notes: str


def generate_pair_trading_zscore_signal(
    asset_a: str,
    asset_b: str,
    strategy_name: str = "Pair Trading Z-Score",
    country: str = "Brazil",
    period: str = "1y",
    interval: str = "1d",
    rolling_window: int = 60,
    entry_zscore: float = 2.0,
    exit_zscore: float = 0.5,
) -> PairTradingSignal:
    """
    Generate a pair trading signal using the price ratio z-score.

    Ratio:
        asset_a price / asset_b price

    Interpretation:
        High z-score:
            asset_a is expensive relative to asset_b.
            Signal: SELL/SHORT asset_a, BUY/LONG asset_b.

        Low z-score:
            asset_a is cheap relative to asset_b.
            Signal: BUY/LONG asset_a, SELL/SHORT asset_b.

        Near zero:
            Relative spread normalized.
            Signal: HOLD/CLOSE.
    """
    if rolling_window <= 1:
        raise ValueError("Rolling window must be greater than 1.")

    history_a = fetch_price_history(
        ticker=asset_a,
        country=country,
        period=period,
        interval=interval,
    )

    history_b = fetch_price_history(
        ticker=asset_b,
        country=country,
        period=period,
        interval=interval,
    )

    prices_a = history_a[["date", "close_price"]].rename(
        columns={"close_price": "close_a"}
    )
    prices_b = history_b[["date", "close_price"]].rename(
        columns={"close_price": "close_b"}
    )

    merged = prices_a.merge(prices_b, on="date", how="inner").dropna()

    if len(merged) < rolling_window:
        raise ValueError(
            f"Not enough data for rolling window. "
            f"Rows available: {len(merged)}, rolling window: {rolling_window}"
        )

    merged["ratio"] = merged["close_a"] / merged["close_b"]
    merged["rolling_mean"] = merged["ratio"].rolling(rolling_window).mean()
    merged["rolling_std"] = merged["ratio"].rolling(rolling_window).std()
    merged["zscore"] = (
        merged["ratio"] - merged["rolling_mean"]
    ) / merged["rolling_std"]

    signal_data = merged.dropna(subset=["zscore"]).copy()

    if signal_data.empty:
        raise ValueError("Could not calculate z-score.")

    latest = signal_data.iloc[-1]
    latest_zscore = float(latest["zscore"])
    latest_ratio = float(latest["ratio"])
    latest_date = pd.to_datetime(latest["date"]).date().isoformat()

    asset_a = asset_a.upper().replace(".SA", "")
    asset_b = asset_b.upper().replace(".SA", "")

    if latest_zscore >= entry_zscore:
        signal = "PAIR_TRADE"
        legs = [
            SignalLeg(
                ticker=asset_a,
                action="SELL_OR_SHORT",
                rationale=f"{asset_a} appears expensive relative to {asset_b}.",
            ),
            SignalLeg(
                ticker=asset_b,
                action="BUY_OR_LONG",
                rationale=f"{asset_b} appears cheap relative to {asset_a}.",
            ),
        ]
        notes = (
            f"Ratio z-score is {latest_zscore:.2f}, above entry threshold "
            f"{entry_zscore:.2f}."
        )

    elif latest_zscore <= -entry_zscore:
        signal = "PAIR_TRADE"
        legs = [
            SignalLeg(
                ticker=asset_a,
                action="BUY_OR_LONG",
                rationale=f"{asset_a} appears cheap relative to {asset_b}.",
            ),
            SignalLeg(
                ticker=asset_b,
                action="SELL_OR_SHORT",
                rationale=f"{asset_b} appears expensive relative to {asset_a}.",
            ),
        ]
        notes = (
            f"Ratio z-score is {latest_zscore:.2f}, below negative entry threshold "
            f"-{entry_zscore:.2f}."
        )

    elif abs(latest_zscore) <= exit_zscore:
        signal = "CLOSE_OR_HOLD"
        legs = [
            SignalLeg(
                ticker=asset_a,
                action="HOLD_OR_CLOSE",
                rationale="Spread is close to its historical mean.",
            ),
            SignalLeg(
                ticker=asset_b,
                action="HOLD_OR_CLOSE",
                rationale="Spread is close to its historical mean.",
            ),
        ]
        notes = (
            f"Ratio z-score is {latest_zscore:.2f}, inside exit threshold "
            f"±{exit_zscore:.2f}."
        )

    else:
        signal = "HOLD"
        legs = [
            SignalLeg(
                ticker=asset_a,
                action="HOLD",
                rationale="No entry or exit signal triggered.",
            ),
            SignalLeg(
                ticker=asset_b,
                action="HOLD",
                rationale="No entry or exit signal triggered.",
            ),
        ]
        notes = (
            f"Ratio z-score is {latest_zscore:.2f}. "
            "No actionable threshold was triggered."
        )

    return PairTradingSignal(
        strategy_name=strategy_name,
        asset_a=asset_a,
        asset_b=asset_b,
        signal=signal,
        zscore=round(latest_zscore, 6),
        ratio=round(latest_ratio, 6),
        date=latest_date,
        legs=legs,
        notes=notes,
    )

