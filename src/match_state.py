"""
Stage 1: Pre-Ball Match-State Feature Engineering
Avoids any future leakage. Computes pre-ball state for every delivery.
"""
import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np

sys.path.append(str(Path(__file__).resolve().parent.parent))
from src.config import DATA_DIR, OUTPUTS_DIR, RANDOM_SEED

np.random.seed(RANDOM_SEED)

def compute_match_state_features(df=None):
    print("=" * 80)
    print("STAGE 1: COMPUTING PRE-BALL MATCH-STATE FEATURES")
    print("=" * 80)

    if df is None:
        clean_path = DATA_DIR / "master_clean_deliveries.csv"
        if not clean_path.exists():
            raise FileNotFoundError(f"Clean deliveries not found at {clean_path}. Run Stage 0 first.")
        print(f"Loading clean deliveries from {clean_path}...")
        df = pd.read_csv(clean_path, low_memory=False)

    # Sort strictly by match, innings, overid, over_ball_num
    df = df.sort_values(['match_id', 'innings', 'overid', 'over_ball_num']).reset_index(drop=True)

    # Calculate 1st innings total per match to establish Innings 2 target
    inn1_totals = df[df['innings'] == 1].groupby('match_id')['total_runs'].sum().reset_index()
    inn1_totals.rename(columns={'total_runs': 'inn1_total_runs'}, inplace=True)
    df = df.merge(inn1_totals, on='match_id', how='left')

    # Target calculation
    # In Innings 2, target is inn1_total_runs + 1 (unless revised_target is specified)
    df['target'] = np.where(
        df['innings'] == 2,
        df['revised_target'].fillna(df['inn1_total_runs'] + 1),
        np.nan
    )

    # Group by match_id and innings to compute cumulative pre-ball states
    print("Computing cumulative pre-ball state metrics across matches...")

    # Grouped cumulative sums
    grouped = df.groupby(['match_id', 'innings'])

    # Shifted cumulative values represent the state BEFORE the delivery is bowled
    # Total runs in innings before this ball
    df['score_before'] = grouped['total_runs'].cumsum() - df['total_runs']
    
    # Wickets lost before this ball
    # Note: is_wicket can be boolean or int
    is_wkt_int = df['is_wicket'].astype(int)
    df['wickets_before'] = grouped.apply(lambda g: g['is_wicket'].astype(int).cumsum() - g['is_wicket'].astype(int)).reset_index(level=[0,1], drop=True)
    
    # Legal balls bowled before this ball
    df['legal_balls_before'] = grouped.apply(lambda g: g['is_legal'].astype(int).cumsum() - g['is_legal'].astype(int)).reset_index(level=[0,1], drop=True)

    # Balls remaining in innings (T20 format = 120 legal balls)
    df['balls_remaining'] = np.maximum(0, 120 - df['legal_balls_before'])
    
    # Wickets in hand
    df['wickets_in_hand'] = np.maximum(0, 10 - df['wickets_before'])

    # Current Run Rate (CRR)
    overs_completed = df['legal_balls_before'] / 6.0
    df['current_run_rate'] = np.where(
        overs_completed > 0,
        df['score_before'] / overs_completed,
        0.0
    )

    # Innings 2 Chase Metrics
    df['runs_required'] = np.where(
        df['innings'] == 2,
        np.maximum(0, df['target'] - df['score_before']),
        np.nan
    )

    overs_remaining = df['balls_remaining'] / 6.0
    df['required_run_rate'] = np.where(
        (df['innings'] == 2) & (overs_remaining > 0),
        df['runs_required'] / overs_remaining,
        np.where((df['innings'] == 2) & (df['runs_required'] > 0), 36.0, 0.0)
    )

    df['rrr_minus_crr'] = np.where(
        df['innings'] == 2,
        df['required_run_rate'] - df['current_run_rate'],
        np.nan
    )

    # Match Phase: Powerplay (1-6), Middle (7-15), Death (16-20)
    def assign_phase(overid):
        if overid <= 6:
            return 'powerplay'
        elif overid <= 15:
            return 'middle'
        else:
            return 'death'

    df['phase'] = df['overid'].apply(assign_phase)

    # Recent Form: Runs and Wickets in the last 18 legal deliveries of the innings
    print("Computing rolling recent form (last 18 balls) per innings...")
    def compute_rolling(group):
        # We compute rolling sum on legal balls, or simple rolling on previous rows
        # Rolling 18 balls shifted by 1 so current ball is not included
        r_runs = group['total_runs'].shift(1).rolling(window=18, min_periods=1).sum().fillna(0)
        r_wkts = group['is_wicket'].astype(int).shift(1).rolling(window=18, min_periods=1).sum().fillna(0)
        return pd.DataFrame({'runs_last_18': r_runs, 'wkts_last_18': r_wkts}, index=group.index)

    rolling_res = grouped.apply(compute_rolling).reset_index(level=[0,1], drop=True)
    df['runs_last_18_balls'] = rolling_res['runs_last_18']
    df['wickets_last_18_balls'] = rolling_res['wkts_last_18']

    # Innings 1: Par-Relative Score
    # Compute the average score in Innings 1 at each (overid, wickets_before) bucket across the dataset
    print("Computing Innings 1 par-relative baseline...")
    inn1_df = df[df['innings'] == 1]
    par_lookup = inn1_df.groupby(['overid', 'wickets_before'])['score_before'].mean().to_dict()
    
    # Map back to df
    def get_par(row):
        if row['innings'] == 1:
            key = (row['overid'], row['wickets_before'])
            return par_lookup.get(key, row['score_before'])
        return np.nan

    df['inn1_par_score'] = df.apply(get_par, axis=1)
    df['score_vs_par'] = np.where(
        df['innings'] == 1,
        df['score_before'] - df['inn1_par_score'],
        np.nan
    )

    # Ground truth: Batting team won
    # win_team_id == batting_team_id
    df['batting_team_won'] = np.where(
        df['win_team_id'].notnull(),
        (df['win_team_id'] == df['batting_team_id']).astype(int),
        np.nan
    )

    print("\nPre-ball state sample summary:")
    print(df[['match_id', 'innings', 'overid', 'over_ball_num', 'score_before', 'wickets_before',
              'balls_remaining', 'wickets_in_hand', 'current_run_rate', 'phase', 'batting_team_won']].head(10))

    # Save master with match state
    output_path = DATA_DIR / "master_with_match_state.csv"
    df.to_csv(output_path, index=False)
    print(f"\n[+] Successfully saved {len(df):,} rows with match-state features to {output_path}")

    # Summarize phase counts
    print("\nDeliveries by Phase:")
    print(df['phase'].value_counts())

    print("\nInnings 2 Chase Summary:")
    inn2_sample = df[df['innings'] == 2][['runs_required', 'balls_remaining', 'required_run_rate', 'rrr_minus_crr']].describe()
    print(inn2_sample)

    return df

if __name__ == "__main__":
    compute_match_state_features()
