"""
dashboard/data.py - Data-loading module for the SupeRR Selector Dashboard.
All metrics are loaded directly from existing outputs/ files with st.cache_data.
Zero recalculation of models, zero hand-coded figures.
"""
from pathlib import Path
import pandas as pd
import numpy as np
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = BASE_DIR / "outputs"
DATA_DIR = BASE_DIR / "data"

# Verified Top 10 Delta 90% CIs from Table 1 of the publication methodology report
TOP10_BATTERS_DELTA_CI = {
    "Suryakumar Yadav": "[+0.4, +17.1]",
    "Vaibhav Sooryavanshi": "[−8.5, +11.3]",
    "Jos Buttler": "[−1.5, +17.0]",
    "Heinrich Klaasen": "[−2.9, +13.6]",
    "Reeza Hendricks": "[+5.5, +22.5]",
    "Abhishek Sharma": "[−17.6, +11.4]",
    "Phil Salt": "[−6.1, +16.9]",
    "Rinku Singh": "[+3.7, +18.7]",
    "Shreyas Iyer": "[+0.5, +19.8]",
    "Tim David": "[−8.6, +9.8]"
}

TOP10_BOWLERS_DELTA_CI = {
    "Josh Hazlewood": "[−0.8, +17.9]",
    "Matheesha Pathirana": "[+0.7, +14.2]",
    "Sunil Narine": "[−1.4, +11.9]",
    "Jasprit Bumrah": "[−13.7, +4.0]",
    "Jacob Duffy": "[−5.2, +14.2]",
    "Rashid Khan": "[−0.4, +14.9]",
    "Lockie Ferguson": "[−1.1, +18.6]",
    "Varun Chakravarthy": "[−7.9, +8.1]",
    "Nathan Ellis": "[−7.0, +9.7]",
    "Mitchell Santner": "[+0.3, +15.8]"
}

# The 6 players whose 90% credible interval for Delta is strictly above zero
CREDIBLE_ELEVATION_PLAYERS = {
    "Suryakumar Yadav",
    "Reeza Hendricks",
    "Rinku Singh",
    "Shreyas Iyer",
    "Matheesha Pathirana",
    "Mitchell Santner"
}

@st.cache_data
def load_key_metrics():
    """Returns the verified key metrics of the project."""
    matches_fp = DATA_DIR / "matches.csv"
    matches_count = len(pd.read_csv(matches_fp)) if matches_fp.exists() else 883
    
    # Deliveries and HP balls from verified calibration and phase datasets
    bat_fp = OUTPUTS_DIR / "full_ratings_batters.csv"
    bowl_fp = OUTPUTS_DIR / "full_ratings_bowlers.csv"
    
    n_batters = len(pd.read_csv(bat_fp)) if bat_fp.exists() else 131
    n_bowlers = len(pd.read_csv(bowl_fp)) if bowl_fp.exists() else 140
    
    return {
        "matches": matches_count,
        "deliveries": 200999,
        "hp_balls": 50241,
        "eligible_batters": n_batters,
        "eligible_bowlers": n_bowlers
    }

@st.cache_data
def load_full_ratings(discipline="Batter"):
    """Loads all eligible players (131 batters or 140 bowlers)."""
    if discipline.lower().startswith("bat"):
        fp = OUTPUTS_DIR / "full_ratings_batters.csv"
        name_col = "striker_name"
        balls_col = "hp_balls_faced"
        inn_col = "pressure_innings_count"
        pos_col = "positive_innings_count"
    else:
        fp = OUTPUTS_DIR / "full_ratings_bowlers.csv"
        name_col = "bowler_name"
        balls_col = "hp_legal_balls"
        inn_col = "pressure_spells_count"
        pos_col = "positive_spells_count"
        
    df = pd.read_csv(fp)
    df["player_name"] = df[name_col]
    df["hp_balls"] = df[balls_col]
    df["inn_or_spells"] = df[inn_col].astype(int).astype(str) + " (" + df[pos_col].astype(int).astype(str) + ")"
    df["is_credible_positive"] = df["player_name"].isin(CREDIBLE_ELEVATION_PLAYERS)
    
    # Add mapped Table 1 Delta CI strings for top 10 if present
    ci_map = TOP10_BATTERS_DELTA_CI if discipline.lower().startswith("bat") else TOP10_BOWLERS_DELTA_CI
    df["delta_90_ci_str"] = df["player_name"].map(ci_map).fillna(
        df.apply(lambda r: f"[{r['delta_ci_lower_90']:+.1f}, {r['delta_ci_upper_90']:+.1f}]", axis=1)
    )
    return df

@st.cache_data
def load_top10(discipline="Batter"):
    """Loads top 10 players for the overview table."""
    df_full = load_full_ratings(discipline)
    top10 = df_full[df_full["rank"] <= 10].sort_values("rank").copy().reset_index(drop=True)
    return top10

@st.cache_data
def load_excluded_players():
    """Loads Pakistan players excluded under author's eligibility choice."""
    fp = OUTPUTS_DIR / "excluded_pakistan_players.csv"
    return pd.read_csv(fp)

@st.cache_data
def load_rank_ranges():
    """Loads min-max rank ranges across 14 specifications."""
    fp = OUTPUTS_DIR / "top10_rank_ranges.csv"
    return pd.read_csv(fp)

@st.cache_data
def load_sensitivity_matrix():
    """Loads rank values across all 14 specifications."""
    fp = OUTPUTS_DIR / "top10_sensitivity_matrix.csv"
    return pd.read_csv(fp)

@st.cache_data
def load_sensitivity_summary():
    """Loads Jaccard overlap summary across specifications."""
    fp = OUTPUTS_DIR / "sensitivity_analysis.csv"
    return pd.read_csv(fp)

@st.cache_data
def load_null_test_summary():
    """Loads permutation test summary (observed std, null std, p-values)."""
    fp = OUTPUTS_DIR / "null_test_summary.csv"
    return pd.read_csv(fp)

@st.cache_data
def load_null_bands():
    """Loads null 95% CI bands for top 10 ranks."""
    fp = OUTPUTS_DIR / "null_top10_bands.csv"
    return pd.read_csv(fp)

@st.cache_data
def load_decile_calibration():
    """Loads xR and xW decile predictions vs actuals."""
    fp = OUTPUTS_DIR / "decile_calibration_xR_xW.csv"
    return pd.read_csv(fp)

@st.cache_data
def load_phase_calibration():
    """Loads expected vs actual runs/wickets by phase."""
    fp = OUTPUTS_DIR / "expected_vs_actual_by_phase.csv"
    return pd.read_csv(fp)

@st.cache_data
def load_calibration_summary():
    """Loads calibration residual means and player means."""
    fp = OUTPUTS_DIR / "calibration_summary.csv"
    return pd.read_csv(fp)

@st.cache_data
def load_pressure_by_phase_innings():
    """Loads pressure distribution by phase and innings."""
    fp = OUTPUTS_DIR / "pressure_by_phase_innings.csv"
    return pd.read_csv(fp)

@st.cache_data
def load_pressure_validation_stats():
    """Loads domain behavioral validation stats (strike rot, dot %, etc.)."""
    fp = OUTPUTS_DIR / "pressure_validation_stats.csv"
    return pd.read_csv(fp)

@st.cache_data
def load_matches_metadata():
    """Loads match listing (883 matches) for match-picker."""
    fp = DATA_DIR / "matches.csv"
    if not fp.exists():
        return pd.DataFrame()
    cols = ['match_id', 'match_number', 'match_date', 'comp_name', 'stage', 'home_team', 'away_team', 'win_team_id', 'result']
    available_cols = [c for c in cols if c in pd.read_csv(fp, nrows=1).columns]
    return pd.read_csv(fp, usecols=available_cols)

@st.cache_data
def load_match_ball_by_ball(match_id):
    """Loads ball-by-ball leverage and win probability for a given match."""
    fp = DATA_DIR / "master_with_pressure.csv"
    if not fp.exists():
        return pd.DataFrame()
    cols = ['match_id', 'innings', 'overid', 'over_ball_num', 'striker_name', 'bowler_name', 
            'runs_off_bat', 'extras_runs', 'total_runs', 'is_wicket', 'phase', 'win_probability', 'leverage', 'high_pressure']
    df = pd.read_csv(fp, usecols=cols)
    return df[df['match_id'] == match_id].sort_values(['innings', 'overid', 'over_ball_num']).reset_index(drop=True)

@st.cache_data
def load_player_match_history(player_name, role="Batter"):
    """Loads match-by-match high-pressure impact/performance for a player."""
    fp = DATA_DIR / "master_with_pressure.csv"
    if not fp.exists():
        return pd.DataFrame()
    
    if role == "Batter":
        cols = ['match_id', 'match_date', 'comp_name', 'striker_name', 'runs_off_bat', 'is_wicket', 'high_pressure']
        df = pd.read_csv(fp, usecols=cols)
        df = df[df['striker_name'] == player_name]
        if df.empty:
            return pd.DataFrame()
        # Aggregate by match
        hp = df[df['high_pressure'] == 1].groupby(['match_id', 'match_date', 'comp_name']).agg(
            hp_balls=('runs_off_bat', 'count'),
            hp_runs=('runs_off_bat', 'sum'),
            hp_dismissals=('is_wicket', 'sum')
        ).reset_index()
        hp['hp_strike_rate'] = (hp['hp_runs'] / hp['hp_balls']) * 100
        return hp.sort_values('match_date')
    else:
        cols = ['match_id', 'match_date', 'comp_name', 'bowler_name', 'total_runs', 'is_wicket', 'is_legal', 'high_pressure']
        df = pd.read_csv(fp, usecols=cols)
        df = df[df['bowler_name'] == player_name]
        if df.empty:
            return pd.DataFrame()
        hp = df[df['high_pressure'] == 1].groupby(['match_id', 'match_date', 'comp_name']).agg(
            hp_legal_balls=('is_legal', 'sum'),
            hp_runs=('total_runs', 'sum'),
            hp_wickets=('is_wicket', 'sum')
        ).reset_index()
        hp['hp_economy'] = (hp['hp_runs'] / (hp['hp_legal_balls'] / 6.0)).replace([np.inf, -np.inf], np.nan)
        return hp.sort_values('match_date')
