"""
Revised Configuration settings for SupeRR Selector Season 2 - Round 1
"""
import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUTS_DIR = BASE_DIR / "outputs"
NOTEBOOKS_DIR = BASE_DIR / "notebooks"
REPORT_DIR = BASE_DIR / "report"

for p in [OUTPUTS_DIR, NOTEBOOKS_DIR, REPORT_DIR]:
    p.mkdir(parents=True, exist_ok=True)

# Random Seed
RANDOM_SEED = 42

# Pressure Modeling Parameters
PRESSURE_PERCENTILE_DEFAULT = 75.0  # Top 25% of leverage deliveries = High Pressure
PRESSURE_PERCENTILE_SENSITIVITY = [70.0, 75.0, 80.0]  # Top 30%, 25%, 20%

# Eligibility Thresholds
MIN_HP_BALLS_FACED_BATTER = 100      # balls faced in high-pressure deliveries
MIN_HP_BALLS_BOWLED_BOWLER = 100     # legal deliveries in high-pressure
MIN_MATCHES_BATTER = 10              # total matches
MIN_HP_MATCHES_BATTER = 6            # matches with high pressure exposure
MIN_MATCHES_BOWLER = 10
MIN_HP_MATCHES_BOWLER = 6

# Exclusion Rule: Exclude all Pakistan players (Pakistan national team and Pakistan A)
EXCLUDE_PAKISTAN_PLAYERS = True

def get_pakistan_player_ids(data_dir=DATA_DIR):
    import pandas as pd
    teams = pd.read_csv(data_dir / 'teams.csv')
    pak_team_ids = set(teams[teams['team_name'].str.contains('Pakistan|Pak', case=False, na=False)]['team_id'].unique())
    matches = pd.read_csv(data_dir / 'matches.csv')
    pak_home_ids = set(matches[matches['home_team'].str.contains('Pakistan|Pak', case=False, na=False)]['home_team_id'].unique())
    pak_away_ids = set(matches[matches['away_team'].str.contains('Pakistan|Pak', case=False, na=False)]['away_team_id'].unique())
    all_pak_team_ids = pak_team_ids.union(pak_home_ids).union(pak_away_ids)

    mapping = pd.read_csv(data_dir / 'competition_team_player_mapping.csv')
    pak_players_mapping = set(mapping[mapping['team_id'].isin(all_pak_team_ids) | mapping['team_name'].str.contains('Pakistan|Pak', case=False, na=False)]['player_id'].unique())
    p11 = pd.read_csv(data_dir / 'playing_eleven.csv')
    pak_players_p11 = set(p11[p11['team_id'].isin(all_pak_team_ids)]['player_id'].unique())
    bbb = pd.read_csv(data_dir / 'ball_by_ball.csv', usecols=['match_id', 'batting_team_id', 'bowling_team_id', 'striker_id', 'bowler_id'])
    pak_strikers = set(bbb[bbb['batting_team_id'].isin(all_pak_team_ids)]['striker_id'].unique())
    pak_bowlers = set(bbb[bbb['bowling_team_id'].isin(all_pak_team_ids)]['bowler_id'].unique())
    all_pak_player_ids = pak_players_mapping.union(pak_players_p11).union(pak_strikers).union(pak_bowlers)
    return all_pak_player_ids

# Sensitivity test thresholds
SENSITIVITY_THRESHOLDS = {
    'batters': [75, 100, 120, 150],
    'bowlers': [75, 100, 120, 150]
}

# Empirical Phase Transition Probabilities for Leverage Expectation
# Derived from 200,999 historical deliveries
PHASE_TRANSITION_PROBS = {
    'powerplay': {0: 0.442, 1: 0.252, 2: 0.046, 3: 0.005, 4: 0.155, 6: 0.054, 'wicket': 0.045},
    'middle':    {0: 0.301, 1: 0.436, 2: 0.065, 3: 0.002, 4: 0.090, 6: 0.059, 'wicket': 0.047},
    'death':     {0: 0.283, 1: 0.350, 2: 0.081, 3: 0.003, 4: 0.113, 6: 0.088, 'wicket': 0.081}
}

# Empirical Wicket Run Values derived from Win-Probability Marginal Rate of Substitution:
# delta_WP(Wicket) / delta_WP(1 Run)
WICKET_RUN_VALUE_EMPIRICAL = {
    'powerplay': 14.36,
    'middle': 8.13,
    'death': 2.92,
    'weighted_mean': 8.85
}
# Default base wicket run value (Phase-specific by default)
USE_PHASE_SPECIFIC_WICKET_VALUE = True
DEFAULT_WICKET_RUN_VALUE = 8.85

# Participant / Author Metadata
AUTHOR_NAME = "Kishalay Das (SupeRR Selector Analytics – Round 1 Submission)"

# Sensitivity wicket values
WICKET_VALUE_SENSITIVITY = [7.0, 9.0, 11.0, 13.0]
