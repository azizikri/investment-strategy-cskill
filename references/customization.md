# Customization & Adaptation Guide

The `investment-strategy-cskill` is designed to be flexible. Here is how you can adapt it to your specific needs.

## 1. Customizing Asset Classes

By default, the skill supports `stock`, `crypto`, `money_market`, and `gold`. You can add more in the `scripts/utils/validators.py` file.

**Adding a new class (e.g., Real Estate):**
1.  Add `real_estate` to the `VALID_ASSET_TYPES` list.
2.  Update your `portfolio.json` with positions of this type.
3.  The skill will automatically include it in the "Other" category in tables unless you define a specific formatting rule in `scripts/utils/formatters.py`.

## 2. Adjusting Rebalancing Thresholds

The 5% drift threshold is a common standard, but you might prefer 3% or 10%.

*   **To Change**: Modify the `REBALANCE_THRESHOLD` constant in `scripts/calculators/rebalancer.py`.
*   **Per-Asset Thresholds**: You can also add a `threshold` key to individual assets in `portfolio.json` to override the global setting.

## 3. Extending the Due Diligence Checklist

The `analyze <ticker>` command uses a checklist defined in `templates/due_diligence.md`.

*   **How to customize**: Edit that markdown file to include your own criteria (e.g., specific ESG scores, management quality checks, or technical indicators).

## 4. Custom Currencies

The skill defaults to `IDR`. If you live in another country or prefer `USD` as your base currency:

1.  Update the `base_currency` in `data/portfolio.json`.
2.  The `fx_fetcher.py` will automatically switch its conversion logic to use your new base currency as the target.

## 5. Adding New Data Fetchers

If you have assets on a platform not covered by Yahoo Finance or CoinGecko (e.g., a specific Indonesian P2P lending platform):

1.  Create a new file in `scripts/data_fetchers/`.
2.  Implement a `fetch(ticker)` method.
3.  Register the fetcher in `scripts/data_fetchers/__init__.py`.
