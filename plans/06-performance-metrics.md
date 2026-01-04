# Module 06: Analytics & KPIs
**Document Version:** 1.2.0
**Last Updated:** January 3, 2026

## 1. The Measurement Mandate
In professional finance, we don't just ask "Did I make money?" We ask "How much risk did I take to make that money, and did I beat the market after costs and inflation?" Measurement is the only way to distinguish between "Skill" and "Luck."

---

## 2. Return Metrics (The "What")
### A. CAGR (Compound Annual Growth Rate)
The geometric progression ratio that provides a constant rate of return over the time period.
$$CAGR = \left( \frac{EV}{BV} \right)^{\frac{1}{n}} - 1$$
- *Note:* Always use CAGR for comparisons longer than 1 year to account for compounding.

### B. TWR (Time-Weighted Return)
TWR eliminates the impact of your IDR 7.2M monthly deposits. It tells you how well your *investment choices* are performing.
- **Formula:** $TWR = (1 + r_1) \times (1 + r_2) \times ... \times (1 + r_n) - 1$.
- **Why it matters:** If you deposit a large sum right before a market rally, your bank balance will explode, but that wasn't your "skill"—it was just timing. TWR measures the skill.

### C. MWR (Money-Weighted Return)
Also known as Internal Rate of Return (IRR). It accounts for the timing of your cash flows. Use this to see how your *actual wealth* is growing.

---

## 3. Risk-Adjusted Metrics (The "Quality")
### A. Sharpe Ratio (The Benchmark)
$$Sharpe = \frac{R_p - R_f}{\sigma_p}$$
- $R_p$: Portfolio Return.
- $R_f$: Risk-Free Rate (e.g., 6.5% for Indonesian 10Y Bonds).
- $\sigma_p$: Annualized Standard Deviation.
- **Target:** > 1.0 is the goal for most professionals.

### B. Sortino Ratio (The Professional's Choice)
Unlike Sharpe, Sortino only penalizes **Downside Deviation**.
- Why? Because upside volatility (prices going up fast) is actually good.
- **Formula:** $Sortino = (R_p - R_f) / \sigma_{downside}$
- **Target:** > 2.0 is considered institutional quality.

### C. Information Ratio (IR)
Measures the consistency of your "Alpha."
$$IR = \frac{R_p - R_b}{\text{Tracking Error}}$$
- $R_b$: Benchmark return (S&P 500).
- **Tracking Error:** The volatility of your outperformance.
- **Interpretation:** An IR of 0.5 is good; 1.0 is exceptional. It shows you aren't just "lucky" once, but consistently better than the index.

---

## 4. The Math of Compounding & Inflation
Returns in a vacuum are useless. You must account for the erosion of purchasing power.

### A. Real Rate of Return
$$\text{Real Return} = \frac{1 + \text{Nominal Return}}{1 + \text{Inflation Rate}} - 1$$
- If your portfolio returns 10% but IDR inflation is 5%, your "Real" return is only ~4.76%.
- **Institutional Rule:** Always measure your progress in **Real Dollars** (or USD for global assets) to ensure your future buying power is actually growing.

### B. The Rule of 72
A quick way to estimate how long it takes to double your money.
- **Formula:** $72 / \text{Annual Return \%} = \text{Years to Double}$.
- At 10% return, your money doubles every 7.2 years. At 15%, it's 4.8 years.

---

## 5. Risk Metrics: Measuring the "Cliff"
### A. Value at Risk (VaR)
Estimates the maximum loss over a given time period.
- **Calculation:** $\text{Portfolio Value} \times \text{Confidence Level (Z-score)} \times \sigma$.
- *Example:* A 95% 1-day VaR of IDR 2,000,000 means that on any given day, there is only a 5% chance you will lose more than 2M.

### B. Conditional VaR (Expected Shortfall)
VaR tells you the *limit* of normal losses. CVaR tells you "If the limit is broken, how bad will it be?" It measures the "Tail Risk" or the risk of a black swan event (like a flash crash).

### C. Maximum Drawdown (MaxDD)
The distance from the highest peak to the lowest valley.
- **Metric of Pain:** MaxDD is the ultimate measure of your psychological limit.
- **Institutional Rule:** If your MaxDD exceeds your "Risk Tolerance" defined in your IPS (Module 07), you must immediately de-risk.

---

## 6. Benchmarking: The "Sincere" Mirror
Retail investors often "cherry-pick" benchmarks. You must be honest.
- **If you own 100% US Tech:** Benchmark against **QQQ**.
- **If you own a Balanced Portfolio:** Benchmark against **60% VTI / 40% BND**.
- **If you are Indonesian-centric:** Benchmark against the **IHSG (Composite Index)**.

---

## 7. Performance Attribution (The "Why")
Institutions use the **Brinson-Fachler Model** to decompose returns into:
1.  **Allocation Effect:** Did you pick the right sectors? (e.g., being overweight Tech).
2.  **Selection Effect:** Did you pick the right stocks within those sectors? (e.g., picking Nvidia over Intel).
3.  **Interaction Effect:** The synergy between allocation and selection.
4.  **Currency Effect:** Since you invest in USD but live in IDR, this is huge. If the USD strengthens 10%, your Gotrade portfolio grows 10% in IDR terms even if the stocks stay flat.

---

## 8. KPI Dashboard for Personal Use
Create a table and update it every 6 months:

| Metric | Last 6 Months | Last 3 Years | Benchmark |
| :--- | :--- | :--- | :--- |
| **CAGR** | [%] | [%] | [%] |
| **Sharpe Ratio** | [Ratio] | [Ratio] | [Ratio] |
| **Max Drawdown** | [%] | [%] | [%] |
| **Alpha (Excess)** | [%] | [%] | - |
| **Beta (Market)** | [Ratio] | [Ratio] | 1.0 |

---

## 9. Common Mistakes to Avoid
- **Annualizing Short-Term Returns:** "I made 5% this week, so I'll make 260% this year." (Wrong. Markets are mean-reverting).
- **Ignoring Slippage & Fees:** You must subtract every transaction fee and tax from your returns to get the true "Net" result.
- **Survivorship Bias:** Only counting the stocks you still own and forgetting the ones you sold at a loss.

## 10. Implementation Guide
1. Calculate your portfolio's **Standard Deviation** over the last 12 months using Excel/Sheets (`=STDEV`).
2. Calculate your **Sharpe Ratio** using the Indo 10Y Bond rate as the risk-free rate.
3. If your Sharpe is < 0.5, your strategy is essentially "Gambling"—consider moving more to the Core.

---
**Next Module:** `07-governance-compliance.md` - Your investment rules.
