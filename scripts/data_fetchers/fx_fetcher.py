"""Foreign exchange rate fetcher for IDR/USD conversion.

This module provides functions to fetch current exchange rates,
primarily for converting USD prices to IDR for Indonesian investors.

Uses multiple free sources with fallback:
1. Yahoo Finance (USDIDR=X)
2. CoinGecko (via stable coin proxy)
3. Fallback to hardcoded rate

Example:
    >>> from scripts.data_fetchers.fx_fetcher import get_usd_idr_rate
    >>> rate = get_usd_idr_rate()
    >>> print(rate)
    {'rate': 15900.0, 'source': 'yahoo', 'last_updated': '...'}
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

import requests
import yfinance as yf

__all__ = [
    "get_usd_idr_rate",
    "get_exchange_rate",
    "convert_usd_to_idr",
    "convert_idr_to_usd",
]

logger = logging.getLogger(__name__)

# Cache for exchange rates
_cache: dict[str, tuple[Any, datetime]] = {}
CACHE_TTL_SECONDS: int = 300  # 5 minutes

# Fallback rate if all sources fail
FALLBACK_USD_IDR_RATE: float = 15900.0

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


def _fetch_from_yahoo(pair: str) -> float | None:
    """Fetch exchange rate from Yahoo Finance.

    Args:
        pair: Currency pair (e.g., "USDIDR=X").

    Returns:
        Exchange rate or None if failed.
    """
    try:
        ticker = yf.Ticker(pair)
        info = ticker.info
        rate = info.get("regularMarketPrice") or info.get("previousClose")

        if rate and rate > 0:
            return float(rate)

        # Try history
        hist = ticker.history(period="1d")
        if not hist.empty:
            return float(hist["Close"].iloc[-1])

        return None

    except Exception as e:
        logger.debug(f"Yahoo Finance fetch failed for {pair}: {e}")
        return None


def _fetch_from_coingecko_proxy() -> float | None:
    """Fetch USD/IDR rate using CoinGecko USDT as proxy.

    Gets USDT price in both USD and IDR to calculate exchange rate.

    Returns:
        Exchange rate or None if failed.
    """
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {"ids": "tether", "vs_currencies": "usd,idr"}

        response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

        data = response.json()
        usdt_data = data.get("tether", {})

        usd_price = usdt_data.get("usd", 1.0)
        idr_price = usdt_data.get("idr")

        if idr_price and usd_price and usd_price > 0:
            return float(idr_price / usd_price)

        return None

    except Exception as e:
        logger.debug(f"CoinGecko proxy fetch failed: {e}")
        return None


def get_usd_idr_rate() -> dict[str, Any]:
    """Fetch current USD/IDR exchange rate.

    Tries multiple sources in order:
    1. Yahoo Finance (USDIDR=X)
    2. CoinGecko (via USDT proxy)
    3. Fallback hardcoded rate

    Returns:
        Dictionary containing:
        - rate: Exchange rate (1 USD = X IDR)
        - source: Data source used ("yahoo", "coingecko", "fallback")
        - last_updated: ISO timestamp
        - is_fallback: True if using fallback rate
    """
    cache_key = "fx:USDIDR"

    cached = _get_cached(cache_key)
    if cached is not None:
        return cached

    rate = None
    source = "fallback"
    is_fallback = True

    # Try Yahoo Finance first
    rate = _fetch_from_yahoo("USDIDR=X")
    if rate and rate > 0:
        source = "yahoo"
        is_fallback = False
    else:
        # Try CoinGecko proxy
        rate = _fetch_from_coingecko_proxy()
        if rate and rate > 0:
            source = "coingecko"
            is_fallback = False

    # Use fallback if all sources failed
    if rate is None or rate <= 0:
        rate = FALLBACK_USD_IDR_RATE
        source = "fallback"
        is_fallback = True
        logger.warning(f"Using fallback USD/IDR rate: {FALLBACK_USD_IDR_RATE}")

    result = {
        "rate": round(float(rate), 2),
        "source": source,
        "last_updated": datetime.now().isoformat(),
        "is_fallback": is_fallback,
        "pair": "USD/IDR",
    }

    _set_cached(cache_key, result)
    return result


def get_exchange_rate(from_currency: str, to_currency: str) -> dict[str, Any]:
    """Fetch exchange rate between two currencies.

    Args:
        from_currency: Source currency code (e.g., "USD").
        to_currency: Target currency code (e.g., "IDR").

    Returns:
        Dictionary containing:
        - rate: Exchange rate (1 from_currency = X to_currency)
        - from_currency: Source currency
        - to_currency: Target currency
        - source: Data source used
        - last_updated: ISO timestamp
    """
    from_curr = from_currency.upper().strip()
    to_curr = to_currency.upper().strip()

    # Handle USD/IDR specifically (most common case)
    if (from_curr == "USD" and to_curr == "IDR"):
        usd_idr = get_usd_idr_rate()
        return {
            "rate": usd_idr["rate"],
            "from_currency": from_curr,
            "to_currency": to_curr,
            "source": usd_idr["source"],
            "last_updated": usd_idr["last_updated"],
            "is_fallback": usd_idr.get("is_fallback", False),
        }

    if (from_curr == "IDR" and to_curr == "USD"):
        usd_idr = get_usd_idr_rate()
        return {
            "rate": round(1.0 / usd_idr["rate"], 8),
            "from_currency": from_curr,
            "to_currency": to_curr,
            "source": usd_idr["source"],
            "last_updated": usd_idr["last_updated"],
            "is_fallback": usd_idr.get("is_fallback", False),
        }

    # Generic forex pair via Yahoo Finance
    cache_key = f"fx:{from_curr}{to_curr}"
    cached = _get_cached(cache_key)
    if cached is not None:
        return cached

    pair = f"{from_curr}{to_curr}=X"
    rate = _fetch_from_yahoo(pair)

    if rate and rate > 0:
        result = {
            "rate": round(float(rate), 6),
            "from_currency": from_curr,
            "to_currency": to_curr,
            "source": "yahoo",
            "last_updated": datetime.now().isoformat(),
            "is_fallback": False,
        }
        _set_cached(cache_key, result)
        return result

    # Fallback: return error
    raise RuntimeError(f"Could not fetch exchange rate for {from_curr}/{to_curr}")


def convert_usd_to_idr(amount_usd: float, rate: float | None = None) -> dict[str, Any]:
    """Convert USD amount to IDR."""
    if rate is None:
        fx_data = get_usd_idr_rate()
        effective_rate: float = float(fx_data["rate"])
        source = fx_data["source"]
    else:
        effective_rate = float(rate)
        source = "provided"

    amount_idr = float(amount_usd) * effective_rate

    return {
        "amount_usd": round(float(amount_usd), 2),
        "amount_idr": round(amount_idr, 0),
        "rate": effective_rate,
        "rate_source": source,
    }


def convert_idr_to_usd(amount_idr: float, rate: float | None = None) -> dict[str, Any]:
    """Convert IDR amount to USD."""
    if rate is None:
        fx_data = get_usd_idr_rate()
        effective_rate: float = float(fx_data["rate"])
        source = fx_data["source"]
    else:
        effective_rate = float(rate)
        source = "provided"

    amount_usd = float(amount_idr) / effective_rate

    return {
        "amount_idr": round(float(amount_idr), 0),
        "amount_usd": round(amount_usd, 2),
        "rate": effective_rate,
        "rate_source": source,
    }
