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
        price_date=__import__("datetime").date.fromisoformat(latest_price.date),
        ticker=latest_price.ticker,
        asset_type=asset_type,
        close_price=latest_price.close_price,
        currency=latest_price.currency,
        source=latest_price.source,
    )

    return price_id
