"""Portfolio initialization and setup workflows."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

__all__ = [
    "initialize_portfolio",
    "create_sample_data",
    "setup_directories",
]


SKILL_ROOT = Path(__file__).parent.parent
DATA_DIR = SKILL_ROOT / "data"
TEMPLATES_DIR = SKILL_ROOT / "templates"


def setup_directories() -> dict[str, Path]:
    """Create required directory structure."""
    directories = {
        "data": DATA_DIR,
        "templates": TEMPLATES_DIR,
    }

    for name, path in directories.items():
        path.mkdir(parents=True, exist_ok=True)

    return directories


def create_sample_portfolio() -> dict[str, Any]:
    """Create sample portfolio data for testing."""
    return {
        "positions": [
            {
                "id": "POS-001",
                "platform": "bibit",
                "ticker": "RDPU-SUCORINVEST",
                "name": "Sucorinvest Money Market Fund",
                "quantity": 12500000,
                "avg_price": 1.0,
                "currency": "IDR",
                "type": "money_market",
                "is_emergency_fund": True,
                "purchase_date": "2025-01-01",
                "last_price": 1.001,
                "last_updated": datetime.now().isoformat(),
            },
            {
                "id": "POS-002",
                "platform": "stockbit",
                "ticker": "BBCA.JK",
                "name": "Bank Central Asia",
                "quantity": 10,
                "avg_price": 9500,
                "currency": "IDR",
                "type": "stock",
                "is_emergency_fund": False,
                "purchase_date": "2025-01-02",
                "last_price": 9650,
                "last_updated": datetime.now().isoformat(),
            },
            {
                "id": "POS-003",
                "platform": "gotrade",
                "ticker": "NVDA",
                "name": "NVIDIA Corporation",
                "quantity": 0.5,
                "avg_price": 140,
                "currency": "USD",
                "type": "stock",
                "is_emergency_fund": False,
                "purchase_date": "2025-01-02",
                "last_price": 148.5,
                "last_updated": datetime.now().isoformat(),
            },
            {
                "id": "POS-004",
                "platform": "tokocrypto",
                "ticker": "BTC",
                "name": "Bitcoin",
                "quantity": 0.001,
                "avg_price": 1500000000,
                "currency": "IDR",
                "type": "crypto",
                "is_emergency_fund": False,
                "purchase_date": "2025-01-02",
                "last_price": 1650000000,
                "last_updated": datetime.now().isoformat(),
            },
        ],
        "metadata": {
            "last_updated": datetime.now().isoformat(),
            "total_positions": 4,
            "base_currency": "IDR",
            "usd_idr_rate": 15900,
        },
    }


def create_sample_journal() -> dict[str, Any]:
    """Create sample trade journal data."""
    return {
        "trades": [
            {
                "id": "TRD-2025-001",
                "timestamp": datetime.now().isoformat(),
                "platform": "stockbit",
                "ticker": "BBCA.JK",
                "action": "BUY",
                "quantity": 10,
                "price": 9500,
                "currency": "IDR",
                "total_value": 95000,
                "fees": 190,
                "thesis": "Strong fundamentals, Q4 earnings catalyst expected",
                "tags": ["banking", "blue-chip", "dividend"],
                "notes": "Entry per plans/03-due-diligence.md checklist",
                "sentiment": "confident",
                "market_condition": "neutral",
                "phase": 1,
            }
        ],
        "metadata": {
            "last_updated": datetime.now().isoformat(),
            "total_trades": 1,
            "total_buys": 1,
            "total_sells": 0,
        },
    }


def create_sample_ef_progress() -> dict[str, Any]:
    """Create sample emergency fund progress data."""
    return {
        "target_amount": 36000000,
        "target_months": 6,
        "monthly_expenses": 6000000,
        "current_balance": 12500000,
        "months_covered": 2.08,
        "progress_percent": 34.7,
        "phase": 1,
        "last_updated": datetime.now().isoformat(),
        "history": [
            {
                "date": "2025-01-01",
                "balance": 10000000,
                "months_covered": 1.67,
            },
            {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "balance": 12500000,
                "months_covered": 2.08,
            },
        ],
    }


def create_csv_template() -> str:
    """Generate CSV template content."""
    lines = [
        "platform,ticker,name,quantity,avg_price,currency,purchase_date,type,is_emergency_fund",
        "bibit,RDPU-SUCORINVEST,Sucorinvest Money Market Fund,12500000,1.0,IDR,2025-01-01,money_market,true",
        "stockbit,BBCA.JK,Bank Central Asia,10,9500,IDR,2025-01-02,stock,false",
        "gotrade,NVDA,NVIDIA Corporation,0.5,140,USD,2025-01-02,stock,false",
        "tokocrypto,BTC,Bitcoin,0.001,1500000000,IDR,2025-01-02,crypto,false",
    ]
    return "\n".join(lines)


def create_sample_data(overwrite: bool = False) -> dict[str, Path]:
    """Create all sample data files."""
    setup_directories()

    created_files: dict[str, Path] = {}

    portfolio_path = DATA_DIR / "portfolio.json"
    if not portfolio_path.exists() or overwrite:
        with portfolio_path.open("w", encoding="utf-8") as f:
            json.dump(create_sample_portfolio(), f, indent=2, ensure_ascii=False)
        created_files["portfolio"] = portfolio_path

    journal_path = DATA_DIR / "journal.json"
    if not journal_path.exists() or overwrite:
        with journal_path.open("w", encoding="utf-8") as f:
            json.dump(create_sample_journal(), f, indent=2, ensure_ascii=False)
        created_files["journal"] = journal_path

    ef_path = DATA_DIR / "ef_progress.json"
    if not ef_path.exists() or overwrite:
        with ef_path.open("w", encoding="utf-8") as f:
            json.dump(create_sample_ef_progress(), f, indent=2, ensure_ascii=False)
        created_files["ef_progress"] = ef_path

    csv_path = DATA_DIR / "portfolio_template.csv"
    if not csv_path.exists() or overwrite:
        csv_path.write_text(create_csv_template(), encoding="utf-8")
        created_files["csv_template"] = csv_path

    sample_json = TEMPLATES_DIR / "sample_portfolio.json"
    if not sample_json.exists() or overwrite:
        with sample_json.open("w", encoding="utf-8") as f:
            json.dump(create_sample_portfolio(), f, indent=2, ensure_ascii=False)
        created_files["sample_portfolio"] = sample_json

    return created_files


def initialize_portfolio(include_sample_data: bool = True) -> dict[str, Any]:
    """Initialize portfolio system with optional sample data."""
    directories = setup_directories()

    result = {
        "directories_created": [str(p) for p in directories.values()],
        "files_created": [],
        "status": "success",
    }

    if include_sample_data:
        files = create_sample_data(overwrite=False)
        result["files_created"] = [str(p) for p in files.values()]

    empty_templates = {
        "portfolio": {"positions": [], "metadata": {"last_updated": None, "base_currency": "IDR"}},
        "journal": {"trades": [], "metadata": {"last_updated": None}},
        "ef_progress": {"target_amount": 0, "current_balance": 0, "history": []},
    }

    for name, template in empty_templates.items():
        path = DATA_DIR / f"{name}.json"
        if not path.exists():
            with path.open("w", encoding="utf-8") as f:
                json.dump(template, f, indent=2)
            result["files_created"].append(str(path))

    return result


def get_init_summary() -> str:
    """Generate initialization summary message."""
    return """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📁 PORTFOLIO INITIALIZED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Created directories:
  • data/          - Portfolio, journal, EF tracking
  • templates/     - Sample files and templates

Created files:
  • data/portfolio.json       - Your positions
  • data/journal.json         - Trade journal
  • data/ef_progress.json     - Emergency Fund tracking
  • data/portfolio_template.csv - CSV import template

Next steps:
  1. Edit data/portfolio_template.csv with your positions
  2. Run "import portfolio" to load your data
  3. Run "daily check" to see your portfolio

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""


if __name__ == "__main__":
    result = initialize_portfolio(include_sample_data=True)
    print(get_init_summary())
    print(f"Created {len(result['files_created'])} files")
