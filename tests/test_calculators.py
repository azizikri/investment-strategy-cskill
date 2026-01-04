"""Tests for calculator modules."""

import math

import pytest

from scripts.calculators.phase_detector import detect_phase, get_allocation_target
from scripts.calculators.position_sizer import calculate_position_size, kelly_criterion
from scripts.calculators.rebalancer import calculate_rebalance_trades, check_allocation_drift
from scripts.calculators.risk_metrics import (
    calculate_cagr,
    calculate_max_drawdown,
    calculate_sharpe_ratio,
    calculate_sortino_ratio,
    calculate_volatility,
)


class TestKellyCriterion:
    def test_positive_edge(self):
        result = kelly_criterion(win_rate=0.6, win_loss_ratio=1.5)
        assert 0 < result < 1
        assert math.isclose(result, 0.167, abs_tol=0.01)

    def test_no_edge(self):
        result = kelly_criterion(win_rate=0.5, win_loss_ratio=1.0)
        assert result == 0.0

    def test_negative_edge(self):
        result = kelly_criterion(win_rate=0.3, win_loss_ratio=1.0)
        assert result == 0.0

    def test_zero_win_rate(self):
        result = kelly_criterion(win_rate=0.0, win_loss_ratio=2.0)
        assert result == 0.0

    def test_invalid_ratio(self):
        result = kelly_criterion(win_rate=0.6, win_loss_ratio=-1.0)
        assert result == 0.0

    def test_clipping_high_win_rate(self):
        result = kelly_criterion(win_rate=1.5, win_loss_ratio=2.0)
        assert 0 <= result <= 1


class TestPositionSize:
    def test_basic_calculation(self):
        result = calculate_position_size(
            portfolio_value=100_000,
            kelly_fraction=0.10,
        )
        assert result == 10_000

    def test_max_allocation_cap(self):
        result = calculate_position_size(
            portfolio_value=100_000,
            kelly_fraction=0.50,
            max_allocation=0.25,
        )
        assert result == 25_000

    def test_zero_portfolio(self):
        result = calculate_position_size(
            portfolio_value=0,
            kelly_fraction=0.10,
        )
        assert result == 0.0

    def test_negative_portfolio(self):
        result = calculate_position_size(
            portfolio_value=-100_000,
            kelly_fraction=0.10,
        )
        assert result == 0.0


class TestRiskMetrics:
    def test_sharpe_ratio_positive_returns(self):
        returns = [0.01, 0.02, 0.015, 0.01, 0.005]
        result = calculate_sharpe_ratio(returns, risk_free_rate=0.05)
        assert result > 0

    def test_sharpe_ratio_insufficient_data(self):
        returns = [0.01]
        result = calculate_sharpe_ratio(returns)
        assert result == 0.0

    def test_sortino_ratio_positive_returns(self):
        returns = [0.01, 0.02, -0.005, 0.015, 0.01]
        result = calculate_sortino_ratio(returns, risk_free_rate=0.05)
        assert isinstance(result, float)

    def test_max_drawdown_with_decline(self):
        values = [100, 110, 105, 95, 100, 90, 95]
        max_dd, peak_idx, trough_idx = calculate_max_drawdown(values)
        assert max_dd > 0
        assert peak_idx < trough_idx

    def test_max_drawdown_only_up(self):
        values = [100, 110, 120, 130]
        max_dd, peak_idx, trough_idx = calculate_max_drawdown(values)
        assert max_dd == 0.0

    def test_max_drawdown_empty(self):
        max_dd, peak_idx, trough_idx = calculate_max_drawdown([])
        assert max_dd == 0.0
        assert peak_idx == -1
        assert trough_idx == -1

    def test_cagr_positive_growth(self):
        result = calculate_cagr(start_value=100, end_value=150, years=2)
        assert math.isclose(result, 0.2247, abs_tol=0.01)

    def test_cagr_negative_growth(self):
        result = calculate_cagr(start_value=100, end_value=80, years=2)
        assert result < 0

    def test_cagr_invalid_inputs(self):
        assert calculate_cagr(0, 100, 1) == 0.0
        assert calculate_cagr(100, 0, 1) == 0.0
        assert calculate_cagr(100, 150, 0) == 0.0

    def test_volatility_calculation(self):
        returns = [0.01, -0.01, 0.02, -0.02, 0.01]
        result = calculate_volatility(returns)
        assert result > 0


class TestPhaseDetector:
    def test_phase_1_under_target(self):
        result = detect_phase(ef_balance=10_000, ef_target=36_000)
        assert result == 1

    def test_phase_2_at_target(self):
        result = detect_phase(ef_balance=36_000, ef_target=36_000)
        assert result == 2

    def test_phase_2_over_target(self):
        result = detect_phase(ef_balance=50_000, ef_target=36_000)
        assert result == 2

    def test_zero_target_returns_phase_2(self):
        result = detect_phase(ef_balance=10_000, ef_target=0)
        assert result == 2

    def test_get_allocation_phase_1(self):
        alloc = get_allocation_target(1)
        assert "ef" in alloc
        assert alloc["ef"] == 0.80

    def test_get_allocation_phase_2(self):
        alloc = get_allocation_target(2)
        assert "stocks" in alloc
        assert alloc["stocks"] == 0.50

    def test_invalid_phase_raises(self):
        with pytest.raises(ValueError):
            get_allocation_target(3)


class TestRebalancer:
    def test_drift_detection(self):
        current = {"stocks": 0.65, "bonds": 0.35}
        target = {"stocks": 0.60, "bonds": 0.40}
        result = check_allocation_drift(current, target, threshold=0.05)
        assert len(result) == 2

    def test_no_drift_within_threshold(self):
        current = {"stocks": 0.62, "bonds": 0.38}
        target = {"stocks": 0.60, "bonds": 0.40}
        result = check_allocation_drift(current, target, threshold=0.05)
        assert len(result) == 0

    def test_rebalance_trades_calculation(self):
        current = {"stocks": 0.70, "bonds": 0.30}
        target = {"stocks": 0.60, "bonds": 0.40}
        trades = calculate_rebalance_trades(100_000, current, target)
        assert len(trades) == 2

        stock_trade = next(t for t in trades if t["asset"] == "stocks")
        assert stock_trade["action"] == "sell"
        assert stock_trade["amount"] == 10_000

    def test_rebalance_zero_portfolio(self):
        trades = calculate_rebalance_trades(0, {"stocks": 0.6}, {"stocks": 0.5})
        assert trades == []
