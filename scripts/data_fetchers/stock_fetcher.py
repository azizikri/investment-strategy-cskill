"""Yahoo Finance stock data fetcher for IDX and US stocks.

This module provides functions to fetch real-time and historical stock data
using the yfinance library. Supports both Indonesian stocks (*.JK suffix)
and US stocks.

Example:
    >>> from scripts.data_fetchers.stock_fetcher import get_stock_price
    >>> price = get_stock_price("BBCA.JK")
    >>> print(price)
    {'ticker': 'BBCA.JK', 'price': 9650.0, 'change_24h': -0.5, ...}
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

import yfinance as yf

__all__ = [
    "get_stock_price",
    "get_stock_prices_batch",
    "get_stock_history",
    "get_stock_info",
]

logger = logging.getLogger(__name__)

# Cache for API responses (simple in-memory cache)
_cache: dict[str, tuple[Any, datetime]] = {}
CACHE_TTL_SECONDS: int = 300  # 5 minutes


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


def get_stock_price(ticker: str) -> dict[str, Any]:
    """Fetch current stock price and 24h change.

    Args:
        ticker: Stock ticker symbol. For Indonesian stocks, use .JK suffix
                (e.g., "BBCA.JK"). For US stocks, use standard symbols.

    Returns:
        Dictionary containing:
        - ticker: The ticker symbol
        - price: Current/latest price
        - change_24h: Percentage change from previous close
        - currency: Currency of the price (IDR, USD, etc.)
        - last_updated: ISO timestamp of price fetch
        - market_status: "open" or "closed"

    Raises:
        ValueError: If ticker is empty or invalid.
        RuntimeError: If API call fails.
    """
    if not ticker or not isinstance(ticker, str):
        raise ValueError("Ticker must be a non-empty string")

    ticker = ticker.upper().strip()
    cache_key = f"price:{ticker}"

    cached = _get_cached(cache_key)
    if cached is not None:
        return cached

    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        # Get current price - try multiple fields
        price = info.get("regularMarketPrice") or info.get("currentPrice") or info.get("previousClose")
        if price is None:
            # Fallback: get from history
            hist = stock.history(period="1d")
            if not hist.empty:
                price = float(hist["Close"].iloc[-1])
            else:
                raise RuntimeError(f"Could not fetch price for {ticker}")

        # Calculate 24h change
        prev_close = info.get("previousClose") or info.get("regularMarketPreviousClose")
        if prev_close and prev_close > 0:
            change_24h = ((price - prev_close) / prev_close) * 100
        else:
            change_24h = 0.0

        # Determine currency
        currency = info.get("currency", "USD")
        if ticker.endswith(".JK"):
            currency = "IDR"

        # Market status
        market_state = info.get("marketState", "CLOSED")
        market_status = "open" if market_state in ("REGULAR", "PRE", "POST") else "closed"

        result = {
            "ticker": ticker,
            "price": float(price),
            "change_24h": round(float(change_24h), 2),
            "currency": currency,
            "last_updated": datetime.now().isoformat(),
            "market_status": market_status,
            "name": info.get("shortName", info.get("longName", ticker)),
        }

        _set_cached(cache_key, result)
        return result

    except Exception as e:
        logger.error(f"Failed to fetch stock price for {ticker}: {e}")
        raise RuntimeError(f"Failed to fetch stock price for {ticker}: {e}") from e


def get_stock_prices_batch(tickers: list[str]) -> dict[str, dict[str, Any]]:
    """Fetch prices for multiple stocks in a single batch.

    More efficient than calling get_stock_price() multiple times.

    Args:
        tickers: List of ticker symbols.

    Returns:
        Dictionary mapping ticker to price data. Failed tickers will have
        an error field instead of price data.
    """
    if not tickers:
        return {}

    results: dict[str, dict[str, Any]] = {}

    # Clean tickers
    clean_tickers = [t.upper().strip() for t in tickers if t and isinstance(t, str)]

    # Check cache first
    uncached = []
    for ticker in clean_tickers:
        cache_key = f"price:{ticker}"
        cached = _get_cached(cache_key)
        if cached is not None:
            results[ticker] = cached
        else:
            uncached.append(ticker)

    if not uncached:
        return results

    try:
        # Batch download
        data = yf.download(uncached, period="2d", progress=False, group_by="ticker")

        for ticker in uncached:
            try:
                if len(uncached) == 1:
                    ticker_data = data
                else:
                    ticker_data = data[ticker] if ticker in data.columns.levels[0] else None

                if ticker_data is not None and not ticker_data.empty:
                    latest = ticker_data["Close"].dropna()
                    if len(latest) >= 1:
                        price = float(latest.iloc[-1])
                        prev_close = float(latest.iloc[-2]) if len(latest) >= 2 else price
                        change_24h = ((price - prev_close) / prev_close) * 100 if prev_close > 0 else 0.0

                        result = {
                            "ticker": ticker,
                            "price": price,
                            "change_24h": round(change_24h, 2),
                            "currency": "IDR" if ticker.endswith(".JK") else "USD",
                            "last_updated": datetime.now().isoformat(),
                            "market_status": "unknown",
                            "name": ticker,
                        }
                        results[ticker] = result
                        _set_cached(f"price:{ticker}", result)
                    else:
                        results[ticker] = {"ticker": ticker, "error": "No data available"}
                else:
                    results[ticker] = {"ticker": ticker, "error": "No data available"}
            except Exception as e:
                results[ticker] = {"ticker": ticker, "error": str(e)}

    except Exception as e:
        logger.error(f"Batch download failed: {e}")
        for ticker in uncached:
            if ticker not in results:
                results[ticker] = {"ticker": ticker, "error": str(e)}

    return results


def get_stock_history(
    ticker: str,
    period: str = "1mo",
    interval: str = "1d",
) -> list[dict[str, Any]]:
    """Fetch historical stock data.

    Args:
        ticker: Stock ticker symbol.
        period: Data period. Valid: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max.
        interval: Data interval. Valid: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo.

    Returns:
        List of dictionaries with OHLCV data:
        - date: ISO date string
        - open: Opening price
        - high: High price
        - low: Low price
        - close: Closing price
        - volume: Trading volume
    """
    if not ticker:
        raise ValueError("Ticker must be provided")

    ticker = ticker.upper().strip()
    cache_key = f"history:{ticker}:{period}:{interval}"

    cached = _get_cached(cache_key)
    if cached is not None:
        return cached

    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period, interval=interval)

        if hist.empty:
            return []

        result = []
        for idx, row in hist.iterrows():
            result.append({
                "date": idx.isoformat() if hasattr(idx, "isoformat") else str(idx),
                "open": round(float(row["Open"]), 4),
                "high": round(float(row["High"]), 4),
                "low": round(float(row["Low"]), 4),
                "close": round(float(row["Close"]), 4),
                "volume": int(row["Volume"]),
            })

        _set_cached(cache_key, result)
        return result

    except Exception as e:
        logger.error(f"Failed to fetch history for {ticker}: {e}")
        raise RuntimeError(f"Failed to fetch history for {ticker}: {e}") from e


def get_stock_info(ticker: str) -> dict[str, Any]:
    """Fetch detailed stock information.

    Args:
        ticker: Stock ticker symbol.

    Returns:
        Dictionary with stock metadata:
        - ticker: Symbol
        - name: Company name
        - sector: Industry sector
        - market_cap: Market capitalization
        - pe_ratio: Price-to-earnings ratio
        - dividend_yield: Annual dividend yield
        - 52_week_high: 52-week high price
        - 52_week_low: 52-week low price
    """
    if not ticker:
        raise ValueError("Ticker must be provided")

    ticker = ticker.upper().strip()
    cache_key = f"info:{ticker}"

    cached = _get_cached(cache_key)
    if cached is not None:
        return cached

    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        result = {
            "ticker": ticker,
            "name": info.get("shortName", info.get("longName", ticker)),
            "sector": info.get("sector", "Unknown"),
            "industry": info.get("industry", "Unknown"),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "dividend_yield": info.get("dividendYield"),
            "52_week_high": info.get("fiftyTwoWeekHigh"),
            "52_week_low": info.get("fiftyTwoWeekLow"),
            "avg_volume": info.get("averageVolume"),
            "currency": info.get("currency", "USD"),
        }

        _set_cached(cache_key, result)
        return result

    except Exception as e:
        logger.error(f"Failed to fetch info for {ticker}: {e}")
        raise RuntimeError(f"Failed to fetch info for {ticker}: {e}") from e
