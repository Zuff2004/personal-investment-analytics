from dataclasses import dataclass

import pandas as pd
import yfinance as yf


@dataclass
class LatestPrice:
    ticker: str
    provider_ticker: str
    date: str
    close_price: float
    currency: str
    source: str = "yfinance"


def normalize_ticker_for_yahoo(ticker: str, country: str = "Brazil") -> str:
    """
    Convert local tickers into Yahoo Finance tickers.

    Examples:
        PETR4 + Brazil -> PETR4.SA
        AAPL + United States -> AAPL
    """
    ticker = ticker.upper().strip()

    if country.lower() == "brazil" and not ticker.endswith(".SA"):
        return f"{ticker}.SA"

    return ticker


def fetch_price_history(
    ticker: str,
    country: str = "Brazil",
    period: str = "1y",
    interval: str = "1d",
) -> pd.DataFrame:
    provider_ticker = normalize_ticker_for_yahoo(ticker, country)

    data = yf.download(
        provider_ticker,
        period=period,
        interval=interval,
        progress=False,
        auto_adjust=False,
    )

    if data.empty:
        raise ValueError(f"No market data found for ticker: {provider_ticker}")

    data = data.reset_index()

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [column[0] for column in data.columns]

    data = data.rename(
        columns={
            "Date": "date",
            "Open": "open_price",
            "High": "high_price",
            "Low": "low_price",
            "Close": "close_price",
            "Volume": "volume",
        }
    )

    data["ticker"] = ticker.upper().replace(".SA", "")
    data["provider_ticker"] = provider_ticker
    data["source"] = "yfinance"

    return data[
        [
            "date",
            "ticker",
            "provider_ticker",
            "open_price",
            "high_price",
            "low_price",
            "close_price",
            "volume",
            "source",
        ]
    ]


def fetch_latest_price(
    ticker: str,
    country: str = "Brazil",
    currency: str = "BRL",
) -> LatestPrice:
    history = fetch_price_history(
        ticker=ticker,
        country=country,
        period="5d",
        interval="1d",
    )

    latest_row = history.dropna(subset=["close_price"]).iloc[-1]

    return LatestPrice(
        ticker=ticker.upper().replace(".SA", ""),
        provider_ticker=str(latest_row["provider_ticker"]),
        date=pd.to_datetime(latest_row["date"]).date().isoformat(),
        close_price=float(latest_row["close_price"]),
        currency=currency,
        source="yfinance",
    )
