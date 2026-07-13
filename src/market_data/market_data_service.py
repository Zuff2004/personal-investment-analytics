from datetime import date, datetime, timedelta

from src.database.connection import fetch_dataframe
from src.database.manual_entries import add_market_price
from src.market_data.yahoo_provider import fetch_latest_price


def fetch_and_save_latest_price(
    ticker: str,
    asset_type: str = "Stock",
    country: str = "Brazil",
    currency: str = "BRL",
) -> int:
    latest_price = fetch_latest_price(
        ticker=ticker,
        country=country,
        currency=currency,
    )

    price_id = add_market_price(
        price_date=date.fromisoformat(latest_price.date),
        ticker=latest_price.ticker,
        asset_type=asset_type,
        close_price=latest_price.close_price,
        currency=latest_price.currency,
        source=latest_price.source,
    )

    return price_id


def fetch_tracked_assets() -> list[dict]:
    """
    Fetch assets that are currently relevant for the portfolio.

    For now, tracked assets are assets that appear in transactions.
    Later, we can also include assets from strategies, watchlists and open signals.
    """
    assets = fetch_dataframe(
        """
        SELECT DISTINCT
            a.ticker,
            a.asset_type,
            a.currency,
            COALESCE(a.country, 'Brazil') AS country
        FROM transactions t
        LEFT JOIN assets a ON t.asset_id = a.asset_id
        WHERE a.ticker IS NOT NULL
        ORDER BY a.ticker
        """
    )

    return assets.to_dict("records")


def get_last_retrieved_at(ticker: str, source: str = "yfinance") -> datetime | None:
    result = fetch_dataframe(
        """
        SELECT
            p.retrieved_at
        FROM market_prices p
        LEFT JOIN assets a ON p.asset_id = a.asset_id
        WHERE a.ticker = ?
          AND p.source = ?
          AND p.retrieved_at IS NOT NULL
        ORDER BY p.retrieved_at DESC
        LIMIT 1
        """,
        params=(ticker.upper(), source),
    )

    if result.empty:
        return None

    retrieved_at = result.iloc[0]["retrieved_at"]

    if retrieved_at is None:
        return None

    return datetime.fromisoformat(str(retrieved_at))


def should_update_price(
    ticker: str,
    source: str = "yfinance",
    max_age_hours: int = 12,
) -> bool:
    last_retrieved_at = get_last_retrieved_at(ticker=ticker, source=source)

    if last_retrieved_at is None:
        return True

    return datetime.now() - last_retrieved_at > timedelta(hours=max_age_hours)


def update_prices_for_tracked_assets(
    max_age_hours: int = 12,
) -> dict:
    """
    Automatically update latest prices for all tracked assets.

    It only fetches prices when the last retrieval is older than max_age_hours.
    This avoids unnecessary internet calls on every Streamlit rerun.
    """
    tracked_assets = fetch_tracked_assets()

    result = {
        "tracked_assets": len(tracked_assets),
        "updated": [],
        "skipped": [],
        "errors": [],
    }

    for asset in tracked_assets:
        ticker = asset["ticker"]
        asset_type = asset.get("asset_type") or "Stock"
        country = asset.get("country") or "Brazil"
        currency = asset.get("currency") or "BRL"

        try:
            if not should_update_price(
                ticker=ticker,
                source="yfinance",
                max_age_hours=max_age_hours,
            ):
                result["skipped"].append(ticker)
                continue

            price_id = fetch_and_save_latest_price(
                ticker=ticker,
                asset_type=asset_type,
                country=country,
                currency=currency,
            )

            result["updated"].append(
                {
                    "ticker": ticker,
                    "price_id": price_id,
                }
            )

        except Exception as error:
            result["errors"].append(
                {
                    "ticker": ticker,
                    "error": str(error),
                }
            )

    return result
