# API & Integration Guide

The `investment-strategy-cskill` relies on live data from external sources. This guide explains how these integrations work and how to handle common issues.

## 1. Yahoo Finance (via `yfinance`)

**Usage**: Primary source for Indonesian stocks (IDX), US stocks, ETFs, and FX rates.

*   **Ticker Formats**:
    *   IDX Stocks: `<Symbol>.JK` (e.g., `TLKM.JK`)
    *   US Stocks: `<Symbol>` (e.g., `MSFT`)
    *   ETFs: `<Symbol>` (e.g., `VOO`)
    *   FX Rates: `IDR=X`, `EURUSD=X`
*   **Data Latency**: Prices are generally real-time or 15-minute delayed depending on the exchange.
*   **Reliability**: Highly reliable. No API key required.

## 2. CoinGecko API

**Usage**: Primary source for cryptocurrency prices.

*   **Ticker Formats**: Standard symbols like `BTC`, `ETH`, `SOL`.
*   **Integration**: Uses the CoinGecko public V3 API.
*   **Rate Limits**: The free tier is limited to 30 calls per minute. The skill includes a basic cache to avoid hitting these limits during multiple `daily check` runs.

## 3. Caching Layer

To ensure speed and stay within rate limits, the skill implements a simple file-based cache in `data/cache/`.

*   **Stock Cache**: Valid for 15 minutes during market hours.
*   **Crypto Cache**: Valid for 5 minutes.
*   **FX Cache**: Valid for 1 hour.

If you need a fresh price immediately, you can bypass the cache by adding `--fresh` to the command (e.g., `daily check --fresh`).

## 4. Error Handling & Fallbacks

If an API becomes unavailable or a ticker is not found:

1.  **Console Warning**: A clear warning will be displayed indicating which asset failed.
2.  **Portfolio Fallback**: The skill will use the `last_price` found in `data/portfolio.json`.
3.  **Manual Override**: You can manually update a price if needed:
    `update price BBCA.JK 9550`

## 5. Security & Privacy

*   **Local Only**: No data about your portfolio or holdings is ever sent to Yahoo Finance or CoinGecko. We only send the *ticker symbols* to fetch prices.
*   **No API Keys**: Both sources used are public and do not require personal API keys or account linking.
