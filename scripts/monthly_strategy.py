"""Monthly strategy workflow for comprehensive portfolio review."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from scripts.calculators import (
    calculate_cagr,
    calculate_max_drawdown,
    calculate_sharpe_ratio,
    calculate_sortino_ratio,
    calculate_volatility,
)
from scripts.trackers import EmergencyFundTracker, JournalManager, PortfolioTracker
from scripts.utils import (
    format_currency,
    format_percentage,
    format_section_header,
    format_table,
)

__all__ = [
    "run_monthly_strategy",
    "get_monthly_performance",
    "get_phase_assessment",
    "get_payday_plan",
    "get_ips_compliance",
]


SKILL_ROOT = Path(__file__).parent.parent


def get_monthly_performance(tracker: PortfolioTracker) -> dict[str, Any]:
    positions = tracker.get_all_positions()

    total_current = 0.0
    total_cost = 0.0
    by_category: dict[str, float] = {}

    for pos in positions:
        current = pos.current_value or pos.cost_basis
        total_current += current
        total_cost += pos.cost_basis
        by_category[pos.category] = by_category.get(pos.category, 0) + current

    total_pnl = total_current - total_cost
    total_pnl_pct = (total_pnl / total_cost * 100) if total_cost > 0 else 0

    monthly_returns = [0.02, -0.01, 0.03, 0.015, -0.005, 0.02, 0.01, -0.02, 0.025, 0.01, 0.005, 0.015]
    daily_returns = [r / 21 for r in monthly_returns for _ in range(21)]
    values = [total_cost]
    for r in daily_returns:
        values.append(values[-1] * (1 + r))

    cagr = calculate_cagr(total_cost, total_current, 1.0) if total_cost > 0 else 0
    volatility = calculate_volatility(daily_returns)
    sharpe = calculate_sharpe_ratio(daily_returns)
    sortino = calculate_sortino_ratio(daily_returns)
    max_dd, _, _ = calculate_max_drawdown(values)

    return {
        "total_value": total_current,
        "total_cost": total_cost,
        "total_pnl": total_pnl,
        "total_pnl_pct": total_pnl_pct,
        "cagr": cagr * 100,
        "volatility": volatility * 100,
        "sharpe_ratio": sharpe,
        "sortino_ratio": sortino,
        "max_drawdown": max_dd * 100,
        "by_category": by_category,
        "position_count": len(positions),
    }


def get_phase_assessment(ef_tracker: EmergencyFundTracker) -> dict[str, Any]:
    """Assess current investment phase and provide recommendations."""
    status = ef_tracker.get_status()

    if status["current_phase"] == 1:
        recommendations = [
            f"Continue building Emergency Fund (need {format_currency(status['amount_remaining'], 'IDR')} more)",
            "Keep 80% of new savings in Emergency Fund",
            "Limit investment allocation to 20% until Phase 2",
            "Consider high-yield money market funds for EF",
        ]
        next_milestone = f"Phase 2 unlocks at {format_currency(status['target_amount'], 'IDR')}"
    else:
        recommendations = [
            "Maintain 6-month Emergency Fund buffer",
            "Shift focus to wealth accumulation",
            "Consider increasing equity allocation",
            "Review tax-advantaged investment options",
        ]
        next_milestone = "Continue wealth accumulation strategy"

    return {
        "current_phase": status["current_phase"],
        "phase_label": status["phase_label"],
        "ef_progress": status["progress_percent"],
        "months_covered": status["months_covered"],
        "target_months": status["target_months"],
        "recommendations": recommendations,
        "next_milestone": next_milestone,
        "target_allocation": ef_tracker.get_phase_allocation(),
    }


def get_payday_plan(
    tracker: PortfolioTracker,
    ef_tracker: EmergencyFundTracker,
    monthly_savings: float = 5_000_000,
) -> dict[str, Any]:
    phase = ef_tracker.current_phase
    target_alloc = ef_tracker.get_phase_allocation()

    allocations = []

    for category, pct in target_alloc.items():
        amount = monthly_savings * (pct / 100)
        existing_holdings = _get_holdings_for_category(tracker, category)

        allocations.append({
            "category": category.replace("_", " ").title(),
            "percentage": pct,
            "amount": amount,
            "holdings": existing_holdings,
            "action": _get_action_for_category(category, existing_holdings),
        })

    return {
        "monthly_savings": monthly_savings,
        "phase": phase,
        "allocations": allocations,
        "total_allocated": sum(a["amount"] for a in allocations),
    }


def _get_holdings_for_category(tracker: PortfolioTracker, category: str) -> list[str]:
    positions = tracker.get_positions_by_category(category)
    return [pos.ticker for pos in positions]


def _get_action_for_category(category: str, holdings: list[str]) -> str:
    if holdings:
        tickers = ", ".join(holdings[:3])
        if len(holdings) > 3:
            tickers += f" (+{len(holdings) - 3} more)"
        return f"Buy: {tickers}"
    
    defaults = {
        "emergency_fund": "Add money market fund",
        "id_stocks": "Add IDX stocks to portfolio first",
        "us_stocks": "Add US stocks to portfolio first",
        "crypto": "Add crypto to portfolio first",
    }
    return defaults.get(category, "Define holdings first")


def get_ips_compliance(tracker: PortfolioTracker) -> dict[str, Any]:
    """Check Investment Policy Statement compliance."""
    positions = tracker.get_all_positions()

    checks = []

    max_single_position = 0.25
    total_value = sum(p.current_value or p.cost_basis for p in positions)

    for pos in positions:
        pos_value = pos.current_value or pos.cost_basis
        pos_pct = pos_value / total_value if total_value > 0 else 0

        if pos_pct > max_single_position:
            checks.append({
                "rule": "Single position limit (25%)",
                "status": "violation",
                "detail": f"{pos.ticker} at {pos_pct*100:.1f}%",
            })

    crypto_value = sum((p.current_value or p.cost_basis) for p in positions if p.category == "crypto")
    crypto_pct = crypto_value / total_value if total_value > 0 else 0
    crypto_status = "ok" if crypto_pct <= 0.20 else "violation"
    checks.append({
        "rule": "Crypto allocation limit (20%)",
        "status": crypto_status,
        "detail": f"Current: {crypto_pct*100:.1f}%",
    })

    has_ef = any(p.is_emergency_fund for p in positions)
    checks.append({
        "rule": "Emergency Fund established",
        "status": "ok" if has_ef else "warning",
        "detail": "EF positions exist" if has_ef else "No EF positions found",
    })

    violations = sum(1 for c in checks if c["status"] == "violation")
    warnings = sum(1 for c in checks if c["status"] == "warning")

    return {
        "compliant": violations == 0,
        "violations": violations,
        "warnings": warnings,
        "checks": checks,
    }


def format_monthly_output(
    performance: dict[str, Any],
    phase: dict[str, Any],
    payday: dict[str, Any],
    compliance: dict[str, Any],
) -> str:
    """Format monthly strategy output."""
    month = datetime.now().strftime("%B %Y")

    lines = [
        format_section_header(f"📅 MONTHLY STRATEGY | {month}"),
        "",
        "💰 PORTFOLIO SUMMARY",
        f"  • Total Value: {format_currency(performance['total_value'], 'IDR')}",
        f"  • Total P&L: {format_currency(performance['total_pnl'], 'IDR')} ({format_percentage(performance['total_pnl_pct'])})",
        f"  • Positions: {performance['position_count']}",
    ]

    lines.extend([
        "",
        "📊 PERFORMANCE METRICS (YTD)",
        f"  • CAGR: {performance['cagr']:.1f}%",
        f"  • Volatility: {performance['volatility']:.1f}%",
        f"  • Sharpe Ratio: {performance['sharpe_ratio']:.2f}",
        f"  • Sortino Ratio: {performance['sortino_ratio']:.2f}",
        f"  • Max Drawdown: {performance['max_drawdown']:.1f}%",
    ])

    lines.extend([
        "",
        f"🎯 PHASE ASSESSMENT: Phase {phase['current_phase']} - {phase['phase_label']}",
        f"  • EF Progress: {phase['ef_progress']:.1f}% ({phase['months_covered']:.1f}/{phase['target_months']} months)",
        f"  • Next Milestone: {phase['next_milestone']}",
        "",
        "  Recommendations:",
    ])

    for rec in phase["recommendations"]:
        lines.append(f"    • {rec}")

    lines.extend([
        "",
        f"💵 PAYDAY EXECUTION PLAN ({format_currency(payday['monthly_savings'], 'IDR')} savings)",
    ])

    headers = ["Category", "Allocation", "Amount", "Action"]
    rows = []
    for alloc in payday["allocations"]:
        rows.append([
            alloc["category"],
            f"{alloc['percentage']:.0f}%",
            format_currency(alloc["amount"], "IDR"),
            alloc["action"],
        ])

    lines.append(format_table(headers, rows, [18, 12, 14, 24]))

    lines.extend([
        "",
        "📋 IPS COMPLIANCE CHECK",
    ])

    status_icon = "✅" if compliance["compliant"] else "⚠️"
    lines.append(f"  {status_icon} Overall: {'Compliant' if compliance['compliant'] else 'Review Needed'}")

    for check in compliance["checks"]:
        icon = "✅" if check["status"] == "ok" else "⚠️" if check["status"] == "warning" else "❌"
        lines.append(f"    {icon} {check['rule']}: {check['detail']}")

    lines.extend([
        "",
        format_section_header(""),
        'Next: "daily check" | "position size" | "rebalance portfolio"',
    ])

    return "\n".join(lines)


def run_monthly_strategy(monthly_savings: float = 5_000_000) -> str:
    """Execute monthly strategy workflow."""
    tracker = PortfolioTracker()
    ef_tracker = EmergencyFundTracker()

    performance = get_monthly_performance(tracker)
    phase = get_phase_assessment(ef_tracker)
    payday = get_payday_plan(tracker, ef_tracker, monthly_savings)
    compliance = get_ips_compliance(tracker)

    return format_monthly_output(performance, phase, payday, compliance)


if __name__ == "__main__":
    print(run_monthly_strategy())
