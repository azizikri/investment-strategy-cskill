"""Data fetchers for live market data from Yahoo Finance, CoinGecko, and FX APIs."""

from scripts.data_fetchers.crypto_fetcher import (
    COMMON_CRYPTOS,
    get_crypto_history,
    get_crypto_list,
    get_crypto_price,
    get_crypto_prices_batch,
)
from scripts.data_fetchers.fx_fetcher import (
    convert_idr_to_usd,
    convert_usd_to_idr,
    get_exchange_rate,
    get_usd_idr_rate,
)
from scripts.data_fetchers.stock_fetcher import (
    get_stock_history,
    get_stock_info,
    get_stock_price,
    get_stock_prices_batch,
)

__all__ = [
    "get_stock_price",
    "get_stock_prices_batch",
    "get_stock_history",
    "get_stock_info",
    "get_crypto_price",
    "get_crypto_prices_batch",
    "get_crypto_history",
    "get_crypto_list",
    "COMMON_CRYPTOS",
    "get_usd_idr_rate",
    "get_exchange_rate",
    "convert_usd_to_idr",
    "convert_idr_to_usd",
]
