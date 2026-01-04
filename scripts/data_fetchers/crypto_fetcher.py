"""CoinGecko cryptocurrency data fetcher.

This module provides functions to fetch real-time cryptocurrency prices
using the CoinGecko API (free tier, no API key required).

Rate limits: 30 calls/minute for free tier.

Example:
    >>> from scripts.data_fetchers.crypto_fetcher import get_crypto_price
    >>> price = get_crypto_price("bitcoin")
    >>> print(price)
    {'id': 'bitcoin', 'symbol': 'BTC', 'price_usd': 98000.50, ...}
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

import requests

__all__ = [
    "get_crypto_price",
    "get_crypto_prices_batch",
    "get_crypto_history",
    "get_crypto_list",
    "COMMON_CRYPTOS",
]

logger = logging.getLogger(__name__)

# CoinGecko API base URL (free tier)
COINGECKO_API_BASE = "https://api.coingecko.com/api/v3"

# Common crypto ID mappings (symbol -> coingecko id)
COMMON_CRYPTOS: dict[str, str] = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "BNB": "binancecoin",
    "SOL": "solana",
    "XRP": "ripple",
    "ADA": "cardano",
    "DOGE": "dogecoin",
    "DOT": "polkadot",
    "MATIC": "matic-network",
    "SHIB": "shiba-inu",
    "AVAX": "avalanche-2",
    "LINK": "chainlink",
    "UNI": "uniswap",
    "ATOM": "cosmos",
    "LTC": "litecoin",
}

# Cache for API responses
_cache: dict[str, tuple[Any, datetime]] = {}
CACHE_TTL_SECONDS: int = 60  # 1 minute for crypto (more volatile)

# Request timeout
REQUEST_TIMEOUT: int = 10


def _get_cached(key: str) -> Any | None:
    """Retrieve cached value if not expired."""
    if key in _cache:
        value, timestamp = _cache[key]
        if datetime.now() - timestamp < timedelta(seconds=CACHE_TTL_SECONDS):
            return value
        del _cache[key]
    return None


def _set_cached(key: str, value: Any) -> None:
    """Store value in cache with current timestamp."""
    _cache[key] = (value, datetime.now())


def _symbol_to_id(symbol: str) -> str:
    """Convert a crypto symbol to CoinGecko ID.

    Args:
        symbol: Crypto symbol (e.g., "BTC", "ETH") or CoinGecko ID.

    Returns:
        CoinGecko ID (e.g., "bitcoin", "ethereum").
    """
    symbol_upper = symbol.upper().strip()
    return COMMON_CRYPTOS.get(symbol_upper, symbol.lower().strip())


def get_crypto_price(crypto_id: str, vs_currency: str = "usd") -> dict[str, Any]:
    """Fetch current cryptocurrency price.

    Args:
        crypto_id: CoinGecko ID or common symbol (e.g., "bitcoin" or "BTC").
        vs_currency: Quote currency (default: "usd"). Supports "idr" for IDR.

    Returns:
        Dictionary containing:
        - id: CoinGecko ID
        - symbol: Crypto symbol (uppercase)
        - name: Full name
        - price_usd: Price in USD
        - price_idr: Price in IDR (if vs_currency includes idr)
        - change_24h: 24h percentage change
        - market_cap: Market capitalization
        - volume_24h: 24h trading volume
        - last_updated: ISO timestamp

    Raises:
        ValueError: If crypto_id is empty or invalid.
        RuntimeError: If API call fails.
    """
    if not crypto_id or not isinstance(crypto_id, str):
        raise ValueError("crypto_id must be a non-empty string")

    coin_id = _symbol_to_id(crypto_id)
    cache_key = f"crypto_price:{coin_id}:{vs_currency}"

    cached = _get_cached(cache_key)
    if cached is not None:
        return cached

    try:
        # Build request URL
        currencies = f"usd,idr" if vs_currency.lower() in ("usd", "idr") else vs_currency
        url = f"{COINGECKO_API_BASE}/coins/markets"
        params = {
            "vs_currency": "usd",
            "ids": coin_id,
            "order": "market_cap_desc",
            "per_page": 1,
            "page": 1,
            "sparkline": "false",
            "price_change_percentage": "24h",
        }

        response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

        data = response.json()
        if not data:
            raise RuntimeError(f"No data found for crypto: {crypto_id}")

        coin = data[0]

        # Get IDR price separately if needed
        price_idr = None
        if vs_currency.lower() == "idr" or True:  # Always fetch IDR for Indonesian users
            idr_url = f"{COINGECKO_API_BASE}/simple/price"
            idr_params = {"ids": coin_id, "vs_currencies": "idr"}
            try:
                idr_response = requests.get(idr_url, params=idr_params, timeout=REQUEST_TIMEOUT)
                idr_response.raise_for_status()
                idr_data = idr_response.json()
                price_idr = idr_data.get(coin_id, {}).get("idr")
            except Exception:
                pass  # IDR price is optional

        result = {
            "id": coin["id"],
            "symbol": coin["symbol"].upper(),
            "name": coin["name"],
            "price_usd": coin["current_price"],
            "price_idr": price_idr,
            "change_24h": round(coin.get("price_change_percentage_24h", 0) or 0, 2),
            "market_cap": coin.get("market_cap"),
            "market_cap_rank": coin.get("market_cap_rank"),
            "volume_24h": coin.get("total_volume"),
            "high_24h": coin.get("high_24h"),
            "low_24h": coin.get("low_24h"),
            "last_updated": datetime.now().isoformat(),
        }

        _set_cached(cache_key, result)
        return result

    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed for {crypto_id}: {e}")
        raise RuntimeError(f"Failed to fetch crypto price for {crypto_id}: {e}") from e
    except Exception as e:
        logger.error(f"Failed to fetch crypto price for {crypto_id}: {e}")
        raise RuntimeError(f"Failed to fetch crypto price for {crypto_id}: {e}") from e


def get_crypto_prices_batch(crypto_ids: list[str], vs_currency: str = "usd") -> dict[str, dict[str, Any]]:
    """Fetch prices for multiple cryptocurrencies in a single batch.

    Args:
        crypto_ids: List of CoinGecko IDs or symbols.
        vs_currency: Quote currency.

    Returns:
        Dictionary mapping crypto ID to price data.
    """
    if not crypto_ids:
        return {}

    # Convert symbols to IDs
    coin_ids = [_symbol_to_id(c) for c in crypto_ids if c]
    results: dict[str, dict[str, Any]] = {}

    # Check cache first
    uncached = []
    for coin_id in coin_ids:
        cache_key = f"crypto_price:{coin_id}:{vs_currency}"
        cached = _get_cached(cache_key)
        if cached is not None:
            results[coin_id] = cached
        else:
            uncached.append(coin_id)

    if not uncached:
        return results

    try:
        # Batch request
        url = f"{COINGECKO_API_BASE}/coins/markets"
        params = {
            "vs_currency": "usd",
            "ids": ",".join(uncached),
            "order": "market_cap_desc",
            "per_page": 100,
            "page": 1,
            "sparkline": "false",
            "price_change_percentage": "24h",
        }

        response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

        data = response.json()

        # Get IDR prices in batch
        idr_prices: dict[str, float] = {}
        try:
            idr_url = f"{COINGECKO_API_BASE}/simple/price"
            idr_params = {"ids": ",".join(uncached), "vs_currencies": "idr"}
            idr_response = requests.get(idr_url, params=idr_params, timeout=REQUEST_TIMEOUT)
            idr_response.raise_for_status()
            idr_data = idr_response.json()
            for coin_id, prices in idr_data.items():
                idr_prices[coin_id] = prices.get("idr")
        except Exception:
            pass

        for coin in data:
            coin_id = coin["id"]
            result = {
                "id": coin_id,
                "symbol": coin["symbol"].upper(),
                "name": coin["name"],
                "price_usd": coin["current_price"],
                "price_idr": idr_prices.get(coin_id),
                "change_24h": round(coin.get("price_change_percentage_24h", 0) or 0, 2),
                "market_cap": coin.get("market_cap"),
                "market_cap_rank": coin.get("market_cap_rank"),
                "volume_24h": coin.get("total_volume"),
                "last_updated": datetime.now().isoformat(),
            }
            results[coin_id] = result
            _set_cached(f"crypto_price:{coin_id}:{vs_currency}", result)

        # Mark missing coins
        for coin_id in uncached:
            if coin_id not in results:
                results[coin_id] = {"id": coin_id, "error": "Not found"}

    except Exception as e:
        logger.error(f"Batch crypto fetch failed: {e}")
        for coin_id in uncached:
            if coin_id not in results:
                results[coin_id] = {"id": coin_id, "error": str(e)}

    return results


def get_crypto_history(
    crypto_id: str,
    days: int = 30,
    vs_currency: str = "usd",
) -> list[dict[str, Any]]:
    """Fetch historical cryptocurrency data.

    Args:
        crypto_id: CoinGecko ID or symbol.
        days: Number of days of history (1, 7, 14, 30, 90, 180, 365, max).
        vs_currency: Quote currency.

    Returns:
        List of dictionaries with price history:
        - date: ISO date string
        - price: Price at that time
        - market_cap: Market cap at that time
        - volume: Volume at that time
    """
    if not crypto_id:
        raise ValueError("crypto_id must be provided")

    coin_id = _symbol_to_id(crypto_id)
    cache_key = f"crypto_history:{coin_id}:{days}:{vs_currency}"

    cached = _get_cached(cache_key)
    if cached is not None:
        return cached

    try:
        url = f"{COINGECKO_API_BASE}/coins/{coin_id}/market_chart"
        params = {
            "vs_currency": vs_currency,
            "days": days,
        }

        response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

        data = response.json()

        result = []
        prices = data.get("prices", [])
        market_caps = data.get("market_caps", [])
        volumes = data.get("total_volumes", [])

        for i, (timestamp, price) in enumerate(prices):
            dt = datetime.fromtimestamp(timestamp / 1000)
            result.append({
                "date": dt.isoformat(),
                "price": round(price, 8),
                "market_cap": market_caps[i][1] if i < len(market_caps) else None,
                "volume": volumes[i][1] if i < len(volumes) else None,
            })

        _set_cached(cache_key, result)
        return result

    except Exception as e:
        logger.error(f"Failed to fetch crypto history for {crypto_id}: {e}")
        raise RuntimeError(f"Failed to fetch crypto history for {crypto_id}: {e}") from e


def get_crypto_list() -> list[dict[str, str]]:
    """Fetch list of all supported cryptocurrencies.

    Returns:
        List of dictionaries with:
        - id: CoinGecko ID
        - symbol: Crypto symbol
        - name: Full name
    """
    cache_key = "crypto_list"

    cached = _get_cached(cache_key)
    if cached is not None:
        return cached

    try:
        url = f"{COINGECKO_API_BASE}/coins/list"
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

        data = response.json()
        result = [{"id": c["id"], "symbol": c["symbol"].upper(), "name": c["name"]} for c in data]

        _set_cached(cache_key, result)
        return result

    except Exception as e:
        logger.error(f"Failed to fetch crypto list: {e}")
        raise RuntimeError(f"Failed to fetch crypto list: {e}") from e
