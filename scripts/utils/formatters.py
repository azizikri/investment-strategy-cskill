"""Output formatters for verbose tables and display."""

from __future__ import annotations

from datetime import datetime
from typing import Any

__all__ = [
    "format_currency",
    "format_percentage",
    "format_number",
    "format_table",
    "format_portfolio_row",
    "format_change_indicator",
    "format_date",
    "format_status_badge",
]


def format_currency(amount: float | None, currency: str = "IDR", decimals: int = 0) -> str:
    """Format amount as currency string."""
    if amount is None:
        return "-"

    if currency.upper() == "IDR":
        if abs(amount) >= 1_000_000_000:
            return f"Rp {amount / 1_000_000_000:,.1f}B"
        if abs(amount) >= 1_000_000:
            return f"Rp {amount / 1_000_000:,.1f}M"
        return f"Rp {amount:,.{decimals}f}"

    if currency.upper() == "USD":
        if abs(amount) >= 1_000_000_000:
            return f"${amount / 1_000_000_000:,.1f}B"
        if abs(amount) >= 1_000_000:
            return f"${amount / 1_000_000:,.1f}M"
        return f"${amount:,.2f}"

    return f"{amount:,.{decimals}f} {currency}"


def format_percentage(value: float | None, decimals: int = 2, include_sign: bool = True) -> str:
    """Format value as percentage string."""
    if value is None:
        return "-"

    formatted = f"{value:,.{decimals}f}%"
    if include_sign and value > 0:
        return f"+{formatted}"
    return formatted


def format_number(value: float | None, decimals: int = 2) -> str:
    """Format numeric value with thousands separator."""
    if value is None:
        return "-"
    return f"{value:,.{decimals}f}"


def format_change_indicator(change: float | None) -> str:
    """Format change value with color indicator emoji."""
    if change is None:
        return "➖ -"

    if change > 0:
        return f"🟢 +{change:.2f}%"
    if change < 0:
        return f"🔴 {change:.2f}%"
    return f"⚪ {change:.2f}%"


def format_date(dt: datetime | str | None, fmt: str = "%Y-%m-%d") -> str:
    """Format datetime to string."""
    if dt is None:
        return "-"

    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))
        except ValueError:
            return dt

    return dt.strftime(fmt)


def format_status_badge(status: str) -> str:
    """Format status as emoji badge."""
    status_map = {
        "ok": "✅",
        "warning": "⚠️",
        "error": "❌",
        "info": "ℹ️",
        "pending": "⏳",
        "active": "🟢",
        "inactive": "⚫",
    }
    return status_map.get(status.lower(), "•")


def format_portfolio_row(
    platform: str,
    asset: str,
    quantity: float | str,
    value: float,
    change: float | None,
    currency: str = "IDR",
) -> dict[str, str]:
    """Format a single portfolio row for table display."""
    return {
        "platform": platform,
        "asset": asset,
        "quantity": str(quantity) if isinstance(quantity, str) else format_number(quantity, 4),
        "value": format_currency(value, currency),
        "change": format_change_indicator(change),
    }


def format_table(
    headers: list[str],
    rows: list[list[str]],
    col_widths: list[int] | None = None,
) -> str:
    """Format data as ASCII table."""
    if not headers or not rows:
        return ""

    if col_widths is None:
        col_widths = []
        for i, header in enumerate(headers):
            max_width = len(header)
            for row in rows:
                if i < len(row):
                    max_width = max(max_width, len(str(row[i])))
            col_widths.append(min(max_width + 2, 40))

    def format_row(cells: list[str], widths: list[int]) -> str:
        formatted = []
        for i, cell in enumerate(cells):
            width = widths[i] if i < len(widths) else 15
            formatted.append(str(cell).ljust(width)[:width])
        return "│ " + " │ ".join(formatted) + " │"

    separator_top = "┌" + "┬".join("─" * (w + 2) for w in col_widths) + "┐"
    separator_header = "├" + "┼".join("─" * (w + 2) for w in col_widths) + "┤"
    separator_bottom = "└" + "┴".join("─" * (w + 2) for w in col_widths) + "┘"

    lines = [
        separator_top,
        format_row(headers, col_widths),
        separator_header,
    ]

    for row in rows:
        lines.append(format_row(row, col_widths))

    lines.append(separator_bottom)

    return "\n".join(lines)


def format_section_header(title: str, width: int = 55) -> str:
    """Format section header with decorative lines."""
    line = "━" * width
    return f"\n{line}\n{title}\n{line}"


def format_key_value(key: str, value: Any, key_width: int = 20) -> str:
    """Format key-value pair for display."""
    return f"{key.ljust(key_width)}: {value}"


def format_alert(message: str, level: str = "info") -> str:
    """Format alert message with appropriate emoji."""
    emoji = format_status_badge(level)
    return f"{emoji} {message}"
