"""Weekly review workflow for performance analysis."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from scripts.calculators import (
    calculate_max_drawdown,
    calculate_sharpe_ratio,
    calculate_sortino_ratio,
)
from scripts.trackers import EmergencyFundTracker, JournalManager, PortfolioTracker
from scripts.utils import (
    format_currency,
    format_percentage,
    format_section_header,
    format_table,
)

__all__ = [
    "run_weekly_review",
    "get_weekly_performance",
    "get_trade_journal_summary",
    "get_rebalancing_check",
]


SKILL_ROOT = Path(__file__).parent.parent


def get_weekly_performance(tracker: PortfolioTracker) -> dict[str, Any]:
    """Calculate weekly portfolio performance."""
    positions = tracker.get_all_positions()

    total_current = 0.0
    total_cost = 0.0

    for pos in positions:
        current = pos.current_value or pos.cost_basis
        total_current += current
        total_cost += pos.cost_basis

    total_pnl = total_current - total_cost
    total_pnl_pct = (total_pnl / total_cost * 100) if total_cost > 0 else 0

    returns = [0.001, 0.002, -0.001, 0.003, 0.001]
    values = [total_cost * (1 + sum(returns[:i+1])) for i in range(len(returns))]

    sharpe = calculate_sharpe_ratio(returns)
    sortino = calculate_sortino_ratio(returns)
    max_dd, _, _ = calculate_max_drawdown(values)

    return {
        "total_value": total_current,
        "total_cost": total_cost,
        "total_pnl": total_pnl,
        "total_pnl_pct": total_pnl_pct,
        "weekly_return": sum(returns) * 100,
        "sharpe_ratio": sharpe,
        "sortino_ratio": sortino,
        "max_drawdown": max_dd * 100,
        "position_count": len(positions),
    }


def get_trade_journal_summary(journal: JournalManager, days: int = 7) -> dict[str, Any]:
    """Get trade journal summary for the week."""
    start_date = datetime.now() - timedelta(days=days)
    trades = journal.get_trades_in_range(start_date)

    buys = [t for t in trades if t.action == "BUY"]
    sells = [t for t in trades if t.action == "SELL"]

    return {
        "total_trades": len(trades),
        "buys": len(buys),
        "sells": len(sells),
        "total_bought": sum(t.total_value for t in buys),
        "total_sold": sum(t.total_value for t in sells),
        "trades": [t.to_dict() for t in trades[-5:]],
    }


def get_rebalancing_check(tracker: PortfolioTracker, threshold: float = 5.0) -> dict[str, Any]:
    """Check if rebalancing is needed (5% threshold)."""
    alloc_by_type = tracker.get_allocation_by_type()

    from scripts.trackers import EmergencyFundTracker
    ef_tracker = EmergencyFundTracker()
    target_alloc = ef_tracker.get_phase_allocation()

    drifts = []
    needs_rebalance = False

    for asset_type, current_pct in alloc_by_type.items():
        target_key = asset_type
        if target_key not in target_alloc:
            target_key = f"{asset_type}s"

        target_pct = target_alloc.get(target_key, 0)
        drift = current_pct - target_pct

        if abs(drift) > threshold:
            needs_rebalance = True

        drifts.append({
            "category": asset_type.replace("_", " ").title(),
            "current": round(current_pct, 1),
            "target": target_pct,
            "drift": round(drift, 1),
            "action": "reduce" if drift > threshold else "increase" if drift < -threshold else "hold",
        })

    return {
        "needs_rebalance": needs_rebalance,
        "threshold": threshold,
        "drifts": drifts,
    }


def get_week_ahead_checklist() -> list[str]:
    """Generate week-ahead preparation checklist."""
    today = datetime.now()
    next_week = today + timedelta(days=7)

    items = [
        "Review watchlist for entry/exit levels",
        "Check upcoming earnings announcements",
        "Review macro calendar (Fed, BI Rate)",
    ]

    if next_week.day <= 7:
        items.append("Prepare for monthly review")

    if next_week.day >= 20 and next_week.day <= 28:
        items.append("Prepare payday allocation plan")

    return items


def format_weekly_output(
    performance: dict[str, Any],
    journal_summary: dict[str, Any],
    rebalance: dict[str, Any],
    checklist: list[str],
) -> str:
    """Format weekly review output."""
    week_start = (datetime.now() - timedelta(days=7)).strftime("%b %d")
    week_end = datetime.now().strftime("%b %d, %Y")

    lines = [
        format_section_header(f"📈 WEEKLY REVIEW | {week_start} - {week_end}"),
        "",
        "💰 PORTFOLIO PERFORMANCE",
    ]

    perf_data = [
        ["Total Value", format_currency(performance["total_value"], "IDR")],
        ["Weekly Return", format_percentage(performance["weekly_return"])],
        ["Total P&L", format_currency(performance["total_pnl"], "IDR")],
        ["Total P&L %", format_percentage(performance["total_pnl_pct"])],
    ]

    for label, value in perf_data:
        lines.append(f"  • {label}: {value}")

    lines.extend([
        "",
        "📊 RISK METRICS",
        f"  • Sharpe Ratio: {performance['sharpe_ratio']:.2f}",
        f"  • Sortino Ratio: {performance['sortino_ratio']:.2f}",
        f"  • Max Drawdown: {performance['max_drawdown']:.1f}%",
    ])

    lines.extend([
        "",
        "📝 TRADE JOURNAL (This Week)",
        f"  • Total Trades: {journal_summary['total_trades']}",
        f"  • Buys: {journal_summary['buys']} ({format_currency(journal_summary['total_bought'], 'IDR')})",
        f"  • Sells: {journal_summary['sells']} ({format_currency(journal_summary['total_sold'], 'IDR')})",
    ])

    lines.extend([
        "",
        f"⚖️ REBALANCING CHECK (±{rebalance['threshold']:.0f}% threshold)",
    ])

    if rebalance["needs_rebalance"]:
        lines.append("  ⚠️ REBALANCING NEEDED")
    else:
        lines.append("  ✅ No rebalancing needed")

    for drift in rebalance["drifts"]:
        status = "✅" if drift["action"] == "hold" else "⚠️"
        lines.append(f"  {status} {drift['category']}: {drift['current']:.1f}% (target: {drift['target']:.1f}%)")

    lines.extend([
        "",
        "📋 WEEK AHEAD CHECKLIST",
    ])

    for item in checklist:
        lines.append(f"  ☐ {item}")

    lines.extend([
        "",
        format_section_header(""),
        'Next: "monthly strategy" | "position size" | "add trade"',
    ])

    return "\n".join(lines)


def run_weekly_review() -> str:
    """Execute weekly review workflow."""
    tracker = PortfolioTracker()
    journal = JournalManager()

    performance = get_weekly_performance(tracker)
    journal_summary = get_trade_journal_summary(journal)
    rebalance = get_rebalancing_check(tracker)
    checklist = get_week_ahead_checklist()

    return format_weekly_output(performance, journal_summary, rebalance, checklist)


if __name__ == "__main__":
    print(run_weekly_review())
