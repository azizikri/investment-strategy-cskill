"""Daily check-in workflow for portfolio monitoring."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from scripts.data_fetchers import (
    get_crypto_price,
    get_stock_price,
    get_usd_idr_rate,
)
from scripts.trackers import EmergencyFundTracker, PortfolioTracker
from scripts.utils import (
    format_change_indicator,
    format_currency,
    format_percentage,
    format_section_header,
    format_table,
)

__all__ = [
    "run_daily_checkin",
    "get_portfolio_snapshot",
    "get_allocation_status",
    "get_alerts",
]


SKILL_ROOT = Path(__file__).parent.parent


def _update_live_prices(tracker: PortfolioTracker) -> dict[str, Any]:
    """Fetch and update live prices for all positions."""
    results = {"updated": 0, "failed": 0, "errors": []}

    fx_data = get_usd_idr_rate()
    tracker.update_fx_rate(fx_data["rate"])

    for pos in tracker.get_all_positions():
        try:
            if pos.type == "crypto":
                crypto_data = get_crypto_price(pos.ticker)
                if "error" not in crypto_data:
                    price = crypto_data.get("price_idr") or crypto_data.get("price_usd", 0) * fx_data["rate"]
                    pos.update_price(price)
                    results["updated"] += 1
                else:
                    results["failed"] += 1
                    results["errors"].append(f"{pos.ticker}: {crypto_data.get('error')}")
            elif pos.type == "money_market":
                pos.update_price(pos.avg_price * 1.001)
                results["updated"] += 1
            else:
                stock_data = get_stock_price(pos.ticker)
                if "error" not in stock_data:
                    pos.update_price(stock_data["price"])
                    results["updated"] += 1
                else:
                    results["failed"] += 1
                    results["errors"].append(f"{pos.ticker}: {stock_data.get('error')}")
        except Exception as e:
            results["failed"] += 1
            results["errors"].append(f"{pos.ticker}: {e}")

    tracker.save()
    return results


def get_portfolio_snapshot(tracker: PortfolioTracker) -> dict[str, Any]:
    """Get current portfolio snapshot with live values."""
    positions = tracker.get_all_positions()

    total_value = 0.0
    position_data = []

    for pos in positions:
        value = pos.current_value or pos.cost_basis
        total_value += value

        position_data.append({
            "platform": pos.platform.title(),
            "asset": pos.name or pos.ticker,
            "ticker": pos.ticker,
            "quantity": pos.quantity,
            "value": value,
            "currency": pos.currency,
            "change_24h": pos.unrealized_pnl_percent,
            "is_ef": pos.is_emergency_fund,
        })

    return {
        "positions": position_data,
        "total_value": total_value,
        "position_count": len(positions),
        "last_updated": datetime.now().isoformat(),
    }


def get_allocation_status(
    tracker: PortfolioTracker,
    ef_tracker: EmergencyFundTracker,
) -> dict[str, Any]:
    """Calculate current vs target allocation."""
    snapshot = get_portfolio_snapshot(tracker)
    total = snapshot["total_value"]

    if total == 0:
        return {"allocations": [], "phase": 1}

    ef_value = sum(p["value"] for p in snapshot["positions"] if p["is_ef"])
    investment_value = total - ef_value

    ef_pct = (ef_value / total) * 100

    target_allocations = ef_tracker.get_phase_allocation()
    phase = ef_tracker.current_phase

    allocations = [
        {
            "category": "Emergency Fund",
            "current": round(ef_pct, 1),
            "target": target_allocations.get("emergency_fund", 80),
            "status": "ok" if abs(ef_pct - target_allocations.get("emergency_fund", 80)) <= 5 else "warning",
        }
    ]

    if investment_value > 0:
        by_type = tracker.get_allocation_by_type()
        for asset_type, pct in by_type.items():
            if asset_type != "money_market":
                target_key = f"{asset_type}s" if not asset_type.endswith("s") else asset_type
                target = target_allocations.get(target_key, 0)
                allocations.append({
                    "category": asset_type.replace("_", " ").title(),
                    "current": round(pct, 1),
                    "target": target,
                    "status": "ok" if abs(pct - target) <= 5 else "warning",
                })

    return {
        "allocations": allocations,
        "phase": phase,
        "ef_progress": ef_tracker.progress_percent,
    }


def get_alerts(
    tracker: PortfolioTracker,
    ef_tracker: EmergencyFundTracker,
) -> list[dict[str, str]]:
    """Generate portfolio alerts."""
    alerts = []

    alloc = get_allocation_status(tracker, ef_tracker)
    for a in alloc["allocations"]:
        if a["status"] == "warning":
            diff = a["current"] - a["target"]
            direction = "over" if diff > 0 else "under"
            alerts.append({
                "level": "warning",
                "message": f"{a['category']}: {abs(diff):.1f}% {direction}weight",
            })

    ef_status = ef_tracker.get_status()
    if ef_status["current_phase"] == 1:
        alerts.append({
            "level": "info",
            "message": f"Phase 1 active - prioritize Emergency Fund ({ef_status['progress_percent']:.1f}% complete)",
        })

    if ef_status["is_complete"]:
        alerts.append({
            "level": "ok",
            "message": "Emergency Fund target reached! Phase 2 unlocked.",
        })

    return alerts


def format_daily_output(
    snapshot: dict[str, Any],
    allocation: dict[str, Any],
    alerts: list[dict[str, str]],
    ef_status: dict[str, Any],
) -> str:
    """Format daily check-in output."""
    today = datetime.now().strftime("%A, %b %d, %Y")

    lines = [
        format_section_header(f"📊 DAILY CHECK-IN | {today}"),
        "",
        "💰 PORTFOLIO SNAPSHOT (Live Prices)",
    ]

    headers = ["Platform", "Asset", "Qty", "Value (IDR)", "24h Δ"]
    rows = []
    for p in snapshot["positions"]:
        qty_str = f"{p['quantity']:.4f}" if p["quantity"] < 100 else f"{p['quantity']:,.0f}"
        rows.append([
            p["platform"],
            p["asset"][:20],
            qty_str,
            format_currency(p["value"], p["currency"]),
            format_change_indicator(p["change_24h"]),
        ])

    rows.append([
        "TOTAL",
        "",
        "",
        format_currency(snapshot["total_value"], "IDR"),
        "",
    ])

    lines.append(format_table(headers, rows, [12, 22, 10, 16, 10]))

    lines.extend([
        "",
        f"📊 ALLOCATION (Current vs Target - Phase {allocation['phase']})",
    ])

    alloc_headers = ["Category", "Current", "Target", "Status"]
    alloc_rows = []
    for a in allocation["allocations"]:
        status = "✅ OK" if a["status"] == "ok" else f"⚠️ {a['current'] - a['target']:+.1f}%"
        alloc_rows.append([
            a["category"],
            format_percentage(a["current"], include_sign=False),
            format_percentage(a["target"], include_sign=False),
            status,
        ])

    lines.append(format_table(alloc_headers, alloc_rows, [18, 10, 10, 12]))

    lines.extend([
        "",
        "🎯 EMERGENCY FUND STATUS",
        f"  • Balance: {format_currency(ef_status['current_balance'], 'IDR')}",
        f"  • Target: {format_currency(ef_status['target_amount'], 'IDR')} ({ef_status['target_months']} months)",
        f"  • Progress: {ef_status['progress_percent']:.1f}% ({ef_status['months_covered']:.1f} months covered)",
        f"  • Phase: {ef_status['phase_label']}",
    ])

    if alerts:
        lines.extend([
            "",
            "⚠️ ALERTS",
        ])
        for alert in alerts:
            emoji = "✅" if alert["level"] == "ok" else "⚠️" if alert["level"] == "warning" else "ℹ️"
            lines.append(f"  {emoji} {alert['message']}")

    lines.extend([
        "",
        format_section_header(""),
        'Next: "weekly review" | "add trade" | "phase check"',
    ])

    return "\n".join(lines)


def run_daily_checkin(update_prices: bool = True) -> str:
    """Execute daily check-in workflow."""
    tracker = PortfolioTracker()
    ef_tracker = EmergencyFundTracker()

    if update_prices:
        _update_live_prices(tracker)

    snapshot = get_portfolio_snapshot(tracker)
    allocation = get_allocation_status(tracker, ef_tracker)
    alerts = get_alerts(tracker, ef_tracker)
    ef_status = ef_tracker.get_status()

    return format_daily_output(snapshot, allocation, alerts, ef_status)


if __name__ == "__main__":
    print(run_daily_checkin())
