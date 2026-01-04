# Module 02: Enterprise Risk Management Framework
**Document Version:** 1.2.0
**Last Updated:** January 3, 2026

## 1. The Institutional Risk Mandate
In professional investing, "Risk" is not just the possibility of losing money. It is the mathematical probability of failing to meet your long-term objectives. Our mandate is to maximize **Geometric Mean Return** while keeping the **Risk of Ruin** at zero.

---

## 2. The Mathematics of Drawdown: Why Survival is Everything
Most retail investors do not understand the asymmetrical nature of losses.
- To recover from a **10% loss**, you need an **11% gain**.
- To recover from a **25% loss**, you need a **33% gain**.
- To recover from a **50% loss**, you need a **100% gain**.
- To recover from a **90% loss**, you need a **900% gain**.

**Conclusion:** Small losses are easy to fix; large losses are catastrophic. Our framework is designed to prevent "The Big Loss" that resets years of compounding.

---

## 3. Position Sizing: The Kelly Criterion (Deep Dive)
The Kelly Criterion determines the percentage of your bankroll to wager on a specific opportunity to maximize long-term wealth.

### A. The Basic Formula
$$K\% = W - \frac{1 - W}{R}$$

Where:
- **K%:** % of portfolio to allocate.
- **W:** Win Probability (based on your back-tested hit rate).
- **R:** Win/Loss Ratio (Average profit / Average loss).

### B. Complex Kelly (Multiple Outcomes)
In the real world, you don't just "Win" or "Lose." You might have multiple scenarios.
**Formula:** $E[\ln(1 + Kx)]$ must be maximized.

*Example: Investment in a Tech IPO*
- 10% chance of 10x return ($+900\%$)
- 40% chance of 2x return ($+100\%$)
- 50% chance of 0x return ($-100\%$)
*Calculating this requires a numerical solver, but the result is usually much smaller than people expect.*

### C. The "Fractional Kelly" Standard
Professional traders almost never use "Full Kelly." They use **Quarter-Kelly (0.25x)** or **Half-Kelly (0.5x)**.
- **Why?** It drastically reduces the "Volatility of Wealth." 
- **Half-Kelly** provides roughly 75% of the growth of Full Kelly but with only 50% of the volatility. This is the "Sweet Spot" for institutional personal investing.

---

## 4. Volatility Targeting (Risk-Based Sizing)
Instead of allocating a fixed IDR 1,000,000 to every stock, we allocate based on the "volatility budget" of the position.

**Formula:**
$$\text{Position Size \%} = \frac{\text{Portfolio Volatility Target \%}}{\text{Asset Annualized Volatility \%}}$$

*Institutional Case Study:*
You want each position to contribute only 1% to your total portfolio risk.
- **Stock A (Blue Chip):** Volatility = 20%
- **Stock B (Crypto):** Volatility = 80%
- **Size for A:** $1\% / 20\% = 5.0\%$ of portfolio.
- **Size for B:** $1\% / 80\% = 1.25\%$ of portfolio.

---

## 5. Monte Carlo Simulation: Predicting the Future
A Monte Carlo simulation runs thousands of "random walks" to see the probability of different outcomes.
- **How to use it:** Enter your current portfolio, your monthly IDR 7.2M contribution, and the historical volatility of your assets into a simulator.
- **The "Success Rate":** If the simulation says you have a 95% chance of hitting your retirement goal, you are on track. If it's 60%, you must either increase your savings or lower your risk.

---

## 6. Risk Parity (The All-Weather Approach)
Developed by Bridgewater (Ray Dalio), Risk Parity involves balancing a portfolio by risk contribution rather than capital amount.
- Because Bonds are less volatile than Stocks, a 60/40 Stock/Bond portfolio actually gets ~90% of its risk from Stocks.
- A true Risk Parity portfolio might be 20% Stocks / 80% Bonds (leveraged) so that both contribute 50% of the risk.
- **Personal Application:** If you hold volatile assets like Bitcoin (Satellite), your Core should be weighted toward very low-volatility assets like RDPU (Bibit) to maintain overall balance.

---

## 7. Professional Stop-Loss Strategies
### A. The "Hard Stop" (Price-Based)
Set at the level where your **Investment Thesis is invalidated**. 
- *Rule:* If you bought because of a product launch and the launch fails, you sell. The price doesn't matter.

### B. The "ATR Stop" (Volatility-Adjusted)
Use the **Average True Range (ATR)** to ensure you aren't "whiplashed" by normal market noise.
- **Standard:** Entry Price - $(2.5 \times ATR)$.

### C. The "Time Stop"
If you buy a stock for a catalyst and that catalyst doesn't happen within 6 months, and the stock is flat, you sell. **Dead capital is a risk.**

---

## 8. Tail Risk & "Black Swans"
Tail risk is the risk of an event that occurs at the extremes of a probability distribution (like a 2008 or 2020 crash).
- **The "Antifragile" Approach:** Keep a small portion of the portfolio (1-2%) in "Insurance" assets that explode in value during a crash (e.g., VIX calls or deep OTM puts).
- **The "Cash Buffer":** Simply holding 10% cash is the cheapest way to manage tail risk.

---

## 9. Drawdown Management Protocols (The "Kill Switch")
Every institutional fund has a "Circuit Breaker." You must too.

| Drawdown Level | Action to Take |
| :--- | :--- |
| **-5% (Portfolio)** | Review all positions. Stop all new satellite entries. |
| **-10% (Portfolio)** | Cut all satellite positions by 50%. Move to "Capital Preservation" mode. |
| **-20% (Portfolio)** | **Total Liquidate (Satellites).** Return to 100% Core/Cash. Perform a "Post-Mortem" audit. |

---

## 10. Hedging for the Indonesian Investor
Since you are a Software Engineer with IDR income and USD investments (Gotrade):
1.  **Currency Hedge:** When USD/IDR is at historical highs (>16,000), consider increasing your IDR-denominated Reksadana (Bibit) to hedge against a USD correction.
2.  **Options (Advanced):** Buy "Out-of-the-Money" (OTM) Put options on the Nasdaq 100 (QQQ) to protect against a tech crash. This is like paying an "Insurance Premium."

---

## 11. Key Takeaways
> - **Survival is the first rule.** You can't compound if you are wiped out.
> - **Volatility is not your enemy;** lack of liquidity is.
> - **Math beats intuition.** Always size positions based on formulas, not "feelings."

## 12. Implementation Guide
1. Calculate your current Portfolio Drawdown from its peak.
2. Identify your most volatile holding (usually Crypto or a high-growth tech stock).
3. Recalculate its size using the **Volatility Targeting** formula in Module 10.

---
**Next Module:** `03-due-diligence.md` - Analyzing the assets.
