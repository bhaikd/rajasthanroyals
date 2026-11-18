"""
Notebook Generator: Builds notebooks/analysis.ipynb using standard json module.
Updated for SupeRR Selector Round 1 with Phase-Specific Wicket Values, Calibration Recentering,
REML Hierarchical Model, Opposition Quality Audits, HP-Wicket Comparisons, and Sensitivity Analysis.
"""
import json
from pathlib import Path

def create_analysis_notebook():
    ROOT_DIR = Path(__file__).resolve().parent.parent

    cells = [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# SupeRR Selector Season 2 – Round 1: Pressure Performance Analysis\n",
                "## Identifying the Most Reliable Batters and Bowlers Under Pressure (IPL & T20I 2022 Onwards)\n",
                "\n",
                "**Author:** Kishalay Das (SupeRR Selector Analytics – Round 1 Submission)  \n",
                "**Challenge:** Rajasthan Royals SupeRR Selector Season 2 (Round 1)  \n",
                "**Deliverables:** Top 10 Batters & Top 10 Bowlers under pressure + Comprehensive Methodology\n",
                "**Dataset:** 883 Matches, 200,999 Deliveries (IPL & T20I)\n",
                "\n",
                "---\n",
                "### Executive Summary\n",
                "This analysis implements a sabermetric-grade hierarchical Bayesian framework to measure player performance in high-pressure match situations compared with ordinary baselines.\n",
                "- **Mathematical Outcome Leverage:** Expected absolute outcome swing across all 7 mutually exclusive delivery outcomes ($P(o \\mid \\text{phase}) \\times |\\Delta WP|$; Top 25% defines High Pressure, 50,241 deliveries).\n",
                "- **Calibration Recentering:** Out-of-fold residuals recentered so league-wide residual means are identically $0.000000$.\n",
                "- **Phase-Specific Wickets:** Derived from win-probability utility at 14.36 runs (Powerplay), 8.13 runs (Middle), and 2.92 runs (Death); weighted mean 8.85 runs.\n",
                "- **Hierarchical REML Decomposition:** $\\text{Rating}_i = \\hat{B}_i + \\hat{\\Delta}_i$ with variance components estimated on match-level data.\n",
                "- **Fair Comparisons & Opposition Quality:** Eligibility filters (>= 100 HP balls, >= 6 HP matches, >= 10 total career matches) and opponent-baseline quality audits.\n",
                "- **Within-Match Null Permutation Test:** 1,000 within-match permutations confirm statistically distinguishable bowling control ($p = 0.0060$) vs borderline single-match batting variance ($p = 0.0500$).\n",
                "- **Uncertainty & Single Bootstrap:** 1,000 match-grouped bootstrap draws (seed 42) computing identical credible intervals and $P(\\text{top 10})$ across all tables and charts."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": 1,
            "metadata": {},
            "outputs": [],
            "source": [
                "import os\n",
                "import sys\n",
                "from pathlib import Path\n",
                "import pandas as pd\n",
                "import numpy as np\n",
                "import matplotlib.pyplot as plt\n",
                "import seaborn as sns\n",
                "\n",
                "# Setup paths\n",
                "ROOT_DIR = Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()\n",
                "DATA_DIR = ROOT_DIR / 'data'\n",
                "OUTPUTS_DIR = ROOT_DIR / 'outputs'\n",
                "print(f'Working directory: {ROOT_DIR}')\n"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## Stage 0: Data Audit & Clean Deliveries\n",
                "We audited 6 CSV datasets covering 883 matches and 200,999 deliveries.\n",
                "- Super overs (38 balls across 6 matches) and rain-shortened/DLS matches (68 matches) were identified and isolated to prevent target distortion.\n",
                "- A master clean delivery table was created with bowler-attributed wickets and legal deliveries flagged."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": 2,
            "metadata": {},
            "outputs": [],
            "source": [
                "exclusions = pd.read_csv(OUTPUTS_DIR / 'data_exclusion_log.csv')\n",
                "print('Data Exclusions Summary:')\n",
                "display(exclusions)\n"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## Stage 1 & 2: Win-Probability Leverage, Calibration & Validation\n",
                "We train separate Innings 1 and Innings 2 LightGBM classifiers (GroupKFold by match) to estimate pre-ball win probability.\n",
                "**Leverage** is defined strictly as the expected absolute swing in win probability across all 7 mutually exclusive outcomes weighted by empirical phase transition probabilities:\n",
                "$$\\text{Leverage}_t = \\sum_{o \\in \\mathcal{O}} P(o \\mid \\text{phase}) \\cdot |WP(S_{t+1}(o)) - WP(S_t)|$$\n",
                "Continuous **Pressure Index** is the percentile rank ($0–100$) of context leverage. Deliveries in the top quartile ($\\ge 75$th percentile, 50,241 balls) define **High Pressure**."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": 3,
            "metadata": {},
            "outputs": [],
            "source": [
                "cal_summary = pd.read_csv(OUTPUTS_DIR / 'calibration_summary.csv')\n",
                "print('Calibration Auditing Summary (Out-of-Fold League Mean vs Eligible Players):')\n",
                "display(cal_summary)\n",
                "\n",
                "val_stats = pd.read_csv(OUTPUTS_DIR / 'pressure_validation_stats.csv')\n",
                "print('\\nHigh-Pressure vs Ordinary Delivery Validation (Non-Circular Metrics with Effect Sizes):')\n",
                "display(val_stats)\n",
                "\n",
                "phase_crosstab = pd.read_csv(OUTPUTS_DIR / 'pressure_by_phase_innings.csv')\n",
                "print('\\nPressure Distribution by Phase and Innings:')\n",
                "display(phase_crosstab)\n"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## Stage 3: Context-Aware Expected-Value Models & Phase-Specific Wickets\n",
                "Using 5-fold grouped cross-validation by match, we fit player-agnostic baseline models:\n",
                "- Expected Batter Runs ($xR_{bat}$) and Expected Bowler Runs Conceded ($xR_{bowl}$)\n",
                "- Expected Batter Dismissal Probability ($xW_{bat}$) and Expected Bowler Wicket Probability ($xW_{bowl}$)\n",
                "Each delivery yields out-of-fold residuals: Runs Above Expected ($RAE$) and Wickets Above Expected ($WAE$).\n",
                "Wickets are converted to runs using phase-specific marginal rates of substitution: **14.36 runs (Powerplay)**, **8.13 runs (Middle)**, and **2.92 runs (Death)** (overall mean: 8.85 runs).\n",
                "We also recomputed wicket values on high-pressure deliveries only (**14.40 PP, 10.71 Middle, 5.89 Death, mean 9.52 runs/wkt**)."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": 4,
            "metadata": {},
            "outputs": [],
            "source": [
                "phase_comp_bat = pd.read_csv(OUTPUTS_DIR / 'phase_vs_flat_comparison_batters.csv')\n",
                "print('Phase-Specific vs Flat 8.85 Comparison (Top 10 Batters):')\n",
                "display(phase_comp_bat)\n",
                "\n",
                "phase_comp_bowl = pd.read_csv(OUTPUTS_DIR / 'phase_vs_flat_comparison_bowlers.csv')\n",
                "print('\\nPhase-Specific vs Flat 8.85 Comparison (Top 10 Bowlers):')\n",
                "display(phase_comp_bowl)\n",
                "\n",
                "hp_wkt_comp = pd.read_csv(OUTPUTS_DIR / 'hp_wicket_comparison.csv')\n",
                "print('\\nHigh-Pressure Only Wicket Values vs Phase-Specific & Flat 8.85 Jaccard Table:')\n",
                "display(hp_wkt_comp)\n"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## Stage 4 & 5: Fair Comparisons, Hierarchical REML Model & Opposition Audit\n",
                "We model player pressure performance as Ordinary Baseline ($B_i$) plus Pressure Effect ($\\Delta_i$).\n",
                "Variance components are estimated via REML on match-level data:\n",
                "- Batters: $K_B = 1,717.4$ balls, $K_\\Delta = 773.0$ balls (typical weight on pressure effect = $24.6\\%$).\n",
                "- Bowlers: $K_B = 1,312.9$ balls, $K_\\Delta = 1,041.4$ balls (typical weight on pressure effect = $19.0\\%$).\n",
                "Final Rating = Posterior Baseline + Posterior Pressure Effect ($\\hat{B}_i + \\hat{\\Delta}_i$).\n",
                "We also conduct an Opposition Quality Audit to ensure no player's ranking is solely inflated by sub-par competition."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": 5,
            "metadata": {},
            "outputs": [],
            "source": [
                "top_batters = pd.read_csv(OUTPUTS_DIR / 'final_top10_batters.csv')\n",
                "print('=== FINAL TOP 10 BATTERS UNDER PRESSURE (PRIMARY RANKING: PHASE-SPECIFIC WICKETS) ===')\n",
                "display(top_batters[['rank', 'striker_name', 'teams', 'hp_balls_faced', 'hp_strike_rate', 'shrunk_rating', 'ci_lower_90', 'ci_upper_90', 'shrunk_baseline', 'shrunk_delta', 'delta_label', 'shrunk_success_rate', 'top10_probability']])\n",
                "\n",
                "top_bowlers = pd.read_csv(OUTPUTS_DIR / 'final_top10_bowlers.csv')\n",
                "print('\\n=== FINAL TOP 10 BOWLERS UNDER PRESSURE (PRIMARY RANKING: PHASE-SPECIFIC WICKETS) ===')\n",
                "display(top_bowlers[['rank', 'bowler_name', 'teams', 'hp_legal_balls', 'hp_economy', 'shrunk_rating', 'ci_lower_90', 'ci_upper_90', 'shrunk_baseline', 'shrunk_delta', 'delta_label', 'shrunk_success_rate', 'top10_probability']])\n",
                "\n",
                "opp_audit = pd.read_csv(OUTPUTS_DIR / 'opposition_audit_top10.csv')\n",
                "print('\\n=== OPPOSITION QUALITY AUDIT (TOP 10 BATTERS & BOWLERS) ===')\n",
                "display(opp_audit)\n",
                "\n",
                "if (OUTPUTS_DIR / 'excluded_pakistan_players.csv').exists():\n",
                "    excl_pak = pd.read_csv(OUTPUTS_DIR / 'excluded_pakistan_players.csv')\n",
                "    print('\\n=== TRANSPARENT AUDIT OF EXCLUDED PAKISTAN PLAYERS IN TOP 20 ===')\n",
                "    display(excl_pak)\n",
                "\n",
                "clutch_bat = pd.read_csv(OUTPUTS_DIR / 'top10_clutch_constrained_batters.csv')\n",
                "print('\\n=== CLUTCH-CONSTRAINED BATTERS (RULE B: DELTA >= 0) ===')\n",
                "display(clutch_bat[['clutch_constrained_rank', 'striker_name', 'shrunk_rating', 'shrunk_baseline', 'shrunk_delta', 'delta_label']])\n",
                "\n",
                "clutch_bowl = pd.read_csv(OUTPUTS_DIR / 'top10_clutch_constrained_bowlers.csv')\n",
                "print('\\n=== CLUTCH-CONSTRAINED BOWLERS (RULE B: DELTA >= 0) ===')\n",
                "display(clutch_bowl[['clutch_constrained_rank', 'bowler_name', 'shrunk_rating', 'shrunk_baseline', 'shrunk_delta', 'delta_label']])\n"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## Stage 6: Within-Match Null Permutation Test, Sensitivity Across 14 Specs & Sanity Diagnostics\n",
                "We evaluate:\n",
                "1. **Within-Match Null Permutation Test (1,000 Draws):** Permuting HP labels within matches confirms statistically significant bowler pressure control ($p = 0.0060$) vs borderline batting signal ($p = 0.0500$).\n",
                "2. **Pairwise Distinguishability:** Adjacent rank superiority probabilities.\n",
                "3. **Sensitivity Analysis:** 14 model specifications across wicket values, leverage cutoffs, ball filters, competition filters, and recency weighting.\n",
                "4. **Famous Player Diagnostics:** Data-driven audit for Bumrah, Kohli, Rohit, Hazlewood, and other household names."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": 6,
            "metadata": {},
            "outputs": [],
            "source": [
                "null_summary = pd.read_csv(OUTPUTS_DIR / 'null_test_summary.csv')\n",
                "print('Within-Match Null Permutation Test Summary:')\n",
                "display(null_summary)\n",
                "\n",
                "pw_bat = pd.read_csv(OUTPUTS_DIR / 'pairwise_probabilities_batters.csv')\n",
                "print('\\nBatters Adjacent Pairwise Superiority P(Rank i > Rank i+1):')\n",
                "display(pw_bat)\n",
                "\n",
                "pw_bowl = pd.read_csv(OUTPUTS_DIR / 'pairwise_probabilities_bowlers.csv')\n",
                "print('\\nBowlers Adjacent Pairwise Superiority P(Rank i > Rank i+1):')\n",
                "display(pw_bowl)\n",
                "\n",
                "ranges = pd.read_csv(OUTPUTS_DIR / 'top10_rank_ranges.csv')\n",
                "print('\\nTop 10 Player Rank Ranges across 14 Specifications:')\n",
                "display(ranges)\n",
                "\n",
                "bat_sanity = pd.read_csv(OUTPUTS_DIR / 'sanity_table_famous_batters.csv')\n",
                "print('\\nFamous Batters Sanity Check:')\n",
                "display(bat_sanity)\n",
                "\n",
                "bowl_sanity = pd.read_csv(OUTPUTS_DIR / 'sanity_table_famous_bowlers.csv')\n",
                "print('\\nFamous Bowlers Sanity Check:')\n",
                "display(bowl_sanity)\n"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## Stage 7: Publication Visualizations\n",
                "High-resolution figures generated by `src/visualizations.py`:\n",
                "1. Win-Probability Model Calibration Curves\n",
                "2. Expected Value Model Calibration Curves across Deciles and Phases\n",
                "3. High Pressure vs Ordinary Situations Performance Comparison\n",
                "4. Rating vs Sample Size Funnel Plot (illustrating REML shrinkage dynamics)\n",
                "5. Top 10 Batters & Bowlers 90% Bootstrap Credible Intervals with 95% Within-Match Null Chance Bands Overlay\n",
                "6. Baseline vs Pressure Impact Scatter Plot (illustrating clutch elevation)\n",
                "7. Rank Stability Heatmap across 14 Model Specifications"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": 7,
            "metadata": {},
            "outputs": [],
            "source": [
                "from IPython.display import Image, display\n",
                "charts = [\n",
                "    ('Win-Probability Model Calibration', 'win_probability_calibration.png'),\n",
                "    ('Expected Value Calibration by Decile and Phase', 'expected_value_calibration_deciles_phases.png'),\n",
                "    ('Pressure vs Ordinary Comparison', 'pressure_vs_ordinary_comparison.png'),\n",
                "    ('Rating vs Sample Size Funnel Plot', 'rating_vs_samplesize_funnel.png'),\n",
                "    ('Top 10 Batters 90% Intervals vs Null Band', 'top10_batters_intervals.png'),\n",
                "    ('Top 10 Bowlers 90% Intervals vs Null Band', 'top10_bowlers_intervals.png'),\n",
                "    ('Baseline vs Pressure Impact Scatter', 'baseline_vs_pressure_scatter.png'),\n",
                "    ('Rank Stability Heatmap across Specifications', 'rank_stability_heatmap.png'),\n",
                "]\n",
                "for title, fname in charts:\n",
                "    img_path = OUTPUTS_DIR / fname\n",
                "    if img_path.exists():\n",
                "        print(f'=== {title} ===')\n",
                "        display(Image(filename=str(img_path)))\n"
            ]
        }
    ]

    notebook_content = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.12.0"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 2
    }

    nb_path = ROOT_DIR / "notebooks" / "analysis.ipynb"
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(notebook_content, f, indent=2)
    print(f"[+] Successfully generated valid Jupyter notebook at: {nb_path}")

if __name__ == "__main__":
    create_analysis_notebook()
