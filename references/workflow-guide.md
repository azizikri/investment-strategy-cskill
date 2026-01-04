# Workflow Guide

This guide outlines the standard operating procedures for using the `investment-strategy-cskill` modes effectively.

## 🌅 Daily Workflow (2-3 Minutes)

**When**: Every morning before market open or every evening.
**Command**: `daily check`

1.  **Review the Snapshot**: Check your total portfolio value and 24h change.
2.  **Check Allocation Status**: Look for any red `⚠️` or `🚨` icons indicating your allocation has drifted too far.
3.  **Monitor Emergency Fund**: See how much closer you are to your 6-month goal.
4.  **Today's Focus**: Read the contextual advice. For example, if it's a weekend, focus on research rather than trading.

## 📊 Weekly Review (15-20 Minutes)

**When**: Saturday morning or Sunday evening.
**Command**: `weekly review`

1.  **Benchmark Audit**: Compare your performance to IHSG and S&P 500. If you are significantly underperforming, investigate why.
2.  **Trade Journaling**: Log any trades from the week that you haven't recorded yet using `add trade`. Be honest about your thesis.
3.  **Review Sentiment**: Look at your "Sentiment" stats in the journal. Are you trading out of FOMO or discipline?
4.  **Prep for Next Week**: Check the "Upcoming Events" section for earnings calls or central bank meetings.

## 🗓️ Monthly Strategy (45-60 Minutes)

**When**: Last weekend of the month or Payday.
**Command**: `monthly strategy`

1.  **Full Metric Analysis**: Review your Sharpe and Sortino ratios. Look for trends—is your risk-adjusted return improving?
2.  **Phase Transition Check**: The skill will tell you if you've officially moved from Phase 1 to Phase 2.
3.  **Generate Payday Plan**: This is the most critical output. It tells you exactly how much IDR to transfer to Bibit, Stockbit, etc.
4.  **Update Strategy**: If your life circumstances have changed (e.g., higher expenses), run `setup emergency fund` to update your targets.

## 🛠️ On-Demand Commands

Use these during your active trading or research sessions:

*   **Before Buying**: Run `analyze <ticker>` to go through the due diligence checklist.
*   **Sizing the Entry**: Run `size position <ticker> <price>` to calculate the Kelly Criterion amount.
*   **Logging the Exit**: When you sell, use `add trade` and select `SELL`. Make sure to record the "Lessons Learned" in the notes.
