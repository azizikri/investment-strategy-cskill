# Architectural Decisions

This document records the key technical decisions made during the design and development of the `investment-strategy-cskill`.

## 1. Single Skill vs. Suite

**Decision**: Implement as a single skill with multiple operating modes.
**Reasoning**: 
*   **Workflow Integration**: Investing is a unified workflow. Separate skills for "portfolio tracking" and "risk management" would force the user to switch contexts unnecessarily.
*   **Data Sharing**: All modes share the same `portfolio.json` and `journal.json` data. A single skill simplifies file locking and data integrity.
*   **User Experience**: It's easier for a user to remember one skill name and use different commands than to manage multiple installations.

## 2. Python + `uv` vs. Traditional `pip`/`venv`

**Decision**: Standardize on `uv` for package management.
**Reasoning**:
*   **Speed**: `uv` is significantly faster at resolving and installing dependencies.
*   **Simplicity**: `uv run` abstracts away the need for users to manually activate virtual environments, which is a common friction point for non-developers.
*   **Reproducibility**: The `uv.lock` file ensures that every installation of the skill uses the exact same library versions.

## 3. Local JSON for Data Storage

**Decision**: Store all user data in local JSON files.
**Reasoning**:
*   **Privacy**: Investment data is highly sensitive. Local storage ensures the user has 100% control.
*   **Portability**: JSON is human-readable and easy to back up or migrate to other tools.
*   **Simplicity**: Avoids the overhead and setup complexity of a database (like SQLite or PostgreSQL) for what is essentially a small amount of personal data.

## 4. Yahoo Finance & CoinGecko (No Keys)

**Decision**: Prioritize public APIs that do not require registration or API keys.
**Reasoning**:
*   **Zero Friction**: Users can install and start using the skill in seconds without signing up for external services.
*   **Maintenance**: Reduces the risk of the skill breaking due to expired keys or tier changes.
*   **Cost**: Ensures the skill remains 100% free to operate.

## 5. 5% Absolute Threshold for Rebalancing

**Decision**: Use a fixed 5% absolute drift threshold as the default trigger.
**Reasoning**:
*   **Signal vs. Noise**: Small fluctuations (1-2%) are market noise. Rebalancing too often increases transaction fees and taxes. 5% is a widely accepted "Wall Street" standard for meaningful drift.

## 6. Directory Structure

**Decision**: Separate `scripts/` (logic) from `data/` (user data) and `references/` (docs).
**Reasoning**: 
*   Follows standard software engineering patterns (Separation of Concerns).
*   Allows the user to easily back up just the `data/` folder.
