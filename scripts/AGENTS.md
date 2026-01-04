# scripts/ — Execution Logic

## OVERVIEW

All Python execution code. Four entry-point scripts + four submodules.

## STRUCTURE

```
scripts/
├── daily_checkin.py      # Entry: quick portfolio health
├── weekly_review.py      # Entry: benchmark comparison
├── monthly_strategy.py   # Entry: phase assessment + payday
├── init_portfolio.py     # Entry: first-time setup
├── calculators/          # Pure computation (no I/O)
├── data_fetchers/        # External API calls
├── trackers/             # Stateful file managers
└── utils/                # Formatting, validation, CSV
```

## WHERE TO LOOK

| Task | File | Key Exports |
|------|------|-------------|
| Portfolio snapshot | `daily_checkin.py` | `run_daily_checkin()`, `get_portfolio_snapshot()` |
| Benchmark comparison | `weekly_review.py` | `run_weekly_review()` |
| Payday execution plan | `monthly_strategy.py` | `run_monthly_strategy()` |
| Sharpe/Sortino/MaxDD | `calculators/risk_metrics.py` | `calculate_sharpe_ratio()`, `calculate_max_drawdown()` |
| Kelly sizing | `calculators/position_sizer.py` | `kelly_criterion()`, `calculate_position_size()` |
| Phase detection | `calculators/phase_detector.py` | `detect_phase()`, `get_allocation_target()` |
| Rebalance triggers | `calculators/rebalancer.py` | `check_allocation_drift()` |
| Stock prices | `data_fetchers/stock_fetcher.py` | `get_stock_price()`, `get_stock_prices_batch()` |
| Crypto prices | `data_fetchers/crypto_fetcher.py` | `get_crypto_price()`, `COMMON_CRYPTOS` |
| FX rates | `data_fetchers/fx_fetcher.py` | `get_usd_idr_rate()`, `convert_usd_to_idr()` |
| Portfolio CRUD | `trackers/portfolio_tracker.py` | `PortfolioTracker`, `Position` |
| Trade journal | `trackers/journal_manager.py` | `JournalManager`, `TradeEntry` |
| EF progress | `trackers/ef_tracker.py` | `EmergencyFundTracker` |
| Table output | `utils/formatters.py` | `format_table()`, `format_currency()` |
| Input checks | `utils/validators.py` | `validate_ticker()`, `ValidationError` |
| JSON/CSV I/O | `utils/csv_handler.py` | `save_portfolio_json()`, `export_portfolio_to_csv()` |

## CONVENTIONS

### Module Boundaries
- **calculators/**: Pure functions, no file I/O, no API calls
- **data_fetchers/**: API calls only, return dicts (never raise)
- **trackers/**: File I/O + state management, use `data/` directory
- **utils/**: Stateless helpers

### Import Style
```python
# Absolute imports from package root
from scripts.calculators import kelly_criterion
from scripts.data_fetchers import get_stock_price
from scripts.trackers import PortfolioTracker
from scripts.utils import format_currency
```

### Error Handling
- Fetchers: `return {"error": "message"}` on failure
- Trackers: Create files if missing, never crash
- Calculators: Return `0.0` or default for invalid input

## ANTI-PATTERNS

| Pattern | Why |
|---------|-----|
| Direct API exceptions | Fetchers catch and return error dict |
| Relative imports | Use `from scripts.X` always |
| Print statements | Return strings, let caller print |
| Hardcoded data paths | Use `SKILL_ROOT = Path(__file__).parent.parent` |
