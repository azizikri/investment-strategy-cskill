# PROJECT KNOWLEDGE BASE

**Generated:** 2026-01-05T01:51+07:00  
**Commit:** b1e1613  
**Branch:** main

## OVERVIEW

Investment strategy execution assistant for Indonesian investors—daily/weekly/monthly workflows with live price tracking, risk metrics, and phase-aware portfolio management. Python 3.11+ with `uv`.

## STRUCTURE

```
investment-strategy-cskill/
├── scripts/              # All execution logic (entry points + modules)
│   ├── daily_checkin.py  # Entry: uv run python scripts/daily_checkin.py
│   ├── weekly_review.py  # Entry: uv run python scripts/weekly_review.py
│   ├── monthly_strategy.py
│   ├── init_portfolio.py
│   ├── calculators/      # Risk metrics, Kelly, rebalancing
│   ├── data_fetchers/    # Yahoo Finance, CoinGecko, FX APIs
│   ├── trackers/         # Portfolio, Journal, Emergency Fund state
│   └── utils/            # Formatters, validators, CSV handlers
├── data/                 # User data (JSON/CSV) - gitignore-worthy
├── references/           # Methodology docs (not code)
├── templates/            # Output templates (markdown)
├── tests/                # pytest suite
├── SKILL.md              # Claude skill definition (activation keywords)
└── pyproject.toml        # uv + hatchling config
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Run daily portfolio check | `scripts/daily_checkin.py` | `uv run python scripts/daily_checkin.py` |
| Run weekly review | `scripts/weekly_review.py` | Performance vs IHSG/S&P500 |
| Run monthly strategy | `scripts/monthly_strategy.py` | Phase detection + payday plan |
| Calculate risk metrics | `scripts/calculators/risk_metrics.py` | Sharpe, Sortino, MaxDD, CAGR |
| Kelly position sizing | `scripts/calculators/position_sizer.py` | Half-Kelly approach |
| Fetch stock prices | `scripts/data_fetchers/stock_fetcher.py` | Yahoo Finance (yfinance) |
| Fetch crypto prices | `scripts/data_fetchers/crypto_fetcher.py` | CoinGecko API (no key) |
| Fetch USD/IDR rate | `scripts/data_fetchers/fx_fetcher.py` | Multiple fallback sources |
| Track portfolio state | `scripts/trackers/portfolio_tracker.py` | Reads/writes `data/portfolio.json` |
| Track emergency fund | `scripts/trackers/ef_tracker.py` | Phase 1→2 transition logic |
| Log trades | `scripts/trackers/journal_manager.py` | `data/journal.json` |
| Format output tables | `scripts/utils/formatters.py` | Currency, percentage, tables |
| Validate inputs | `scripts/utils/validators.py` | Tickers, platforms, dates |
| Run tests | `tests/` | `uv run pytest` |
| Customize skill | `references/customization.md` | Phase targets, platforms |
| Understand methodology | `references/methodology.md` | Investment frameworks |

## CONVENTIONS

### Execution
- **ALWAYS** run via `uv run python scripts/<script>.py` (no manual venv activation)
- Each script has `if __name__ == "__main__":` block for direct execution
- Scripts import from sibling modules via `from scripts.X import Y`

### Data Files
- All user data in `data/` directory (JSON format)
- `portfolio.json`: Master holdings record
- `journal.json`: Trade log with thesis/sentiment
- `ef_progress.json`: Emergency fund tracking
- **DO NOT** commit `data/` contents (user-specific)

### API Design
- Fetchers return dicts with `"error"` key on failure (never raise)
- All prices normalized to IDR or original currency
- CoinGecko symbols: uppercase (`BTC`, `ETH`)
- Yahoo Finance tickers: with suffix (`BBCA.JK`, `NVDA`)

### Risk Metrics
- Returns assumed to be **daily simple returns**
- 252 trading days/year constant
- Risk-free rate default: 5% (Indonesian context)

### Formatting
- Currency: IDR uses `Rp` prefix, comma thousands, no decimals
- Percentages: Always include `%` suffix
- Tables: Box-drawing characters via `format_table()`

## ANTI-PATTERNS (THIS PROJECT)

| Pattern | Why Forbidden |
|---------|---------------|
| `requirements.txt` | Use `uv sync` from `pyproject.toml` instead |
| Manual venv activation | Use `uv run` always |
| Hardcoded file paths | Use `Path(__file__).parent.parent / "data"` |
| API keys in code | All APIs are key-free by design (see DECISIONS.md) |
| Rebalancing < 5% drift | Noise threshold—only alert at ≥5% absolute drift |
| `raise` in fetchers | Return `{"error": "msg"}` dict instead |

## UNIQUE STYLES

- **Phase-aware logic**: Phase 1 (EF < 6mo expenses) enforces 80/20 rule
- **Half-Kelly sizing**: Never full Kelly—divide by 2 for conservative sizing
- **No single position > 10%**: Hard cap regardless of Kelly output
- **IDX stock suffix**: Always `.JK` (e.g., `BBCA.JK`, `TLKM.JK`)

## COMMANDS

```bash
# Setup
uv sync                                    # Install dependencies
uv run python scripts/init_portfolio.py   # Initialize data files

# Daily workflows
uv run python scripts/daily_checkin.py    # 2-min portfolio snapshot
uv run python scripts/weekly_review.py    # Performance vs benchmarks
uv run python scripts/monthly_strategy.py # Full analysis + payday plan

# Testing
uv run pytest                             # Run all tests
uv run pytest -v tests/test_calculators.py # Specific test file
uv run pytest --cov=scripts               # With coverage
```

## NOTES

- **No CI/CD**: Personal tool—tests run manually via `uv run pytest`
- **No `.gitignore`**: Add one if forking (exclude `data/`, `__pycache__/`)
- **`scripts/` naming**: Intentional—not `src/` per DECISIONS.md
- **SKILL.md**: Contains Claude activation keywords and full feature docs
- **IDR context**: Default currency, risk-free rate (5%), platform names (Bibit, Stockbit, Gotrade, Tokocrypto)
