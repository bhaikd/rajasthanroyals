"""
Stage 0: Comprehensive Data Audit and Master Delivery Table Construction
"""
import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add src to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from src.config import DATA_DIR, OUTPUTS_DIR, RANDOM_SEED

np.random.seed(RANDOM_SEED)

def run_data_audit():
    print("=" * 80)
    print("STAGE 0: DATA AUDIT & SCHEMA INSPECTION")
    print("=" * 80)

    files = [
        "competitions.csv",
        "matches.csv",
        "teams.csv",
        "playing_eleven.csv",
        "competition_team_player_mapping.csv",
        "ball_by_ball.csv"
    ]

    dfs = {}
    schema_notes = []
    schema_notes.append("# Schema Notes & Table Relationships\n")
    schema_notes.append(f"**Generated during Stage 0 Data Audit**\n")

    for f in files:
        fpath = DATA_DIR / f
        if not fpath.exists():
            raise FileNotFoundError(f"Missing expected data file: {fpath}")
        
        print(f"\n>>> Loading and Auditing: {f}")
        df = pd.read_csv(fpath, low_memory=False)
        dfs[f] = df
        
        print(f"Shape: {df.shape[0]:,} rows x {df.shape[1]} columns")
        print(f"Columns & Types:\n{df.dtypes.to_string()}")
        nulls = df.isnull().sum()
        nulls_pct = (nulls / len(df) * 100).round(2)
        null_report = pd.DataFrame({'Missing_Count': nulls, 'Missing_Pct': nulls_pct})
        print(f"Missing Values:\n{null_report[null_report['Missing_Count'] > 0]}")

        # Schema documentation
        schema_notes.append(f"## Table: `{f}`")
        schema_notes.append(f"- **Dimensions**: {df.shape[0]:,} rows x {df.shape[1]} columns")
        schema_notes.append(f"- **Columns**: `{', '.join(df.columns.tolist())}`")
        
        # Check potential unique keys
        id_cols = [c for c in df.columns if 'id' in c or 'number' in c or 'code' in c]
        schema_notes.append(f"- **Key Identifiers**: `{', '.join(id_cols)}`")
        
        if 'match_date' in df.columns:
            df['match_date'] = pd.to_datetime(df['match_date'], errors='coerce')
            schema_notes.append(f"- **Date Range**: {df['match_date'].min().date()} to {df['match_date'].max().date()}")
            print(f"Date Range: {df['match_date'].min().date()} to {df['match_date'].max().date()}")
        elif 'delivery_ist_time' in df.columns:
            sample_dates = pd.to_datetime(df['delivery_ist_time'].dropna().str[:10], errors='coerce')
            schema_notes.append(f"- **Delivery Time Range**: {sample_dates.min().date()} to {sample_dates.max().date()}")
            print(f"Delivery Time Range: {sample_dates.min().date()} to {sample_dates.max().date()}")
        schema_notes.append("\n---\n")

    # Document joins
    schema_notes.append("## Join Architecture & Entity-Relationship Mapping")
    schema_notes.append("""
1. **matches.csv <-> competitions.csv**:
   - Join Key: `comp_id`
   - Purpose: Connects each match to tournament format (IPL vs T20I) and season.
2. **ball_by_ball.csv <-> matches.csv**:
   - Join Key: `match_id`
   - Purpose: Attaches venue, teams, toss, revised overs (DLS), knockout flag, and winner to deliveries.
3. **ball_by_ball.csv <-> teams.csv**:
   - Join Keys: `batting_team_id` / `bowling_team_id` <-> `team_id`
   - Purpose: Resolves team identities.
4. **ball_by_ball.csv <-> competition_team_player_mapping.csv**:
   - Join Keys: `striker_id` / `bowler_id` / `non_striker_id` <-> `player_id`
   - Purpose: Standardizes canonical player names and teams across tournaments.
5. **playing_eleven.csv <-> matches.csv**:
   - Join Keys: `match_id`, `team_id`, `player_id`
   - Purpose: Tracks starting lineups, batting orders, captaincy, wicketkeepers, and impact player subs.
""")

    # Save schema notes
    schema_notes_path = OUTPUTS_DIR / "schema_notes.md"
    with open(schema_notes_path, "w", encoding="utf-8") as snf:
        snf.write("\n".join(schema_notes))
    print(f"\n[+] Saved schema notes to: {schema_notes_path}")

    # Data Quality & Exclusion Analysis
    print("\n" + "=" * 80)
    print("DATA QUALITY CHECKS & EXCLUSION LOGGING")
    print("=" * 80)

    bbb = dfs["ball_by_ball.csv"].copy()
    matches = dfs["matches.csv"].copy()
    comps = dfs["competitions.csv"].copy()

    total_deliveries_raw = len(bbb)
    total_matches_raw = len(matches)
    print(f"Total raw matches: {total_matches_raw:,}")
    print(f"Total raw deliveries: {total_deliveries_raw:,}")

    # Check for duplicate deliveries
    dup_delivs = bbb.duplicated(subset=['match_id', 'innings', 'overid', 'over_ball_num']).sum()
    print(f"Duplicate delivery records: {dup_delivs:,}")

    # Check super overs
    super_over_mask = bbb['innings'] > 2
    super_over_balls = super_over_mask.sum()
    super_over_matches = bbb.loc[super_over_mask, 'match_id'].nunique()
    print(f"Super Over deliveries (innings > 2): {super_over_balls:,} across {super_over_matches} matches")

    # Check rain-shortened / DLS matches in matches.csv
    # revised overs or revised target or result containing DLS
    dls_condition = (
        matches['first_inn_revised_overs'].notnull() |
        matches['second_inn_revised_overs'].notnull() |
        matches['revised_target'].notnull() |
        matches['result'].str.contains('DLS|method', case=False, na=False)
    )
    dls_match_ids = set(matches.loc[dls_condition, 'match_id'].unique())
    print(f"DLS / Rain-shortened matches identified: {len(dls_match_ids)}")

    # Check abandoned / no-result matches
    no_result_condition = matches['result'].str.contains('No Result|Abandon', case=False, na=False)
    no_result_match_ids = set(matches.loc[no_result_condition, 'match_id'].unique())
    print(f"No Result / Abandoned matches identified: {len(no_result_match_ids)}")

    # Check matches with no result or missing winner
    missing_winner_condition = matches['win_team_id'].isnull() & ~matches['result'].str.contains('Tie', case=False, na=False)
    unresolved_match_ids = set(matches.loc[missing_winner_condition, 'match_id'].unique())
    print(f"Matches with missing winner (excluding ties): {len(unresolved_match_ids)}")

    # Exclusions for Pressure Modeling:
    # Exclude Super Overs (innings > 2) because target dynamics are 1-over shootouts
    # Exclude DLS/shortened matches from Win-Probability training/target calculation because 120-ball target logic breaks
    # Exclude Abandoned / No Result matches
    excluded_match_ids = dls_match_ids.union(no_result_match_ids).union(unresolved_match_ids)
    print(f"Total matches flagged for exclusion from leverage/win-probability modeling: {len(excluded_match_ids)}")

    exclusion_log = pd.DataFrame([
        {"Reason": "Duplicate deliveries", "Deliveries_Affected": dup_delivs, "Matches_Affected": 0, "Action": "Deduplicated"},
        {"Reason": "Super Overs (Innings > 2)", "Deliveries_Affected": super_over_balls, "Matches_Affected": super_over_matches, "Action": "Excluded from 120-ball pressure model"},
        {"Reason": "DLS / Rain-shortened matches", "Deliveries_Affected": bbb[bbb['match_id'].isin(dls_match_ids)].shape[0], "Matches_Affected": len(dls_match_ids), "Action": "Excluded from WP/Pressure model to avoid target distortion"},
        {"Reason": "Abandoned / No Result matches", "Deliveries_Affected": bbb[bbb['match_id'].isin(no_result_match_ids)].shape[0], "Matches_Affected": len(no_result_match_ids), "Action": "Excluded due to lack of ground-truth outcome"}
    ])
    exclusion_log.to_csv(OUTPUTS_DIR / "data_exclusion_log.csv", index=False)
    print(f"[+] Saved exclusion log to: {OUTPUTS_DIR / 'data_exclusion_log.csv'}")

    # Build Clean Master Delivery Table
    print("\n" + "=" * 80)
    print("CONSTRUCTING MASTER CLEAN DELIVERY TABLE")
    print("=" * 80)

    # Filter out super overs for the master pressure dataset
    df_clean = bbb[bbb['innings'].isin([1, 2])].copy()

    # Drop any exact duplicates if present
    df_clean = df_clean.drop_duplicates(subset=['match_id', 'innings', 'overid', 'over_ball_num'])

    # Merge match metadata
    match_meta = matches[['match_id', 'comp_id', 'match_date', 'stage', 'venue_id', 'venue_country',
                          'home_team_id', 'away_team_id', 'toss_win_team_id', 'toss_opted',
                          'knock_out', 'win_team_id', 'result', 'revised_target',
                          'first_inn_revised_overs', 'second_inn_revised_overs']].copy()
    df_clean = df_clean.merge(match_meta, on='match_id', how='left')

    # Merge competition metadata
    comp_meta = comps[['comp_id', 'comp_name', 'match_format', 'season']].copy()
    df_clean = df_clean.merge(comp_meta, on='comp_id', how='left')

    # Classify Competition Type: IPL vs T20I
    def classify_comp(row):
        name = str(row['comp_name']).upper()
        fmt = str(row['match_format']).upper()
        if 'IPL' in name or 'INDIAN PREMIER LEAGUE' in name:
            return 'IPL'
        elif 'T20I' in fmt or 'T20I' in name or 'WORLD CUP' in name:
            return 'T20I'
        return 'T20'

    df_clean['comp_type'] = df_clean.apply(classify_comp, axis=1)

    # Deliveries legality:
    # Wides and Oversteps (No-balls) are illegal deliveries in cricket
    df_clean['extras_type_clean'] = df_clean['extras_type'].fillna('None').str.strip().str.lower()
    df_clean['is_wide'] = df_clean['extras_type_clean'] == 'wide'
    df_clean['is_noball'] = df_clean['extras_type_clean'] == 'overstep'
    df_clean['is_legal'] = ~(df_clean['is_wide'] | df_clean['is_noball'])

    # Runs off bat vs extras:
    # In cricket:
    # if wide: runs off bat = 0; runs column might include wide penalty or wide runs
    # if legbyes/byes/penalty: runs off bat = 0
    # if none or noball: runs off bat = runs
    df_clean['runs_off_bat'] = df_clean['runs'].astype(int)
    df_clean.loc[df_clean['is_wide'], 'runs_off_bat'] = 0
    df_clean.loc[df_clean['extras_type_clean'].isin(['legbyes', 'byes', 'penalty']), 'runs_off_bat'] = 0

    # Total runs on delivery (bat runs + extras)
    # Notice extras1_runs and extras_2_runs in raw data
    df_clean['extras_runs'] = df_clean['extras1_runs'].fillna(0).astype(int) + df_clean['extras_2_runs'].fillna(0).astype(int)
    df_clean['total_runs'] = df_clean['runs_off_bat'] + df_clean['extras_runs']

    # For wides: if runs was logged as total runs, ensure total_runs is at least 1 + any running runs
    df_clean.loc[df_clean['is_wide'] & (df_clean['total_runs'] == 0), 'total_runs'] = 1

    # Wicket Flag & Bowler-Credited Dismissals
    # Standard cricket rules: Bowler gets credit for Bowled, Caught, LBW, Stump, Hit Wicket
    # Bowler DOES NOT get credit for RunOut, Retire Out, etc.
    df_clean['is_wicket'] = df_clean['is_wicket'].astype(str).str.lower().isin(['true', '1'])
    bowler_credited_dismissals = ['bowled', 'caught', 'lbw', 'stump', 'hit wicket']
    df_clean['dismissal_type_clean'] = df_clean['dismissal_type'].fillna('').str.strip().str.lower()
    df_clean['bowler_wicket'] = df_clean['is_wicket'] & df_clean['dismissal_type_clean'].isin(bowler_credited_dismissals)

    # Flag DLS/shortened matches so subsequent modules know whether to include in WP training
    df_clean['is_dls_or_shortened'] = df_clean['match_id'].isin(excluded_match_ids)

    # Ensure sorting: match_id, innings, overid, over_ball_num
    df_clean = df_clean.sort_values(['match_id', 'innings', 'overid', 'over_ball_num']).reset_index(drop=True)

    print(f"Master clean delivery table shape: {df_clean.shape[0]:,} rows x {df_clean.shape[1]} columns")
    print(f"IPL deliveries: {(df_clean['comp_type'] == 'IPL').sum():,}")
    print(f"T20I deliveries: {(df_clean['comp_type'] == 'T20I').sum():,}")
    print(f"Legal deliveries: {df_clean['is_legal'].sum():,}")
    print(f"Total wickets: {df_clean['is_wicket'].sum():,}")
    print(f"Bowler-credited wickets: {df_clean['bowler_wicket'].sum():,}")

    # Save to parquet/csv
    master_path_csv = OUTPUTS_DIR / "clean_deliveries_sample.csv"
    df_clean.head(1000).to_csv(master_path_csv, index=False)
    
    # Save full clean master
    full_clean_path = DATA_DIR / "master_clean_deliveries.parquet"
    try:
        df_clean.to_parquet(full_clean_path, index=False)
        print(f"[+] Saved full clean deliveries to: {full_clean_path}")
    except Exception as e:
        full_clean_path = DATA_DIR / "master_clean_deliveries.csv"
        df_clean.to_csv(full_clean_path, index=False)
        print(f"[+] Saved full clean deliveries to: {full_clean_path}")

    return df_clean

if __name__ == "__main__":
    run_data_audit()
