# Module 03: Institutional Due Diligence Process
**Document Version:** 1.2.0
**Last Updated:** January 3, 2026

## 1. The Due Diligence Mandate
Due Diligence (DD) is the rigorous process of verifying the "Alpha" thesis before committing capital. An institutional-grade DD must be objective, skeptical, and focused on finding reasons *not* to invest.

---

## 2. Fundamental Analysis Deep Dive
### A. The "Big Three" Financial Statements
1.  **Income Statement:** Focus on **Revenue Quality**. 
    - Is growth organic (new customers) or inorganic (acquisitions)? 
    - Is **Operating Leverage** present? (Profits growing faster than revenue).
2.  **Balance Sheet:** Focus on **Solvency**.
    - **Altman Z-Score:** A formula to predict bankruptcy. If Z > 3, the company is safe.
    - **Net Debt / EBITDA:** Should ideally be < 3.0.
3.  **Cash Flow Statement:** The source of truth.
    - **Piotroski F-Score:** A 9-point scale to evaluate the financial strength of a firm.

### B. Moat Analysis (Competitive Advantage)
Rate the company (1-5) on **Porter’s Five Forces**:
- **Threat of New Entrants:** (High barriers to entry?)
- **Bargaining Power of Suppliers:** (Is the company dependent on one vendor?)
- **Bargaining Power of Buyers:** (Can customers easily switch?)
- **Threat of Substitutes:** (Is the product essential?)
- **Competitive Rivalry:** (Is it a "race to the bottom" on price?)

---

## 3. The 5-Step DCF Model: A Worked Example
Let's value a hypothetical Tech Company ($TECH).

### Step 1: Project Free Cash Flows (FCF)
- Current FCF: $100M.
- Expected Growth: 15% for 5 years, then 10% for the next 5.
- Year 1 FCF: $115M | Year 5 FCF: $201M.

### Step 2: Calculate WACC (The Discount Rate)
- Risk-free rate (Indo 10Y Bond): 6.5%.
- Equity Risk Premium: 5%.
- **WACC** (Simplified): 11.5%.

### Step 3: Terminal Value (TV)
- Growth slows to 3% forever after Year 10.
- Formula: $TV = (FCF_{10} \times (1+g)) / (WACC - g)$
- $TV = (521 \times 1.03) / (0.115 - 0.03) = \$6.3B$.

### Step 4: Discount to Present Value (PV)
- Discount all future FCFs and the TV back to today's dollars using the WACC.
- $PV = \text{Sum of all discounted cash flows} = \$4.2B$.

### Step 5: Equity Value Per Share
- **Equity Value** = $PV + \text{Cash} - \text{Debt} = 4.2B + 500M - 200M = \$4.5B$.
- If there are 100M shares, the **Intrinsic Value is $45.00**.
- **Market Price:** If it's trading at $30, you have a **33% Margin of Safety**.

---

## 4. Alternative Data for the Modern Investor
Institutions use satellites and credit card data. You can use:
- **Google Trends:** Is search volume for the product increasing?
- **App Annie:** Are the company's mobile app downloads growing or shrinking?
- **Web Traffic (SimilarWeb):** Is the company's website traffic healthy?
- **Ad Library (Meta):** How much is the company spending on ads? High spend with low growth is a red flag.

---

## 5. Red Flags: The "No-Go" Signals
Institutional analysts look for reasons to say "No."
1.  **Auditor Resignation:** If an auditor quits, sell immediately.
2.  **Frequent CFO Changes:** 3 CFOs in 5 years is a sign of accounting manipulation.
3.  **Related Party Transactions:** Management "renting" buildings they own back to the company.
4.  **Excessive Stock-Based Compensation (SBC):** If SBC is 20% of revenue, the management is working for themselves, not the shareholders.

---

## 6. Technical Analysis Framework
Institutions use technicals for **Execution Timing**, not for the investment thesis itself.

| Pattern | Meaning | Institutional Action |
| :--- | :--- | :--- |
| **Golden Cross** | 50MA crosses above 200MA. | Confirmation of a new Bull Trend. |
| **Cup and Handle** | Consolidation before a breakout. | Enter on the break of the "Handle" with high volume. |
| **RSI Divergence** | Price making new highs but RSI making lower highs. | Warning: Trend is losing strength. *Action: Tighten stops.* |

---

## 7. Macro Analysis & Market Regimes
You must identify the current "Market Regime" to decide how much risk to take.
1.  **Inflation Regime:** Commodities and Value stocks outperform. (Buy $INCO, $ADRO).
2.  **Growth Regime:** Low interest rates; Tech outperforms. (Buy $QQQ, $GOOGL).
3.  **Crisis Regime:** High volatility; Gold and Cash outperform. (Buy $XAU, $USD).

---

## 8. Scuttlebutt: The "Feet on the Ground" Research
Inspired by Philip Fisher. Don't just read spreadsheets; look at the world.
- **Product Experience:** Use the product daily. Is it getting better or worse?
- **Employee Sentiment:** Check Glassdoor. Is the culture innovative or toxic?
- **LinkedIn Hiring:** Is the company hiring for "AI" or "Cost-cutting" roles?

---

## 9. The 10-Point Institutional Scoring Matrix
Score every asset before entry:
1.  [ ] Revenue Growth > 15% (3-year avg).
2.  [ ] FCF / Net Income > 1.0 (Cash quality).
3.  [ ] ROIC > 15% (Capital efficiency).
4.  [ ] Net Debt / EBITDA < 2.0 (Solvency).
5.  [ ] CEO has > 5% equity stake (Skin in the game).
6.  [ ] RSI (14) is between 40 and 60 (Not overbought).
7.  [ ] P/E or P/S is below 5-year historical median.
8.  [ ] Company has a clearly defined "Moat."
9.  [ ] 50MA > 200MA (Bullish trend).
10. [ ] Market Cap < $500B (Room for growth).

**Score 8-10:** Strong Buy. | **Score 5-7:** Hold/Watchlist. | **Score < 5:** Sell/Avoid.

---

## 10. Common Mistakes to Avoid
- **Confirmation Bias:** Only seeking info that supports your thesis.
- **Ignoring the "Small Print":** Not reading the footnotes in the 10-K report.
- **Anchor Bias:** Thinking a stock is "cheap" just because it was higher last year.

## 11. Implementation Guide
1. Create a "Due Diligence" folder in your notes.
2. For your next stock pick, fill out the 10-point matrix.
3. Run the 5-step DCF calculation using a spreadsheet.

---
**Next Module:** `04-portfolio-construction.md` - Building the machine.
