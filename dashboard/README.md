# SupeRR Selector Round 1: Interactive Dashboard
### *Most Reliable T20 Players Under High Pressure*

This interactive dashboard provides a publication-grade, read-only presentation of the empirical results produced by the SupeRR Selector Season 2 sabermetric pipeline.

---

## 🚀 Quick Start Instructions

1. **Install Dependencies**:
   ```bash
   python -m pip install -r requirements.txt
   ```

2. **Run the Dashboard**:
   ```bash
   streamlit run dashboard/app.py
   ```
   The dashboard runs entirely offline using precomputed result files from `outputs/` and `data/`.

3. **Run Data Integrity Assertions**:
   ```bash
   python dashboard/check_data.py
   ```

---

## 📁 Architecture & File Structure

```
dashboard/
├── app.py              # Main Streamlit application with wide mode & sidebar navigation
├── data.py             # Cached data-loading module (st.cache_data) mapping pipeline outputs
├── theme.py            # Custom CSS and Plotly layout formatting (Navy #021D45, Pink #E50695)
├── check_data.py       # Automated data integrity test suite (recomputes rankings, checks cohorts)
├── qa_dashboard.py     # Playwright automated visual inspection and responsiveness runner
└── README.md           # Documentation and run instructions
```

---

## 📊 Dashboard Pages

1. **Overview**:
   - Executive summary and key numbers strip (883 matches, 200,999 balls, 50,241 HP balls, 131 batters, 140 bowlers).
   - Publication-styled stacked Top 10 Batters and Bowlers tables with dot markers, credible elevation green tinting, and red negative delta styling.
2. **Player Explorer**:
   - Drill-down into any of the 131 eligible batters or 140 eligible bowlers.
   - Posterior rating decomposition ($B + \Delta$), credible intervals vs permutation null, ordinary vs HP comparison, and match-by-match HP timeline.
   - Side-by-side comparison mode for 2–3 players.
3. **Rankings Explorer**:
   - Complete interactive rankings table for all 131 batters and 140 bowlers with filters (minimum HP balls, credible-positive delta) and CSV export.
   - Baseline vs Pressure Effect quadrant scatter plot and empirical Bayes shrinkage funnel plot.
4. **Evidence & Reliability**:
   - Forest plots of posterior ratings against the 95% permutation null bands.
   - Rank sensitivity ranges across 14 model specifications with full sensitivity matrices.
   - Decile calibration plots for Expected Runs (xR) and Expected Wickets (xW).
   - Split-half stability and within-match null permutation hypothesis test results.
5. **Pressure Explorer**:
   - Mathematical formulation of leverage ($L_t$).
   - High-pressure delivery distribution by match phase and innings.
   - Behavioral domain validation statistics (strike rotation $+1.39$ pp, dot balls $-1.17$ pp, WP volatility $+2.00$ pp/ball).
   - Ball-by-ball match leverage and win probability inspector for 883 matches.
6. **Excluded Players & Methodology**:
   - Transparent audit table of excluded Pakistan players under author eligibility choice.
   - 6-part methodology summary cards and PDF download button.
   - Explicit analytical caveats and limitations.

---

## 🔒 Design & Integrity Commitments
- **Zero Model Reruns / Zero Hardcoding**: Every number is loaded dynamically from cached DataFrames; no analytical figures are hardcoded in application logic.
- **Visual Parity**: Built using the exact navy (`#021D45`), pink (`#E50695`), and light grey-blue (`#F5F6FA`) palette of the problem-statement and methodology report.
- **Offline / Local**: Operates fully offline without external APIs or credentials.
