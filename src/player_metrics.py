"""
Stage 4 (Revised): Player Metrics Engine with Match-Level Consistency
Computes:
- Raw batting & bowling rates in High-Pressure vs Ordinary conditions
- Net runs added/saved per 100 balls
- Match-level consistency: Success Rate (% of pressure innings with positive impact)
- Match-level standard deviation of impact (sigma_match)
"""
import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np

sys.path.append(str(Path(__file__).resolve().parent.parent))
from src.config import DATA_DIR, OUTPUTS_DIR, RANDOM_SEED, DEFAULT_WICKET_RUN_VALUE

np.random.seed(RANDOM_SEED)

def compute_player_metrics():
    print("=" * 80)
    print("STAGE 4 (REVISED): COMPUTING BATTER & BOWLER METRICS WITH CONSISTENCY")
    print("=" * 80)

    data_path = DATA_DIR / "master_with_expected_values.csv"
    print(f"Loading data from {data_path}...")
    df = pd.read_csv(data_path, low_memory=False)

    w_val = DEFAULT_WICKET_RUN_VALUE
    phase_w = {'powerplay': 14.36, 'middle': 8.13, 'death': 2.92}

    # 1. BATTERS
    print("\nCalculating Batter Metrics & Match-Level Consistency (Phase-Specific & Flat)...")
    df_bat = df[~df['is_wide']].copy()
    df_bat['w_phase'] = df_bat['phase'].map(phase_w).fillna(w_val)
    df_bat['ball_impact'] = (df_bat['runs_off_bat'] - df_bat['exp_batter_runs']) - df_bat['w_phase'] * (df_bat['is_wicket'].astype(int) - df_bat['exp_batter_out'])
    df_bat['ball_impact_flat'] = (df_bat['runs_off_bat'] - df_bat['exp_batter_runs']) - w_val * (df_bat['is_wicket'].astype(int) - df_bat['exp_batter_out'])

    # Per-match batter impact for consistency
    bat_hp_delivs = df_bat[df_bat['high_pressure'] == 1].copy()
    match_bat_grp = bat_hp_delivs.groupby(['striker_id', 'match_id'])
    match_bat_df = match_bat_grp.apply(
        lambda g: pd.Series({
            'match_impact': g['ball_impact'].sum() / len(g) * 100,
            'match_impact_flat': g['ball_impact_flat'].sum() / len(g) * 100,
            'balls': len(g)
        })
    ).reset_index()

    # Consistency across matches with at least 5 pressure deliveries
    min_match_balls = 5
    m_sig_bat = match_bat_df[match_bat_df['balls'] >= min_match_balls]
    bat_consistency = m_sig_bat.groupby('striker_id').agg(
        pressure_innings_count=('match_id', 'count'),
        positive_innings_count=('match_impact', lambda x: (x > 0).sum()),
        success_rate=('match_impact', lambda x: (x > 0).mean() * 100 if len(x) > 0 else 0.0),
        match_impact_std=('match_impact', lambda x: x.std() if len(x) > 1 else 0.0)
    ).reset_index()

    def agg_batting(group):
        bf = len(group)
        runs = group['runs_off_bat'].sum()
        exp_runs = group['exp_batter_runs'].sum()
        outs = group['is_wicket'].sum()
        exp_outs = group['exp_batter_out'].sum()
        dots = (group['runs_off_bat'] == 0).sum()
        bnds = (group['is_four'] | group['is_six']).sum()
        matches = group['match_id'].nunique()

        sr = (runs / bf * 100) if bf > 0 else 0.0
        avg = (runs / outs) if outs > 0 else (runs if runs > 0 else 0.0)
        dot_pct = (dots / bf * 100) if bf > 0 else 0.0
        bnd_pct = (bnds / bf * 100) if bf > 0 else 0.0

        rae_100 = ((runs - exp_runs) / bf * 100) if bf > 0 else 0.0
        oae_100 = ((outs - exp_outs) / bf * 100) if bf > 0 else 0.0
        impact_100 = (group['ball_impact'].sum() / bf * 100) if bf > 0 else 0.0
        impact_100_flat = (group['ball_impact_flat'].sum() / bf * 100) if bf > 0 else 0.0

        return pd.Series({
            'balls_faced': bf,
            'runs': runs,
            'dismissals': outs,
            'strike_rate': sr,
            'average': avg,
            'dot_pct': dot_pct,
            'boundary_pct': bnd_pct,
            'rae_100': rae_100,
            'oae_100': oae_100,
            'batting_impact_100': impact_100,
            'batting_impact_100_flat': impact_100_flat,
            'matches': matches
        })

    bat_hp = df_bat[df_bat['high_pressure'] == 1].groupby(['striker_id', 'striker_name']).apply(agg_batting).reset_index()
    bat_ord = df_bat[df_bat['high_pressure'] == 0].groupby(['striker_id', 'striker_name']).apply(agg_batting).reset_index()
    bat_total = df_bat.groupby(['striker_id', 'striker_name']).apply(agg_batting).reset_index()

    bat_hp = bat_hp.rename(columns={c: f"{c}_hp" for c in bat_hp.columns if c not in ['striker_id', 'striker_name']})
    bat_ord = bat_ord.rename(columns={c: f"{c}_ord" for c in bat_ord.columns if c not in ['striker_id', 'striker_name']})
    bat_total = bat_total.rename(columns={c: f"{c}_tot" for c in bat_total.columns if c not in ['striker_id', 'striker_name']})

    batters = bat_hp.merge(bat_ord, on=['striker_id', 'striker_name'], how='left')
    batters = batters.merge(bat_total, on=['striker_id', 'striker_name'], how='left')
    batters = batters.merge(bat_consistency, on='striker_id', how='left')
    batters['success_rate'] = batters['success_rate'].fillna(0.0)
    batters['match_impact_std'] = batters['match_impact_std'].fillna(0.0)

    batters['delta_sr'] = batters['strike_rate_hp'] - batters['strike_rate_ord']
    batters['delta_dot_pct'] = batters['dot_pct_hp'] - batters['dot_pct_ord']
    batters['delta_boundary_pct'] = batters['boundary_pct_hp'] - batters['boundary_pct_ord']
    batters['delta_rae_100'] = batters['rae_100_hp'] - batters['rae_100_ord']
    batters['delta_impact_100'] = batters['batting_impact_100_hp'] - batters['batting_impact_100_ord']
    batters['delta_impact_100_flat'] = batters['batting_impact_100_flat_hp'] - batters['batting_impact_100_flat_ord']
    batters['performance_dips'] = batters['delta_impact_100'] < 0

    # 2. BOWLERS
    print("\nCalculating Bowler Metrics & Match-Level Consistency (Phase-Specific & Flat)...")
    df_bowl = df.copy()
    df_bowl['w_phase'] = df_bowl['phase'].map(phase_w).fillna(w_val)
    df_bowl['ball_impact'] = (df_bowl['exp_bowler_runs'] - df_bowl['bowler_runs_conceded']) + df_bowl['w_phase'] * (df_bowl['bowler_wicket'].astype(int) - df_bowl['exp_bowler_wicket'])
    df_bowl['ball_impact_flat'] = (df_bowl['exp_bowler_runs'] - df_bowl['bowler_runs_conceded']) + w_val * (df_bowl['bowler_wicket'].astype(int) - df_bowl['exp_bowler_wicket'])

    bowl_hp_delivs = df_bowl[df_bowl['high_pressure'] == 1].copy()
    match_bowl_grp = bowl_hp_delivs[bowl_hp_delivs['is_legal']].groupby(['bowler_id', 'match_id'])
    match_bowl_df = match_bowl_grp.apply(
        lambda g: pd.Series({
            'match_impact': g['ball_impact'].sum() / len(g) * 100,
            'match_impact_flat': g['ball_impact_flat'].sum() / len(g) * 100,
            'balls': len(g)
        })
    ).reset_index()

    m_sig_bowl = match_bowl_df[match_bowl_df['balls'] >= min_match_balls]
    bowl_consistency = m_sig_bowl.groupby('bowler_id').agg(
        pressure_spells_count=('match_id', 'count'),
        positive_spells_count=('match_impact', lambda x: (x > 0).sum()),
        success_rate=('match_impact', lambda x: (x > 0).mean() * 100 if len(x) > 0 else 0.0),
        match_impact_std=('match_impact', lambda x: x.std() if len(x) > 1 else 0.0)
    ).reset_index()

    def agg_bowling(group):
        legal_balls = group['is_legal'].sum()
        total_balls = len(group)
        runs_conc = group['bowler_runs_conceded'].sum()
        exp_runs_conc = group['exp_bowler_runs'].sum()
        wkts = group['bowler_wicket'].sum()
        exp_wkts = group['exp_bowler_wicket'].sum()
        
        legal_group = group[group['is_legal']]
        dots = (legal_group['bowler_runs_conceded'] == 0).sum()
        bnds = (legal_group['is_four'] | legal_group['is_six']).sum()
        matches = group['match_id'].nunique()

        overs = legal_balls / 6.0
        econ = (runs_conc / overs) if overs > 0 else 0.0
        sr = (legal_balls / wkts) if wkts > 0 else 999.0
        dot_pct = (dots / legal_balls * 100) if legal_balls > 0 else 0.0
        bnd_pct = (bnds / legal_balls * 100) if legal_balls > 0 else 0.0

        rse_100 = ((exp_runs_conc - runs_conc) / legal_balls * 100) if legal_balls > 0 else 0.0
        wae_100 = ((wkts - exp_wkts) / legal_balls * 100) if legal_balls > 0 else 0.0
        impact_100 = (legal_group['ball_impact'].sum() / legal_balls * 100) if legal_balls > 0 else 0.0
        impact_100_flat = (legal_group['ball_impact_flat'].sum() / legal_balls * 100) if legal_balls > 0 else 0.0

        return pd.Series({
            'legal_balls_bowled': legal_balls,
            'total_balls_bowled': total_balls,
            'runs_conceded': runs_conc,
            'wickets': wkts,
            'economy': econ,
            'bowling_sr': sr,
            'dot_pct': dot_pct,
            'boundary_pct': bnd_pct,
            'rse_100': rse_100,
            'wae_100': wae_100,
            'bowling_impact_100': impact_100,
            'bowling_impact_100_flat': impact_100_flat,
            'matches': matches
        })

    bowl_hp = df_bowl[df_bowl['high_pressure'] == 1].groupby(['bowler_id', 'bowler_name']).apply(agg_bowling).reset_index()
    bowl_ord = df_bowl[df_bowl['high_pressure'] == 0].groupby(['bowler_id', 'bowler_name']).apply(agg_bowling).reset_index()
    bowl_total = df_bowl.groupby(['bowler_id', 'bowler_name']).apply(agg_bowling).reset_index()

    bowl_hp = bowl_hp.rename(columns={c: f"{c}_hp" for c in bowl_hp.columns if c not in ['bowler_id', 'bowler_name']})
    bowl_ord = bowl_ord.rename(columns={c: f"{c}_ord" for c in bowl_ord.columns if c not in ['bowler_id', 'bowler_name']})
    bowl_total = bowl_total.rename(columns={c: f"{c}_tot" for c in bowl_total.columns if c not in ['bowler_id', 'bowler_name']})

    bowlers = bowl_hp.merge(bowl_ord, on=['bowler_id', 'bowler_name'], how='left')
    bowlers = bowlers.merge(bowl_total, on=['bowler_id', 'bowler_name'], how='left')
    bowlers = bowlers.merge(bowl_consistency, on='bowler_id', how='left')
    bowlers['success_rate'] = bowlers['success_rate'].fillna(0.0)
    bowlers['match_impact_std'] = bowlers['match_impact_std'].fillna(0.0)

    bowlers['delta_economy'] = bowlers['economy_ord'] - bowlers['economy_hp']
    bowlers['delta_dot_pct'] = bowlers['dot_pct_hp'] - bowlers['dot_pct_ord']
    bowlers['delta_boundary_pct'] = bowlers['boundary_pct_ord'] - bowlers['boundary_pct_hp']
    bowlers['delta_rse_100'] = bowlers['rse_100_hp'] - bowlers['rse_100_ord']
    bowlers['delta_impact_100'] = bowlers['bowling_impact_100_hp'] - bowlers['bowling_impact_100_ord']
    bowlers['delta_impact_100_flat'] = bowlers['bowling_impact_100_flat_hp'] - bowlers['bowling_impact_100_flat_ord']
    bowlers['performance_dips'] = bowlers['delta_impact_100'] < 0

    # Attach team information
    mapping_path = DATA_DIR / "competition_team_player_mapping.csv"
    if mapping_path.exists():
        mapping = pd.read_csv(mapping_path)
        player_teams = mapping.groupby('player_id')['team_name'].unique().apply(lambda x: ', '.join(x)).to_dict()
        batters['teams'] = batters['striker_id'].map(player_teams).fillna('Unknown')
        bowlers['teams'] = bowlers['bowler_id'].map(player_teams).fillna('Unknown')

    batters.to_csv(OUTPUTS_DIR / "raw_player_metrics_batters.csv", index=False)
    bowlers.to_csv(OUTPUTS_DIR / "raw_player_metrics_bowlers.csv", index=False)
    print(f"[+] Saved updated player metrics with consistency to {OUTPUTS_DIR / 'raw_player_metrics_batters.csv'}")
    print(f"[+] Saved updated player metrics with consistency to {OUTPUTS_DIR / 'raw_player_metrics_bowlers.csv'}")

    return batters, bowlers

if __name__ == "__main__":
    compute_player_metrics()
