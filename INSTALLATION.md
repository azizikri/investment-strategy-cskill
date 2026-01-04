# Installation Guide

Follow these steps to set up the **Investment Strategy Execution Assistant** on your machine.

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

1.  **Python 3.11+**:
    *   Verify with: `python --version`
2.  **uv**:
    *   The modern Python package manager.
    *   Installation: `curl -LsSf https://astral.sh/uv/install.sh | sh` (macOS/Linux) or `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"` (Windows).

## 🚀 Step-by-Step Installation

### 1. Project Setup

Navigate to the project directory and install dependencies:

```bash
cd /Users/azizikri/notes/finance/investment-strategy-cskill
uv sync
```

This will create a `.venv` directory and install all required packages (yfinance, requests, pandas, numpy).

### 2. Data Initialization

Run the initialization script to create the necessary directory structure and template files:

```bash
uv run python scripts/init_portfolio.py
```

This creates:
*   `data/portfolio.json`
*   `data/journal.json`
*   `data/ef_progress.json`
*   `data/portfolio_template.csv`

### 3. Importing Your Data

You have two ways to add your initial positions:

**Option A: Interactive (Recommended for a few items)**
```bash
uv run python scripts/trackers/portfolio_tracker.py add BBCA.JK 10 9500 stockbit
```

**Option B: Bulk Import (Recommended for existing portfolios)**
1.  Open `data/portfolio_template.csv` in Excel or Google Sheets.
2.  Fill in your holdings.
3.  Save the CSV.
4.  Run the import command:
    ```bash
    uv run python scripts/utils/csv_handler.py import
    ```

### 4. Configuration

To track your Emergency Fund progress:
```bash
uv run python scripts/trackers/ef_tracker.py setup
```
You will be prompted for:
*   Monthly expenses (IDR)
*   Target months (e.g., 6)
*   Current starting balance

## ✅ Verification

Run the daily check-in to verify everything is working correctly:

```bash
uv run python scripts/daily_checkin.py
```

If successful, you should see a formatted table with live prices from Yahoo Finance and CoinGecko.

## 🛠️ Troubleshooting

### Common Issues

**1. "ModuleNotFoundError"**
*   **Cause**: Running python directly instead of through `uv run`.
*   **Fix**: Always use `uv run python script.py`.

**2. Connection Error / Rate Limits**
*   **Cause**: Too many requests to Yahoo Finance or CoinGecko.
*   **Fix**: The skill has built-in caching. Wait 60 seconds and try again.

**3. "Ticker Not Found"**
*   **Cause**: Incorrect ticker format.
*   **Fix**: 
    *   IDX Stocks: Must end in `.JK` (e.g., `ASII.JK`).
    *   US Stocks: Standard symbol (e.g., `AAPL`).
    *   Crypto: Base symbol (e.g., `BTC`).

## 🔄 Updates

To update the skill to the latest version:
```bash
git pull
uv sync
```
