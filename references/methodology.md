# Methodology Reference

This document explains the mathematical formulas and logic used by the calculators in the `investment-strategy-cskill`.

## 1. Position Sizing: The Kelly Criterion

We use the Kelly Criterion to determine the percentage of capital to allocate to a single trade.

**Formula:**
`f* = (p * b - q) / b`

Where:
*   `f*`: The fraction of the current bankroll to wager.
*   `p`: Probability of a win (Win Rate).
*   `q`: Probability of a loss (1 - p).
*   `b`: Odds (Net Profit / Net Loss).

**Implementation:**
The `size position` command uses your historical win rate from `journal.json` as the default `p`. You can override this manually for specific high-conviction trades.

*Reference: `plans/02-risk-management.md`*

## 2. Risk-Adjusted Performance

We calculate three primary metrics to evaluate performance.

### Sharpe Ratio
Measures the average return earned in excess of the risk-free rate per unit of volatility.
`Sharpe = (Portfolio Return - Risk-Free Rate) / Portfolio Standard Deviation`

### Sortino Ratio
A variation of the Sharpe ratio that only considers downside deviation (returns below a target or minimum acceptable return).
`Sortino = (Portfolio Return - Risk-Free Rate) / Downside Deviation`

### Maximum Drawdown (MaxDD)
The maximum observed loss from a peak to a trough of a portfolio, before a new peak is attained.
`MaxDD = (Trough Value - Peak Value) / Peak Value`

*Reference: `plans/06-performance-metrics.md`*

## 3. Allocation Drift & Rebalancing

We use a **5% Absolute Threshold** for rebalancing.

**Logic:**
If Target Allocation = 40% and Current Allocation = 46%, the drift is 6%. Since 6% > 5%, a rebalancing alert is triggered.

The skill calculates the exact amount of "Drift IDR" to help you decide how much to sell or buy to return to the target.

*Reference: `plans/04-portfolio-construction.md`*

## 4. Phase Detection Logic

The skill monitors your Emergency Fund (EF) to determine your investment phase.

*   **Phase 1 (Foundation Building)**: 
    *   Trigger: EF < 6 months of expenses.
    *   Instruction: 80% of new savings must go to EF. Only 20% to investments.
*   **Phase 2 (Wealth Accumulation)**:
    *   Trigger: EF >= 6 months of expenses.
    *   Instruction: 100% of new savings can go to investments.

The `phase check` command automatically evaluates this based on `ef_progress.json`.

*Reference: `plans/09-emergency-fund.md`*

## 5. Benchmarking

We compare your portfolio's weekly and monthly performance against two benchmarks:
1.  **IHSG (^JKSE)**: For Indonesian equity performance.
2.  **S&P 500 (^GSPC)**: For global equity performance.

Total Return includes price appreciation + dividends (where data is available).
