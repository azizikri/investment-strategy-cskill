"""Tests for data fetcher modules.

Note: These tests use mocking to avoid actual API calls.
For integration tests with real APIs, see test_integration.py.
"""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest


class TestStockFetcher:
    @patch("scripts.data_fetchers.stock_fetcher.yf")
    def test_get_stock_price_success(self, mock_yf):
        from scripts.data_fetchers.stock_fetcher import get_stock_price

        mock_ticker = MagicMock()
        mock_ticker.info = {
            "regularMarketPrice": 9650.0,
            "previousClose": 9600.0,
            "currency": "IDR",
            "shortName": "Bank Central Asia",
            "marketState": "REGULAR",
        }
        mock_yf.Ticker.return_value = mock_ticker

        result = get_stock_price("BBCA.JK")

        assert result["ticker"] == "BBCA.JK"
        assert result["price"] == 9650.0
        assert "change_24h" in result
        assert result["currency"] == "IDR"

    def test_get_stock_price_empty_ticker(self):
        from scripts.data_fetchers.stock_fetcher import get_stock_price

        with pytest.raises(ValueError):
            get_stock_price("")

    @patch("scripts.data_fetchers.stock_fetcher.yf")
    def test_get_stock_prices_batch(self, mock_yf):
        from scripts.data_fetchers.stock_fetcher import get_stock_prices_batch

        mock_data = MagicMock()
        mock_data.empty = True
        mock_yf.download.return_value = mock_data

        result = get_stock_prices_batch(["BBCA.JK", "BBRI.JK"])

        assert isinstance(result, dict)


class TestCryptoFetcher:
    @patch("scripts.data_fetchers.crypto_fetcher.requests")
    def test_get_crypto_price_success(self, mock_requests):
        from scripts.data_fetchers.crypto_fetcher import get_crypto_price

        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "id": "bitcoin",
                "symbol": "btc",
                "name": "Bitcoin",
                "current_price": 98000.0,
                "price_change_percentage_24h": 2.5,
                "market_cap": 1900000000000,
                "total_volume": 50000000000,
                "high_24h": 99000.0,
                "low_24h": 96000.0,
                "market_cap_rank": 1,
            }
        ]
        mock_response.raise_for_status = MagicMock()
        mock_requests.get.return_value = mock_response

        result = get_crypto_price("bitcoin")

        assert result["id"] == "bitcoin"
        assert result["symbol"] == "BTC"
        assert result["price_usd"] == 98000.0

    def test_get_crypto_price_empty_id(self):
        from scripts.data_fetchers.crypto_fetcher import get_crypto_price

        with pytest.raises(ValueError):
            get_crypto_price("")

    def test_symbol_to_id_mapping(self):
        from scripts.data_fetchers.crypto_fetcher import COMMON_CRYPTOS

        assert COMMON_CRYPTOS["BTC"] == "bitcoin"
        assert COMMON_CRYPTOS["ETH"] == "ethereum"
        assert COMMON_CRYPTOS["SOL"] == "solana"


class TestFxFetcher:
    @patch("scripts.data_fetchers.fx_fetcher._fetch_from_yahoo")
    def test_get_usd_idr_rate_yahoo_success(self, mock_yahoo):
        from scripts.data_fetchers.fx_fetcher import get_usd_idr_rate

        mock_yahoo.return_value = 15900.0

        result = get_usd_idr_rate()

        assert result["rate"] == 15900.0
        assert result["source"] == "yahoo"
        assert result["is_fallback"] is False

    @patch("scripts.data_fetchers.fx_fetcher._fetch_from_yahoo")
    @patch("scripts.data_fetchers.fx_fetcher._fetch_from_coingecko_proxy")
    def test_get_usd_idr_rate_fallback(self, mock_coingecko, mock_yahoo):
        from scripts.data_fetchers.fx_fetcher import FALLBACK_USD_IDR_RATE, get_usd_idr_rate, _cache

        mock_yahoo.return_value = None
        mock_coingecko.return_value = None

        _cache.clear()
        result = get_usd_idr_rate()

        assert result["rate"] == FALLBACK_USD_IDR_RATE
        assert result["source"] == "fallback"
        assert result["is_fallback"] is True

    def test_convert_usd_to_idr(self):
        from scripts.data_fetchers.fx_fetcher import convert_usd_to_idr

        result = convert_usd_to_idr(100, rate=15900)

        assert result["amount_usd"] == 100
        assert result["amount_idr"] == 1590000
        assert result["rate"] == 15900

    def test_convert_idr_to_usd(self):
        from scripts.data_fetchers.fx_fetcher import convert_idr_to_usd

        result = convert_idr_to_usd(1590000, rate=15900)

        assert result["amount_idr"] == 1590000
        assert result["amount_usd"] == 100
        assert result["rate"] == 15900
