# 📈 Investment Strategy Execution Assistant

Operationalize your investment framework into a disciplined, data-driven daily routine.

## 🚀 Overview

The **Investment Strategy Execution Assistant** (`investment-strategy-cskill`) is a comprehensive tool designed for Indonesian investors who want to move beyond spreadsheets and into professional-grade execution. It bridges your strategic documentation (`./plans/`) with your daily actions.

### Key Features

*   **Live Price Tracking**: Real-time valuations for IDX Stocks, US Stocks, and Crypto using Yahoo Finance and CoinGecko.
*   **Structured Journaling**: A JSON-based trade journal that captures your thesis, sentiment, and results.
*   **Professional Risk Metrics**: Automated calculation of Sharpe Ratio, Sortino Ratio, and Maximum Drawdown.
*   **Wall Street Workflows**: Daily, Weekly, and Monthly operating modes that enforce discipline.
*   **Phase-Aware Logic**: Specifically designed to track the transition from Phase 1 (Foundation) to Phase 2 (Wealth Accumulation).
*   **Automated Payday Planning**: Generates exact execution steps for Bibit, Stockbit, Gotrade, and Tokocrypto.

## 📦 Installation

This project uses `uv` for extremely fast and reliable Python package management.

### Prerequisites

*   Python 3.11 or higher
*   `uv` (Install via `curl -LsSf https://astral.sh/uv/install.sh | sh` or `brew install uv`)

### Setup

1.  **Clone the repository** (or navigate to the directory):
    ```bash
    cd investment-strategy-cskill/
    ```

2.  **Initialize the project**:
    ```bash
    uv init
    ```

3.  **Sync dependencies**:
    ```bash
    uv sync
    ```

4.  **Initialize your data**:
    ```bash
    uv run python scripts/init_portfolio.py
    ```

## 🛠️ Usage

This skill is designed to be used within the Claude interface or via the command line using `uv run`.

### Quick Commands

| Command | Frequency | Description |
| :--- | :--- | :--- |
| `daily check` | Daily | 2-min portfolio health check |
| `weekly review` | Weekly | Performance vs IHSG/S&P500 |
| `monthly strategy` | Monthly | Full analysis + Payday plan |
| `size position BBCA 9500` | As Needed | Kelly Criterion position sizer |
| `add trade` | As Needed | Log a new transaction with thesis |

## 📂 Project Structure

```text
investment-strategy-cskill/
├── SKILL.md                # Main skill documentation
├── scripts/                # Python execution logic
├── data/                   # Your persistent data (JSON/CSV)
├── references/             # Detailed methodology guides
├── templates/              # Markdown output templates
└── tests/                  # Integrity verification suite
```

## ⚖️ License

This project is licensed under the MIT License.

## 🤝 Contributing

This is a personal execution tool. If you wish to adapt it for your own use, please refer to `references/customization.md`.
