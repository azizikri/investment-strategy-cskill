"""CSV import/export utilities for portfolio data."""

from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any

__all__ = [
    "import_portfolio_from_csv",
    "export_portfolio_to_csv",
    "generate_csv_template",
    "CSV_HEADERS",
]


CSV_HEADERS = [
    "platform",
    "ticker",
    "name",
    "quantity",
    "avg_price",
    "currency",
    "purchase_date",
    "type",
    "is_emergency_fund",
]


def generate_csv_template(output_path: str | Path) -> Path:
    """Generate empty CSV template with headers and sample row."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    sample_rows = [
        [
            "bibit",
            "RDPU-SUCORINVEST",
            "Sucorinvest Money Market Fund",
            "12500000",
            "1.0",
            "IDR",
            "2025-01-01",
            "money_market",
            "true",
        ],
        [
            "stockbit",
            "BBCA.JK",
            "Bank Central Asia",
            "10",
            "9500",
            "IDR",
            "2025-01-02",
            "stock",
            "false",
        ],
        [
            "gotrade",
            "NVDA",
            "NVIDIA Corporation",
            "0.5",
            "140",
            "USD",
            "2025-01-02",
            "stock",
            "false",
        ],
        [
            "tokocrypto",
            "BTC",
            "Bitcoin",
            "0.001",
            "1500000000",
            "IDR",
            "2025-01-02",
            "crypto",
            "false",
        ],
    ]

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADERS)
        writer.writerows(sample_rows)

    return path


def import_portfolio_from_csv(csv_path: str | Path) -> dict[str, Any]:
    """Import portfolio positions from CSV file."""
    path = Path(csv_path)

    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")

    positions = []
    position_id = 1

    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            is_ef = row.get("is_emergency_fund", "false").lower() in ("true", "1", "yes")

            position = {
                "id": f"POS-{position_id:03d}",
                "platform": row.get("platform", "").strip().lower(),
                "ticker": row.get("ticker", "").strip().upper(),
                "name": row.get("name", "").strip(),
                "quantity": float(row.get("quantity", 0)),
                "avg_price": float(row.get("avg_price", 0)),
                "currency": row.get("currency", "IDR").strip().upper(),
                "type": row.get("type", "stock").strip().lower(),
                "is_emergency_fund": is_ef,
                "purchase_date": row.get("purchase_date", datetime.now().strftime("%Y-%m-%d")),
                "last_price": None,
                "last_updated": None,
            }

            positions.append(position)
            position_id += 1

    portfolio = {
        "positions": positions,
        "metadata": {
            "last_updated": datetime.now().isoformat(),
            "total_positions": len(positions),
            "base_currency": "IDR",
            "usd_idr_rate": None,
            "imported_from": str(path),
        },
    }

    return portfolio


def export_portfolio_to_csv(portfolio: dict[str, Any], output_path: str | Path) -> Path:
    """Export portfolio positions to CSV file."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    positions = portfolio.get("positions", [])

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADERS)

        for pos in positions:
            row = [
                pos.get("platform", ""),
                pos.get("ticker", ""),
                pos.get("name", ""),
                pos.get("quantity", 0),
                pos.get("avg_price", 0),
                pos.get("currency", "IDR"),
                pos.get("purchase_date", ""),
                pos.get("type", "stock"),
                "true" if pos.get("is_emergency_fund") else "false",
            ]
            writer.writerow(row)

    return path


def save_portfolio_json(portfolio: dict[str, Any], output_path: str | Path) -> Path:
    """Save portfolio to JSON file."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    portfolio["metadata"]["last_updated"] = datetime.now().isoformat()

    with path.open("w", encoding="utf-8") as f:
        json.dump(portfolio, f, indent=2, ensure_ascii=False)

    return path


def load_portfolio_json(json_path: str | Path) -> dict[str, Any]:
    """Load portfolio from JSON file."""
    path = Path(json_path)

    if not path.exists():
        raise FileNotFoundError(f"Portfolio file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
