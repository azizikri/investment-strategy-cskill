"""Integration tests for investment strategy skill.

These tests verify end-to-end functionality with actual data files.
Some tests may require network access for live API testing.
"""

import json
import tempfile
from pathlib import Path

import pytest

from scripts.trackers.ef_tracker import EmergencyFundTracker
from scripts.trackers.journal_manager import JournalManager, TradeEntry
from scripts.trackers.portfolio_tracker import PortfolioTracker, Position
from scripts.utils.csv_handler import (
    export_portfolio_to_csv,
    generate_csv_template,
    import_portfolio_from_csv,
)
from scripts.utils.formatters import (
    format_change_indicator,
    format_currency,
    format_percentage,
    format_table,
)
from scripts.utils.validators import (
    ValidationError,
    validate_currency,
    validate_platform,
    validate_price,
    validate_quantity,
    validate_ticker,
)


class TestPortfolioTracker:
    def test_add_and_get_position(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            temp_path = Path(f.name)

        try:
            tracker = PortfolioTracker(temp_path)

            pos = Position(
                ticker="BBCA.JK",
                platform="stockbit",
                quantity=10,
                avg_price=9500,
            )
            tracker.add_position(pos)

            retrieved = tracker.get_position("BBCA.JK")
            assert retrieved is not None
            assert retrieved.ticker == "BBCA.JK"
            assert retrieved.quantity == 10
        finally:
            temp_path.unlink(missing_ok=True)

    def test_position_calculations(self):
        pos = Position(
            ticker="NVDA",
            platform="gotrade",
            quantity=0.5,
            avg_price=140,
            currency="USD",
        )

        assert pos.cost_basis == 70
        assert pos.current_value is None

        pos.update_price(150)
        assert pos.current_value == 75
        assert pos.unrealized_pnl == 5
        assert pos.unrealized_pnl_percent == pytest.approx(7.14, rel=0.01)


class TestJournalManager:
    def test_add_and_get_trade(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            temp_path = Path(f.name)

        try:
            journal = JournalManager(temp_path)

            trade = TradeEntry(
                ticker="BBCA.JK",
                action="BUY",
                quantity=10,
                price=9500,
                platform="stockbit",
                thesis="Blue chip banking stock",
            )
            journal.add_trade(trade)

            recent = journal.get_recent_trades(1)
            assert len(recent) == 1
            assert recent[0].ticker == "BBCA.JK"
        finally:
            temp_path.unlink(missing_ok=True)

    def test_trade_stats(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            temp_path = Path(f.name)

        try:
            journal = JournalManager(temp_path)

            journal.add_trade(TradeEntry("BBCA.JK", "BUY", 10, 9500, "stockbit"))
            journal.add_trade(TradeEntry("NVDA", "BUY", 0.5, 140, "gotrade", currency="USD"))

            stats = journal.calculate_stats()
            assert stats["total_trades"] == 2
            assert stats["buys"] == 2
            assert stats["sells"] == 0
        finally:
            temp_path.unlink(missing_ok=True)


class TestEmergencyFundTracker:
    def test_phase_detection(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            temp_path = Path(f.name)

        try:
            tracker = EmergencyFundTracker(temp_path)
            tracker.configure(target_months=6, monthly_expenses=6_000_000)

            tracker.update_balance(18_000_000)
            assert tracker.current_phase == 1
            assert tracker.months_covered == 3.0

            tracker.update_balance(36_000_000)
            assert tracker.current_phase == 2
            assert tracker.is_complete
        finally:
            temp_path.unlink(missing_ok=True)

    def test_contribution_tracking(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            temp_path = Path(f.name)

        try:
            tracker = EmergencyFundTracker(temp_path)
            tracker.configure(target_months=6, monthly_expenses=6_000_000)

            tracker.update_balance(10_000_000)
            tracker.add_contribution(2_000_000)

            assert tracker.current_balance == 12_000_000
            assert len(tracker.history) >= 2
        finally:
            temp_path.unlink(missing_ok=True)


class TestCSVHandler:
    def test_generate_and_import_csv(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "portfolio.csv"

            generate_csv_template(csv_path)
            assert csv_path.exists()

            portfolio = import_portfolio_from_csv(csv_path)
            assert "positions" in portfolio
            assert len(portfolio["positions"]) == 4

    def test_export_portfolio(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "export.csv"

            portfolio = {
                "positions": [
                    {
                        "platform": "stockbit",
                        "ticker": "BBCA.JK",
                        "name": "BCA",
                        "quantity": 10,
                        "avg_price": 9500,
                        "currency": "IDR",
                        "purchase_date": "2025-01-01",
                        "type": "stock",
                        "is_emergency_fund": False,
                    }
                ]
            }

            result_path = export_portfolio_to_csv(portfolio, csv_path)
            assert result_path.exists()

            content = csv_path.read_text()
            assert "BBCA.JK" in content


class TestFormatters:
    def test_format_currency_idr(self):
        assert format_currency(12_500_000, "IDR") == "Rp 12.5M"
        assert format_currency(1_650_000_000, "IDR") == "Rp 1.6B"

    def test_format_currency_usd(self):
        assert format_currency(1500.50, "USD") == "$1,500.50"

    def test_format_percentage(self):
        assert format_percentage(5.5) == "+5.50%"
        assert format_percentage(-3.2) == "-3.20%"

    def test_format_change_indicator(self):
        positive = format_change_indicator(5.5)
        assert "🟢" in positive or "+" in positive

        negative = format_change_indicator(-3.2)
        assert "🔴" in negative or "-" in negative

    def test_format_table(self):
        headers = ["A", "B", "C"]
        rows = [["1", "2", "3"], ["4", "5", "6"]]
        result = format_table(headers, rows)

        assert "A" in result
        assert "1" in result
        assert "│" in result or "|" in result


class TestValidators:
    def test_validate_ticker(self):
        assert validate_ticker("BBCA.JK") == "BBCA.JK"
        assert validate_ticker("nvda") == "NVDA"

        with pytest.raises(ValidationError):
            validate_ticker("")

    def test_validate_currency(self):
        assert validate_currency("idr") == "IDR"
        assert validate_currency("USD") == "USD"

        with pytest.raises(ValidationError):
            validate_currency("EUR")

    def test_validate_quantity(self):
        assert validate_quantity(10) == 10.0
        assert validate_quantity("5.5") == 5.5

        with pytest.raises(ValidationError):
            validate_quantity(-1)

    def test_validate_price(self):
        assert validate_price(9500) == 9500.0

        with pytest.raises(ValidationError):
            validate_price(0)

    def test_validate_platform(self):
        assert validate_platform("stockbit") == "stockbit"
        assert validate_platform("BIBIT") == "bibit"

        with pytest.raises(ValidationError):
            validate_platform("unknown_platform")
