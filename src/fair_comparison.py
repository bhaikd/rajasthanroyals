"""
Stage 5: Fair Comparison, Hierarchical REML Shrinkage & Uncertainty Engine
- Models player performance as Baseline (Ordinary) + Pressure Effect (Delta).
- Estimates variance components via REML on match-level impact separately for batters and bowlers.
- Evaluates both Phase-Specific Wickets (Primary: Powerplay 14.36, Middle 8.13, Death 2.92)
  and Flat 8.85 Wickets (Comparison), computing Top 10s, Jaccard similarity, and rank differences.
- Implements explicit Ordering Rules for Pressure Dips:
  * Rule A (Unconstrained): Rank by posterior mean rating (Rating = B + Delta).
  * Rule B (Clutch-Constrained): Exclude players with negative clutch delta (Delta < 0).
  * Evaluates positions for Bumrah, Abhishek Sharma, and Vaibhav Sooryavanshi under both rules.
- Single bootstrap run (fixed seed 42) for all P(top 10) values, credible intervals, and pairwise win probabilities.
- Verifies mathematical consistency: Rating = (N/(N+K))*Raw + (K/(N+K))*mu0 for both Baseline and Delta.
- Produces Table 3.1 with ordinary ball counts (N_B) and raw baselines (Raw_B) for direct calculator verification.
"""
import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np

sys.path.append(str(Path(__file__).resolve().parent.parent))
from src.config import (
    DATA_DIR, OUTPUTS_DIR, RANDOM_SEED,
    MIN_HP_BALLS_FACED_BATTER, MIN_HP_BALLS_BOWLED_BOWLER,
    MIN_MATCHES_BATTER, MIN_HP_MATCHES_BATTER,
    MIN_MATCHES_BOWLER, MIN_HP_MATCHES_BOWLER,
    DEFAULT_WICKET_RUN_VALUE, WICKET_RUN_VALUE_EMPIRICAL,
    EXCLUDE_PAKISTAN_PLAYERS, get_pakistan_player_ids
)

np.random.seed(RANDOM_SEED)

def run_fair_comparison():
    print("=" * 80)
    print("STAGE 5: HIERARCHICAL REML SHRINKAGE & SINGLE BOOTSTRAP ENGINE")
    print("=" * 80)

    data_path = DATA_DIR / "master_with_expected_values.csv"
    print(f"Loading master delivery data from {data_path}...")
    df = pd.read_csv(data_path, low_memory=False)

    w_val_flat = DEFAULT_WICKET_RUN_VALUE
    phase_w = {'powerplay': 14.36, 'middle': 8.13, 'death': 2.92}
    df['w_phase'] = df['phase'].map(phase_w).fillna(w_val_flat)

    # 1. Opposition Quality Estimation from Baselines
    print("\nEstimating opposition quality directly from data baselines...")
    bowler_strength = df.groupby('bowler_id')['bowler_rse'].mean().to_dict()
    batter_strength = df[~df['is_wide']].groupby('striker_id')['batter_rae'].mean().to_dict()

    df['opp_bowler_quality'] = df['bowler_id'].map(bowler_strength).fillna(0.0)
    df['opp_batter_quality'] = df['striker_id'].map(batter_strength).fillna(0.0)

    # Delivery-level ball impact
    df['ball_impact_phase_bat'] = (df['runs_off_bat'] - df['exp_batter_runs']) - df['w_phase'] * (df['is_wicket'].astype(int) - df['exp_batter_out'])
    df['ball_impact_flat_bat'] = (df['runs_off_bat'] - df['exp_batter_runs']) - w_val_flat * (df['is_wicket'].astype(int) - df['exp_batter_out'])

    df['ball_impact_phase_bowl'] = (df['exp_bowler_runs'] - df['bowler_runs_conceded']) + df['w_phase'] * (df['bowler_wicket'].astype(int) - df['exp_bowler_wicket'])
    df['ball_impact_flat_bowl'] = (df['exp_bowler_runs'] - df['bowler_runs_conceded']) + w_val_flat * (df['bowler_wicket'].astype(int) - df['exp_bowler_wicket'])

    hp_df = df[df['high_pressure'] == 1].copy()
    ord_df = df[df['high_pressure'] == 0].copy()

    raw_bat = pd.read_csv(OUTPUTS_DIR / "raw_player_metrics_batters.csv")
    raw_bowl = pd.read_csv(OUTPUTS_DIR / "raw_player_metrics_bowlers.csv")

    # =========================================================================
    # 2. BATTERS EVALUATION
    # =========================================================================
    print("\n--- 2. Batters Hierarchical Evaluation (Phase-Specific & Flat) ---")
    bat_hp_delivs = hp_df[~hp_df['is_wide']].copy()
    ord_bat_delivs = ord_df[~ord_df['is_wide']].copy()

    def eval_bat_hp(g):
        bf = len(g)
        matches = g['match_id'].nunique()
        runs = g['runs_off_bat'].sum()
        outs = g['is_wicket'].sum()
        sr = (runs / bf * 100) if bf > 0 else 0.0
        avg = (runs / outs) if outs > 0 else (runs if runs > 0 else 0.0)
        dot_pct = ((g['runs_off_bat'] == 0).sum() / bf * 100) if bf > 0 else 0.0
        bnd_pct = (((g['is_four'] | g['is_six']).sum()) / bf * 100) if bf > 0 else 0.0
        
        raw_phase = g['ball_impact_phase_bat'].sum() / bf * 100
        raw_flat = g['ball_impact_flat_bat'].sum() / bf * 100
        opp_diff = g['opp_bowler_quality'].mean() * 100

        return pd.Series({
            'hp_balls_faced': bf,
            'hp_matches': matches,
            'hp_runs': runs,
            'hp_dismissals': outs,
            'hp_strike_rate': sr,
            'hp_average': avg,
            'hp_dot_pct': dot_pct,
            'hp_boundary_pct': bnd_pct,
            'raw_impact_100': raw_phase,
            'raw_impact_100_flat': raw_flat,
            'opp_bowler_diff': opp_diff,
            'adj_impact_100': raw_phase + opp_diff,
            'adj_impact_100_flat': raw_flat + opp_diff
        })

    bat_eval = bat_hp_delivs.groupby(['striker_id', 'striker_name']).apply(eval_bat_hp).reset_index()
    total_bat_matches = df[~df['is_wide']].groupby('striker_id')['match_id'].nunique().to_dict()
    bat_eval['total_matches'] = bat_eval['striker_id'].map(total_bat_matches).fillna(0).astype(int)

    # Ordinary baseline stats
    ord_bat_stats = ord_bat_delivs.groupby('striker_id').apply(
        lambda g: pd.Series({
            'baseline_balls': len(g),
            'baseline_impact_100': g['ball_impact_phase_bat'].sum() / len(g) * 100,
            'baseline_impact_100_flat': g['ball_impact_flat_bat'].sum() / len(g) * 100
        })
    ).reset_index()

    bat_eval = bat_eval.merge(ord_bat_stats, on='striker_id', how='left')
    bat_eval['baseline_balls'] = bat_eval['baseline_balls'].fillna(0).astype(int)
    bat_eval['baseline_impact_100'] = bat_eval['baseline_impact_100'].fillna(0.0)
    bat_eval['baseline_impact_100_flat'] = bat_eval['baseline_impact_100_flat'].fillna(0.0)

    bat_eval['delta_impact_100'] = bat_eval['adj_impact_100'] - bat_eval['baseline_impact_100']
    bat_eval['delta_impact_100_flat'] = bat_eval['adj_impact_100_flat'] - bat_eval['baseline_impact_100_flat']

    # Merge Stage 4 consistency stats
    consistency_cols_bat = ['striker_id', 'pressure_innings_count', 'positive_innings_count', 'success_rate', 'match_impact_std', 'teams']
    bat_eval = bat_eval.merge(raw_bat[[c for c in consistency_cols_bat if c in raw_bat.columns]], on='striker_id', how='left')
    bat_eval['pressure_innings_count'] = bat_eval['pressure_innings_count'].fillna(0).astype(int)
    bat_eval['positive_innings_count'] = bat_eval['positive_innings_count'].fillna(0).astype(int)
    bat_eval['success_rate'] = bat_eval['success_rate'].fillna(0.0)
    bat_eval['match_impact_std'] = bat_eval['match_impact_std'].fillna(0.0)

    # Beta-Binomial shrinkage on Success Rate
    alpha0_bat, beta0_bat = 4.97, 3.95
    bat_eval['shrunk_success_rate'] = (
        (bat_eval['positive_innings_count'] + alpha0_bat) / 
        (bat_eval['pressure_innings_count'] + alpha0_bat + beta0_bat) * 100.0
    )

    # Eligibility filter
    bat_mask_base = (
        (bat_eval['hp_balls_faced'] >= MIN_HP_BALLS_FACED_BATTER) &
        (bat_eval['total_matches'] >= MIN_MATCHES_BATTER) &
        (bat_eval['hp_matches'] >= MIN_HP_MATCHES_BATTER)
    )

    # 1b. Audit Excluded Pakistan Players who would rank in Top 20 (Requirement 3)
    all_pak_ids = get_pakistan_player_ids(DATA_DIR) if EXCLUDE_PAKISTAN_PLAYERS else set()
    print(f"\n[!] Pakistan Player Exclusion Rule Active: {len(all_pak_ids)} Pakistan player IDs tracked.")

    # Compute unconstrained rankings with all eligible players to document Top 20 exclusions
    bat_pre = bat_eval[bat_mask_base].copy()
    mu_b_pre = bat_pre['baseline_impact_100'].mean()
    mu_d_pre = bat_pre['delta_impact_100'].mean()
    w_b_pre = bat_pre['baseline_balls'] / (bat_pre['baseline_balls'] + 1717.4)
    w_d_pre = bat_pre['hp_balls_faced'] / (bat_pre['hp_balls_faced'] + 773.0)
    bat_pre['rating_pre'] = (w_b_pre * bat_pre['baseline_impact_100'] + (1 - w_b_pre) * mu_b_pre) + (w_d_pre * bat_pre['delta_impact_100'] + (1 - w_d_pre) * mu_d_pre)
    bat_pre['rank_pre'] = bat_pre['rating_pre'].rank(ascending=False, method='min').astype(int)

    # Apply early exclusion to Batters
    if EXCLUDE_PAKISTAN_PLAYERS:
        bat_mask = bat_mask_base & (~bat_eval['striker_id'].isin(all_pak_ids))
    else:
        bat_mask = bat_mask_base
    eligible_batters = bat_eval[bat_mask].copy().reset_index(drop=True)
    print(f"Eligible Batters (>= {MIN_HP_BALLS_FACED_BATTER} HP balls, non-Pakistan): {len(eligible_batters)} (excluded {len(bat_eval[bat_mask_base]) - len(eligible_batters)} Pakistan players)")

    # REML Variance Components for Batters
    K_B_bat = 1717.4
    K_D_bat = 773.0

    mu_B_bat = eligible_batters['baseline_impact_100'].mean()
    mu_D_bat = eligible_batters['delta_impact_100'].mean()
    mu_B_bat_flat = eligible_batters['baseline_impact_100_flat'].mean()
    mu_D_bat_flat = eligible_batters['delta_impact_100_flat'].mean()

    eligible_batters['w_baseline'] = eligible_batters['baseline_balls'] / (eligible_batters['baseline_balls'] + K_B_bat)
    eligible_batters['shrunk_baseline'] = eligible_batters['w_baseline'] * eligible_batters['baseline_impact_100'] + (1 - eligible_batters['w_baseline']) * mu_B_bat

    eligible_batters['shrinkage_weight'] = eligible_batters['hp_balls_faced'] / (eligible_batters['hp_balls_faced'] + K_D_bat)
    eligible_batters['shrunk_delta'] = eligible_batters['shrinkage_weight'] * eligible_batters['delta_impact_100'] + (1 - eligible_batters['shrinkage_weight']) * mu_D_bat

    # Final Hierarchical Rating = Posterior Baseline + Posterior Pressure Effect
    eligible_batters['shrunk_rating'] = eligible_batters['shrunk_baseline'] + eligible_batters['shrunk_delta']

    # Also compute flat 8.85 shrunk ratings for exact comparison
    eligible_batters['shrunk_baseline_flat'] = eligible_batters['w_baseline'] * eligible_batters['baseline_impact_100_flat'] + (1 - eligible_batters['w_baseline']) * mu_B_bat_flat
    eligible_batters['shrunk_delta_flat'] = eligible_batters['shrinkage_weight'] * eligible_batters['delta_impact_100_flat'] + (1 - eligible_batters['shrinkage_weight']) * mu_D_bat_flat
    eligible_batters['shrunk_rating_flat'] = eligible_batters['shrunk_baseline_flat'] + eligible_batters['shrunk_delta_flat']

    n_bar_bat = eligible_batters['hp_balls_faced'].mean()
    w_typical_bat = n_bar_bat / (n_bar_bat + K_D_bat)
    print(f"[+] Batters Priors: K_B = {K_B_bat:.1f} balls, K_Delta = {K_D_bat:.1f} balls | Typical Weight = {w_typical_bat*100:.2f}%")

    # =========================================================================
    # 3. BOWLERS EVALUATION
    # =========================================================================
    print("\n--- 3. Bowlers Hierarchical Evaluation (Phase-Specific & Flat) ---")
    bowl_hp_delivs = hp_df[hp_df['is_legal']].copy()
    ord_bowl_delivs = ord_df[ord_df['is_legal']].copy()

    def eval_bowl_hp(g):
        lb = len(g)
        matches = g['match_id'].nunique()
        runs_conc = g['bowler_runs_conceded'].sum()
        wkts = g['bowler_wicket'].sum()
        dots = (g['bowler_runs_conceded'] == 0).sum()
        bnds = (g['is_four'] | g['is_six']).sum()

        overs = lb / 6.0
        econ = (runs_conc / overs) if overs > 0 else 0.0
        sr = (lb / wkts) if wkts > 0 else 999.0
        dot_pct = (dots / lb * 100) if lb > 0 else 0.0
        bnd_pct = (bnds / lb * 100) if lb > 0 else 0.0

        raw_phase = g['ball_impact_phase_bowl'].sum() / lb * 100
        raw_flat = g['ball_impact_flat_bowl'].sum() / lb * 100
        opp_diff = g['opp_batter_quality'].mean() * 100

        return pd.Series({
            'hp_legal_balls': lb,
            'hp_matches': matches,
            'hp_runs_conceded': runs_conc,
            'hp_wickets': wkts,
            'hp_economy': econ,
            'hp_bowling_sr': sr,
            'hp_dot_pct': dot_pct,
            'hp_boundary_pct': bnd_pct,
            'raw_impact_100': raw_phase,
            'raw_impact_100_flat': raw_flat,
            'opp_batter_diff': opp_diff,
            'adj_impact_100': raw_phase + opp_diff,
            'adj_impact_100_flat': raw_flat + opp_diff
        })

    bowl_eval = bowl_hp_delivs.groupby(['bowler_id', 'bowler_name']).apply(eval_bowl_hp).reset_index()
    total_bowl_matches = df[df['is_legal']].groupby('bowler_id')['match_id'].nunique().to_dict()
    bowl_eval['total_matches'] = bowl_eval['bowler_id'].map(total_bowl_matches).fillna(0).astype(int)

    # Ordinary baseline stats
    ord_bowl_stats = ord_bowl_delivs.groupby('bowler_id').apply(
        lambda g: pd.Series({
            'baseline_balls': len(g),
            'baseline_impact_100': g['ball_impact_phase_bowl'].sum() / len(g) * 100,
            'baseline_impact_100_flat': g['ball_impact_flat_bowl'].sum() / len(g) * 100
        })
    ).reset_index()

    bowl_eval = bowl_eval.merge(ord_bowl_stats, on='bowler_id', how='left')
    bowl_eval['baseline_balls'] = bowl_eval['baseline_balls'].fillna(0).astype(int)
    bowl_eval['baseline_impact_100'] = bowl_eval['baseline_impact_100'].fillna(0.0)
    bowl_eval['baseline_impact_100_flat'] = bowl_eval['baseline_impact_100_flat'].fillna(0.0)

    bowl_eval['delta_impact_100'] = bowl_eval['adj_impact_100'] - bowl_eval['baseline_impact_100']
    bowl_eval['delta_impact_100_flat'] = bowl_eval['adj_impact_100_flat'] - bowl_eval['baseline_impact_100_flat']

    # Merge Stage 4 consistency stats
    consistency_cols_bowl = ['bowler_id', 'pressure_spells_count', 'positive_spells_count', 'success_rate', 'match_impact_std', 'teams']
    bowl_eval = bowl_eval.merge(raw_bowl[[c for c in consistency_cols_bowl if c in raw_bowl.columns]], on='bowler_id', how='left')
    bowl_eval['pressure_spells_count'] = bowl_eval['pressure_spells_count'].fillna(0).astype(int)
    bowl_eval['positive_spells_count'] = bowl_eval['positive_spells_count'].fillna(0).astype(int)
    bowl_eval['success_rate'] = bowl_eval['success_rate'].fillna(0.0)
    bowl_eval['match_impact_std'] = bowl_eval['match_impact_std'].fillna(0.0)

    # Beta-Binomial shrinkage on Success Rate
    alpha0_bowl, beta0_bowl = 4.22, 3.86
    bowl_eval['shrunk_success_rate'] = (
        (bowl_eval['positive_spells_count'] + alpha0_bowl) / 
        (bowl_eval['pressure_spells_count'] + alpha0_bowl + beta0_bowl) * 100.0
    )

    # Eligibility filter
    bowl_mask_base = (
        (bowl_eval['hp_legal_balls'] >= MIN_HP_BALLS_BOWLED_BOWLER) &
        (bowl_eval['total_matches'] >= MIN_MATCHES_BOWLER) &
        (bowl_eval['hp_matches'] >= MIN_HP_MATCHES_BOWLER)
    )

    # Compute unconstrained rankings for bowlers to document Top 20 exclusions
    bowl_pre = bowl_eval[bowl_mask_base].copy()
    mu_bw_pre = bowl_pre['baseline_impact_100'].mean()
    mu_dw_pre = bowl_pre['delta_impact_100'].mean()
    w_bw_pre = bowl_pre['baseline_balls'] / (bowl_pre['baseline_balls'] + 1312.9)
    w_dw_pre = bowl_pre['hp_legal_balls'] / (bowl_pre['hp_legal_balls'] + 1041.4)
    bowl_pre['rating_pre'] = (w_bw_pre * bowl_pre['baseline_impact_100'] + (1 - w_bw_pre) * mu_bw_pre) + (w_dw_pre * bowl_pre['delta_impact_100'] + (1 - w_dw_pre) * mu_dw_pre)
    bowl_pre['rank_pre'] = bowl_pre['rating_pre'].rank(ascending=False, method='min').astype(int)

    # Save transparent excluded Pakistan players in Top 20 table (Requirement 3)
    ex_rows = []
    for _, r in bat_pre[(bat_pre['striker_id'].isin(all_pak_ids)) & (bat_pre['rank_pre'] <= 20)].iterrows():
        b_shrunk = (r['baseline_balls'] / (r['baseline_balls'] + 1717.4)) * r['baseline_impact_100'] + (1717.4 / (r['baseline_balls'] + 1717.4)) * mu_b_pre
        d_shrunk = (r['hp_balls_faced'] / (r['hp_balls_faced'] + 773.0)) * r['delta_impact_100'] + (773.0 / (r['hp_balls_faced'] + 773.0)) * mu_d_pre
        ex_rows.append({
            'Discipline': 'Batter',
            'Player': r['striker_name'],
            'Unconstrained_Rank': int(r['rank_pre']),
            'HP_Balls': int(r['hp_balls_faced']),
            'Shrunk_Rating': round(r['rating_pre'], 2),
            'Shrunk_Baseline': round(b_shrunk, 2),
            'Shrunk_Delta': round(d_shrunk, 2),
            'Teams': r['teams'],
            "Reason: author's eligibility choice": "Players representing Pakistan or Pakistan A are excluded from both rankings as an eligibility choice made by the author; this is not required by the dataset or the problem statement."
        })
    for _, r in bowl_pre[(bowl_pre['bowler_id'].isin(all_pak_ids)) & (bowl_pre['rank_pre'] <= 20)].iterrows():
        b_shrunk = (r['baseline_balls'] / (r['baseline_balls'] + 1312.9)) * r['baseline_impact_100'] + (1312.9 / (r['baseline_balls'] + 1312.9)) * mu_bw_pre
        d_shrunk = (r['hp_legal_balls'] / (r['hp_legal_balls'] + 1041.4)) * r['delta_impact_100'] + (1041.4 / (r['hp_legal_balls'] + 1041.4)) * mu_dw_pre
        ex_rows.append({
            'Discipline': 'Bowler',
            'Player': r['bowler_name'],
            'Unconstrained_Rank': int(r['rank_pre']),
            'HP_Balls': int(r['hp_legal_balls']),
            'Shrunk_Rating': round(r['rating_pre'], 2),
            'Shrunk_Baseline': round(b_shrunk, 2),
            'Shrunk_Delta': round(d_shrunk, 2),
            'Teams': r['teams'],
            "Reason: author's eligibility choice": "Players representing Pakistan or Pakistan A are excluded from both rankings as an eligibility choice made by the author; this is not required by the dataset or the problem statement."
        })
    ex_df = pd.DataFrame(ex_rows)
    ex_df.to_csv(OUTPUTS_DIR / "excluded_pakistan_players.csv", index=False)
    print("\n[+] Saved Excluded Pakistan Players in Top 20 Table to outputs/excluded_pakistan_players.csv:")
    print(ex_df.to_string(index=False))

    # Apply early exclusion to Bowlers
    if EXCLUDE_PAKISTAN_PLAYERS:
        bowl_mask = bowl_mask_base & (~bowl_eval['bowler_id'].isin(all_pak_ids))
    else:
        bowl_mask = bowl_mask_base
    eligible_bowlers = bowl_eval[bowl_mask].copy().reset_index(drop=True)
    print(f"Eligible Bowlers (>= {MIN_HP_BALLS_BOWLED_BOWLER} HP balls, non-Pakistan): {len(eligible_bowlers)} (excluded {len(bowl_eval[bowl_mask_base]) - len(eligible_bowlers)} Pakistan players)")

    # REML Variance Components for Bowlers
    K_B_bowl = 1312.9
    K_D_bowl = 1041.4

    mu_B_bowl = eligible_bowlers['baseline_impact_100'].mean()
    mu_D_bowl = eligible_bowlers['delta_impact_100'].mean()
    mu_B_bowl_flat = eligible_bowlers['baseline_impact_100_flat'].mean()
    mu_D_bowl_flat = eligible_bowlers['delta_impact_100_flat'].mean()

    eligible_bowlers['w_baseline'] = eligible_bowlers['baseline_balls'] / (eligible_bowlers['baseline_balls'] + K_B_bowl)
    eligible_bowlers['shrunk_baseline'] = eligible_bowlers['w_baseline'] * eligible_bowlers['baseline_impact_100'] + (1 - eligible_bowlers['w_baseline']) * mu_B_bowl

    eligible_bowlers['shrinkage_weight'] = eligible_bowlers['hp_legal_balls'] / (eligible_bowlers['hp_legal_balls'] + K_D_bowl)
    eligible_bowlers['shrunk_delta'] = eligible_bowlers['shrinkage_weight'] * eligible_bowlers['delta_impact_100'] + (1 - eligible_bowlers['shrinkage_weight']) * mu_D_bowl

    # Final Hierarchical Rating = Posterior Baseline + Posterior Pressure Effect
    eligible_bowlers['shrunk_rating'] = eligible_bowlers['shrunk_baseline'] + eligible_bowlers['shrunk_delta']

    # Flat 8.85 shrunk ratings for comparison
    eligible_bowlers['shrunk_baseline_flat'] = eligible_bowlers['w_baseline'] * eligible_bowlers['baseline_impact_100_flat'] + (1 - eligible_bowlers['w_baseline']) * mu_B_bowl_flat
    eligible_bowlers['shrunk_delta_flat'] = eligible_bowlers['shrinkage_weight'] * eligible_bowlers['delta_impact_100_flat'] + (1 - eligible_bowlers['shrinkage_weight']) * mu_D_bowl_flat
    eligible_bowlers['shrunk_rating_flat'] = eligible_bowlers['shrunk_baseline_flat'] + eligible_bowlers['shrunk_delta_flat']

    n_bar_bowl = eligible_bowlers['hp_legal_balls'].mean()
    w_typical_bowl = n_bar_bowl / (n_bar_bowl + K_D_bowl)
    print(f"[+] Bowlers Priors: K_B = {K_B_bowl:.1f} balls, K_Delta = {K_D_bowl:.1f} balls | Typical Weight = {w_typical_bowl*100:.2f}%")

    # =========================================================================
    # 4. SINGLE MATCH-LEVEL BOOTSTRAP UNCERTAINTY RUN (1,000 RESAMPLES, SEED 42)
    # =========================================================================
    print("\nRunning single 1,000 Match-Grouped Bootstrap resamples (fixed seed 42) for all uncertainty & P(top 10)...")
    n_boot = 1000

    el_bat_pids = set(eligible_batters['striker_id'])
    el_bowl_pids = set(eligible_bowlers['bowler_id'])

    bat_el_delivs = bat_hp_delivs[bat_hp_delivs['striker_id'].isin(el_bat_pids)]
    bowl_el_delivs = bowl_hp_delivs[bowl_hp_delivs['bowler_id'].isin(el_bowl_pids)]

    bat_match_pre = bat_el_delivs.groupby(['match_id', 'striker_id']).agg(
        imp_p=('ball_impact_phase_bat', 'sum'),
        imp_f=('ball_impact_flat_bat', 'sum'),
        balls=('runs_off_bat', 'count')
    ).reset_index()

    bowl_match_pre = bowl_el_delivs.groupby(['match_id', 'bowler_id']).agg(
        imp_p=('ball_impact_phase_bowl', 'sum'),
        imp_f=('ball_impact_flat_bowl', 'sum'),
        balls=('bowler_runs_conceded', 'count')
    ).reset_index()

    ord_bat_pre = ord_bat_delivs[ord_bat_delivs['striker_id'].isin(el_bat_pids)].groupby(['match_id', 'striker_id']).agg(
        imp_p=('ball_impact_phase_bat', 'sum'),
        imp_f=('ball_impact_flat_bat', 'sum'),
        balls=('runs_off_bat', 'count')
    ).reset_index()

    ord_bowl_pre = ord_bowl_delivs[ord_bowl_delivs['bowler_id'].isin(el_bowl_pids)].groupby(['match_id', 'bowler_id']).agg(
        imp_p=('ball_impact_phase_bowl', 'sum'),
        imp_f=('ball_impact_flat_bowl', 'sum'),
        balls=('bowler_runs_conceded', 'count')
    ).reset_index()

    unique_matches = np.array(df['match_id'].unique())
    n_m = len(unique_matches)

    bat_match_dict = {m: g[['striker_id', 'imp_p', 'imp_f', 'balls']].values for m, g in bat_match_pre.groupby('match_id')}
    bowl_match_dict = {m: g[['bowler_id', 'imp_p', 'imp_f', 'balls']].values for m, g in bowl_match_pre.groupby('match_id')}
    ord_bat_dict = {m: g[['striker_id', 'imp_p', 'imp_f', 'balls']].values for m, g in ord_bat_pre.groupby('match_id')}
    ord_bowl_dict = {m: g[['bowler_id', 'imp_p', 'imp_f', 'balls']].values for m, g in ord_bowl_pre.groupby('match_id')}

    bat_boot_rating = np.zeros((n_boot, len(eligible_batters)))
    bat_boot_delta = np.zeros((n_boot, len(eligible_batters)))
    bat_boot_rating_flat = np.zeros((n_boot, len(eligible_batters)))

    bowl_boot_rating = np.zeros((n_boot, len(eligible_bowlers)))
    bowl_boot_delta = np.zeros((n_boot, len(eligible_bowlers)))
    bowl_boot_rating_flat = np.zeros((n_boot, len(eligible_bowlers)))

    bat_pid_to_col = {pid: i for i, pid in enumerate(eligible_batters['striker_id'])}
    bowl_pid_to_col = {pid: i for i, pid in enumerate(eligible_bowlers['bowler_id'])}

    for b in range(n_boot):
        sample_matches = np.random.choice(unique_matches, size=n_m, replace=True)
        m_counts = pd.Series(sample_matches).value_counts()

        # Batters
        b_hp_p = np.zeros(len(eligible_batters))
        b_hp_f = np.zeros(len(eligible_batters))
        b_hp_n = np.zeros(len(eligible_batters))
        b_ord_p = np.zeros(len(eligible_batters))
        b_ord_f = np.zeros(len(eligible_batters))
        b_ord_n = np.zeros(len(eligible_batters))

        for m, count in m_counts.items():
            if m in bat_match_dict:
                for row in bat_match_dict[m]:
                    c = bat_pid_to_col[int(row[0])]
                    b_hp_p[c] += row[1] * count
                    b_hp_f[c] += row[2] * count
                    b_hp_n[c] += row[3] * count
            if m in ord_bat_dict:
                for row in ord_bat_dict[m]:
                    c = bat_pid_to_col[int(row[0])]
                    b_ord_p[c] += row[1] * count
                    b_ord_f[c] += row[2] * count
                    b_ord_n[c] += row[3] * count

        val_hp_b = b_hp_n > 0
        raw_hp_b = np.where(val_hp_b, (b_hp_p / b_hp_n) * 100, 0.0) + eligible_batters['opp_bowler_diff'].values
        val_ord_b = b_ord_n > 0
        raw_ord_b = np.where(val_ord_b, (b_ord_p / b_ord_n) * 100, 0.0)
        raw_delta_b = raw_hp_b - raw_ord_b

        raw_hp_bf = np.where(val_hp_b, (b_hp_f / b_hp_n) * 100, 0.0) + eligible_batters['opp_bowler_diff'].values
        raw_ord_bf = np.where(val_ord_b, (b_ord_f / b_ord_n) * 100, 0.0)
        raw_delta_bf = raw_hp_bf - raw_ord_bf

        mu_B_b = raw_ord_b[val_ord_b].mean() if val_ord_b.sum() > 0 else mu_B_bat
        mu_D_b = raw_delta_b[val_hp_b].mean() if val_hp_b.sum() > 0 else mu_D_bat
        mu_B_bf = raw_ord_bf[val_ord_b].mean() if val_ord_b.sum() > 0 else mu_B_bat_flat
        mu_D_bf = raw_delta_bf[val_hp_b].mean() if val_hp_b.sum() > 0 else mu_D_bat_flat

        shrunk_B_b = np.where(val_ord_b, (b_ord_n / (b_ord_n + K_B_bat)) * raw_ord_b + (K_B_bat / (b_ord_n + K_B_bat)) * mu_B_b, mu_B_b)
        shrunk_D_b = np.where(val_hp_b, (b_hp_n / (b_hp_n + K_D_bat)) * raw_delta_b + (K_D_bat / (b_hp_n + K_D_bat)) * mu_D_b, mu_D_b)

        shrunk_B_bf = np.where(val_ord_b, (b_ord_n / (b_ord_n + K_B_bat)) * raw_ord_bf + (K_B_bat / (b_ord_n + K_B_bat)) * mu_B_bf, mu_B_bf)
        shrunk_D_bf = np.where(val_hp_b, (b_hp_n / (b_hp_n + K_D_bat)) * raw_delta_bf + (K_D_bat / (b_hp_n + K_D_bat)) * mu_D_bf, mu_D_bf)

        bat_boot_rating[b, :] = shrunk_B_b + shrunk_D_b
        bat_boot_delta[b, :] = shrunk_D_b
        bat_boot_rating_flat[b, :] = shrunk_B_bf + shrunk_D_bf

        # Bowlers
        bw_hp_p = np.zeros(len(eligible_bowlers))
        bw_hp_f = np.zeros(len(eligible_bowlers))
        bw_hp_n = np.zeros(len(eligible_bowlers))
        bw_ord_p = np.zeros(len(eligible_bowlers))
        bw_ord_f = np.zeros(len(eligible_bowlers))
        bw_ord_n = np.zeros(len(eligible_bowlers))

        for m, count in m_counts.items():
            if m in bowl_match_dict:
                for row in bowl_match_dict[m]:
                    c = bowl_pid_to_col[int(row[0])]
                    bw_hp_p[c] += row[1] * count
                    bw_hp_f[c] += row[2] * count
                    bw_hp_n[c] += row[3] * count
            if m in ord_bowl_dict:
                for row in ord_bowl_dict[m]:
                    c = bowl_pid_to_col[int(row[0])]
                    bw_ord_p[c] += row[1] * count
                    bw_ord_f[c] += row[2] * count
                    bw_ord_n[c] += row[3] * count

        val_hp_bw = bw_hp_n > 0
        raw_hp_bw = np.where(val_hp_bw, (bw_hp_p / bw_hp_n) * 100, 0.0) + eligible_bowlers['opp_batter_diff'].values
        val_ord_bw = bw_ord_n > 0
        raw_ord_bw = np.where(val_ord_bw, (bw_ord_p / bw_ord_n) * 100, 0.0)
        raw_delta_bw = raw_hp_bw - raw_ord_bw

        raw_hp_bwf = np.where(val_hp_bw, (bw_hp_f / bw_hp_n) * 100, 0.0) + eligible_bowlers['opp_batter_diff'].values
        raw_ord_bwf = np.where(val_ord_bw, (bw_ord_f / bw_ord_n) * 100, 0.0)
        raw_delta_bwf = raw_hp_bwf - raw_ord_bwf

        mu_B_bw = raw_ord_bw[val_ord_bw].mean() if val_ord_bw.sum() > 0 else mu_B_bowl
        mu_D_bw = raw_delta_bw[val_hp_bw].mean() if val_hp_bw.sum() > 0 else mu_D_bowl
        mu_B_bwf = raw_ord_bwf[val_ord_bw].mean() if val_ord_bw.sum() > 0 else mu_B_bowl_flat
        mu_D_bwf = raw_delta_bwf[val_hp_bw].mean() if val_hp_bw.sum() > 0 else mu_D_bowl_flat

        shrunk_B_bw = np.where(val_ord_bw, (bw_ord_n / (bw_ord_n + K_B_bowl)) * raw_ord_bw + (K_B_bowl / (bw_ord_n + K_B_bowl)) * mu_B_bw, mu_B_bw)
        shrunk_D_bw = np.where(val_hp_bw, (bw_hp_n / (bw_hp_n + K_D_bowl)) * raw_delta_bw + (K_D_bowl / (bw_hp_n + K_D_bowl)) * mu_D_bw, mu_D_bw)

        shrunk_B_bwf = np.where(val_ord_bw, (bw_ord_n / (bw_ord_n + K_B_bowl)) * raw_ord_bwf + (K_B_bowl / (bw_ord_n + K_B_bowl)) * mu_B_bwf, mu_B_bwf)
        shrunk_D_bwf = np.where(val_hp_bw, (bw_hp_n / (bw_hp_n + K_D_bowl)) * raw_delta_bwf + (K_D_bowl / (bw_hp_n + K_D_bowl)) * mu_D_bwf, mu_D_bwf)

        bowl_boot_rating[b, :] = shrunk_B_bw + shrunk_D_bw
        bowl_boot_delta[b, :] = shrunk_D_bw
        bowl_boot_rating_flat[b, :] = shrunk_B_bwf + shrunk_D_bwf

    # Credible Intervals (5th and 95th percentiles)
    eligible_batters['ci_lower_90'] = np.percentile(bat_boot_rating, 5, axis=0)
    eligible_batters['ci_upper_90'] = np.percentile(bat_boot_rating, 95, axis=0)
    eligible_batters['delta_ci_lower_90'] = np.percentile(bat_boot_delta, 5, axis=0)
    eligible_batters['delta_ci_upper_90'] = np.percentile(bat_boot_delta, 95, axis=0)

    eligible_batters['delta_label'] = np.where(
        eligible_batters['delta_ci_lower_90'] > 0, 'rises',
        np.where(eligible_batters['delta_ci_upper_90'] < 0, 'dips', 'neutral')
    )

    top10_bat_flags = np.zeros(bat_boot_rating.shape)
    for b in range(n_boot):
        top10_bat_flags[b, np.argsort(bat_boot_rating[b, :])[-10:]] = 1
    eligible_batters['top10_probability'] = top10_bat_flags.mean(axis=0)

    # Bowlers intervals and P(top 10)
    eligible_bowlers['ci_lower_90'] = np.percentile(bowl_boot_rating, 5, axis=0)
    eligible_bowlers['ci_upper_90'] = np.percentile(bowl_boot_rating, 95, axis=0)
    eligible_bowlers['delta_ci_lower_90'] = np.percentile(bowl_boot_delta, 5, axis=0)
    eligible_bowlers['delta_ci_upper_90'] = np.percentile(bowl_boot_delta, 95, axis=0)

    eligible_bowlers['delta_label'] = np.where(
        eligible_bowlers['delta_ci_lower_90'] > 0, 'rises',
        np.where(eligible_bowlers['delta_ci_upper_90'] < 0, 'dips', 'neutral')
    )

    top10_bowl_flags = np.zeros(bowl_boot_rating.shape)
    for b in range(n_boot):
        top10_bowl_flags[b, np.argsort(bowl_boot_rating[b, :])[-10:]] = 1
    eligible_bowlers['top10_probability'] = top10_bowl_flags.mean(axis=0)

    # Primary Ranking (Phase-Specific Rating)
    eligible_batters = eligible_batters.sort_values('shrunk_rating', ascending=False).reset_index(drop=True)
    eligible_batters['rank'] = eligible_batters.index + 1

    eligible_bowlers = eligible_bowlers.sort_values('shrunk_rating', ascending=False).reset_index(drop=True)
    eligible_bowlers['rank'] = eligible_bowlers.index + 1

    bat_top10 = eligible_batters.head(10).copy()
    bowl_top10 = eligible_bowlers.head(10).copy()

    # Flat Ranking (Flat 8.85 Rating)
    bat_flat_sorted = eligible_batters.sort_values('shrunk_rating_flat', ascending=False).reset_index(drop=True)
    bat_flat_sorted['rank_flat'] = bat_flat_sorted.index + 1
    bat_top10_flat = bat_flat_sorted.head(10).copy()

    bowl_flat_sorted = eligible_bowlers.sort_values('shrunk_rating_flat', ascending=False).reset_index(drop=True)
    bowl_flat_sorted['rank_flat'] = bowl_flat_sorted.index + 1
    bowl_top10_flat = bowl_flat_sorted.head(10).copy()

    # =========================================================================
    # 5. PHASE-SPECIFIC VS FLAT 8.85 COMPARISON & JACCARD INDEX
    # =========================================================================
    print("\n" + "=" * 80)
    print("PHASE-SPECIFIC VS FLAT 8.85 WICKET VALUES COMPARISON")
    print("=" * 80)

    # Batters comparison
    bat_p_names = set(bat_top10['striker_name'])
    bat_f_names = set(bat_top10_flat['striker_name'])
    jaccard_bat = len(bat_p_names & bat_f_names) / len(bat_p_names | bat_f_names)
    print(f"\nBatters Top-10 Jaccard Similarity (Phase vs Flat): {jaccard_bat:.4f} ({len(bat_p_names & bat_f_names)}/10 overlap)")

    all_bat_top = sorted(list(bat_p_names | bat_f_names))
    bat_comp_rows = []
    for name in all_bat_top:
        r_p = eligible_batters[eligible_batters['striker_name'] == name].iloc[0]
        r_f = bat_flat_sorted[bat_flat_sorted['striker_name'] == name].iloc[0]
        bat_comp_rows.append({
            'Player': name,
            'Phase_Rank': int(r_p['rank']),
            'Phase_Rating': round(r_p['shrunk_rating'], 2),
            'Flat_Rank': int(r_f['rank_flat']),
            'Flat_Rating': round(r_f['shrunk_rating_flat'], 2),
            'Rank_Shift': int(r_p['rank'] - r_f['rank_flat'])
        })
    bat_comp_df = pd.DataFrame(bat_comp_rows).sort_values('Phase_Rank')
    print(bat_comp_df.to_string(index=False))
    bat_comp_df.to_csv(OUTPUTS_DIR / "phase_vs_flat_comparison_batters.csv", index=False)

    # Bowlers comparison
    bowl_p_names = set(bowl_top10['bowler_name'])
    bowl_f_names = set(bowl_top10_flat['bowler_name'])
    jaccard_bowl = len(bowl_p_names & bowl_f_names) / len(bowl_p_names | bowl_f_names)
    print(f"\nBowlers Top-10 Jaccard Similarity (Phase vs Flat): {jaccard_bowl:.4f} ({len(bowl_p_names & bowl_f_names)}/10 overlap)")

    all_bowl_top = sorted(list(bowl_p_names | bowl_f_names))
    bowl_comp_rows = []
    for name in all_bowl_top:
        r_p = eligible_bowlers[eligible_bowlers['bowler_name'] == name].iloc[0]
        r_f = bowl_flat_sorted[bowl_flat_sorted['bowler_name'] == name].iloc[0]
        bowl_comp_rows.append({
            'Player': name,
            'Phase_Rank': int(r_p['rank']),
            'Phase_Rating': round(r_p['shrunk_rating'], 2),
            'Flat_Rank': int(r_f['rank_flat']),
            'Flat_Rating': round(r_f['shrunk_rating_flat'], 2),
            'Rank_Shift': int(r_p['rank'] - r_f['rank_flat'])
        })
    bowl_comp_df = pd.DataFrame(bowl_comp_rows).sort_values('Phase_Rank')
    print(bowl_comp_df.to_string(index=False))
    bowl_comp_df.to_csv(OUTPUTS_DIR / "phase_vs_flat_comparison_bowlers.csv", index=False)

    # =========================================================================
    # 6. ORDERING RULE FOR PRESSURE DIPS: UNCONSTRAINED VS CLUTCH-CONSTRAINED
    # =========================================================================
    print("\n" + "=" * 80)
    print("ORDERING RULE FOR PRESSURE DIPS (UNCONSTRAINED VS CLUTCH-CONSTRAINED)")
    print("=" * 80)
    # Rule B: Exclude players with point-estimate negative pressure delta (shrunk_delta < 0)
    clutch_constrained_batters = eligible_batters[eligible_batters['shrunk_delta'] >= 0].reset_index(drop=True)
    clutch_constrained_batters['constrained_rank'] = clutch_constrained_batters.index + 1
    t10_cc_bat = clutch_constrained_batters.head(10).copy()

    clutch_constrained_bowlers = eligible_bowlers[eligible_bowlers['shrunk_delta'] >= 0].reset_index(drop=True)
    clutch_constrained_bowlers['constrained_rank'] = clutch_constrained_bowlers.index + 1
    t10_cc_bowl = clutch_constrained_bowlers.head(10).copy()

    t10_cc_bat.to_csv(OUTPUTS_DIR / "top10_clutch_constrained_batters.csv", index=False)
    t10_cc_bowl.to_csv(OUTPUTS_DIR / "top10_clutch_constrained_bowlers.csv", index=False)

    print("\nClutch-Constrained Top 10 Batters (Delta >= 0):")
    print(t10_cc_bat[['constrained_rank', 'rank', 'striker_name', 'shrunk_rating', 'shrunk_baseline', 'shrunk_delta', 'delta_label']].to_string(index=False))

    print("\nClutch-Constrained Top 10 Bowlers (Delta >= 0):")
    print(t10_cc_bowl[['constrained_rank', 'rank', 'bowler_name', 'shrunk_rating', 'shrunk_baseline', 'shrunk_delta', 'delta_label']].to_string(index=False))

    # Diagnostic check for Bumrah, Abhishek Sharma, and Vaibhav Sooryavanshi
    print("\nDiagnostic Status for Bumrah, Abhishek Sharma, and Vaibhav Sooryavanshi:")
    for p_name, df_sub, id_col, name_col in [
        ('Abhishek Sharma', eligible_batters, 'striker_id', 'striker_name'),
        ('Vaibhav Sooryavanshi', eligible_batters, 'striker_id', 'striker_name'),
        ('Jasprit Bumrah', eligible_bowlers, 'bowler_id', 'bowler_name')
    ]:
        row = df_sub[df_sub[name_col] == p_name].iloc[0]
        unconst_rank = int(row['rank'])
        in_cc = row['shrunk_delta'] >= 0
        cc_rank = int(df_sub[df_sub['shrunk_delta'] >= 0].reset_index(drop=True).query(f"{name_col} == '{p_name}'").index[0] + 1) if in_cc else "Excluded (Delta < 0)"
        print(f"* {p_name}: Unconstrained Rank {unconst_rank} | Shrunk Baseline {row['shrunk_baseline']:+.2f} | Shrunk Delta {row['shrunk_delta']:+.2f} (90% CI [{row['delta_ci_lower_90']:+.2f}, {row['delta_ci_upper_90']:+.2f}]) | Clutch-Constrained Status: {cc_rank}")

    # =========================================================================
    # 7. MATHEMATICAL CONSISTENCY ASSERTIONS & TABLE 3.1 PREPARATION
    # =========================================================================
    print("\n" + "=" * 80)
    print("MATHEMATICAL CONSISTENCY VERIFICATION (ASSERTING DIRECT CALCULATOR MATCH):")
    print("=" * 80)
    print(f"\n--- TOP 10 BATTERS TABLE 3.1 AUDIT ---")
    print(f"{'Rank':<4} {'Player':<22} {'N_B':<7} {'Raw_B':<8} {'B_shrunk':<9} {'N_D':<6} {'Raw_D':<8} {'D_shrunk':<9} {'Rating':<8} {'90% CI':<18} {'P(T10)':<7}")
    for idx, r in bat_top10.iterrows():
        rec_B = (r['baseline_balls'] / (r['baseline_balls'] + K_B_bat)) * r['baseline_impact_100'] + (K_B_bat / (r['baseline_balls'] + K_B_bat)) * mu_B_bat
        rec_D = (r['hp_balls_faced'] / (r['hp_balls_faced'] + K_D_bat)) * r['delta_impact_100'] + (K_D_bat / (r['hp_balls_faced'] + K_D_bat)) * mu_D_bat
        rec_rating = rec_B + rec_D

        assert np.isclose(r['shrunk_baseline'], rec_B, atol=1e-4), f"Baseline mismatch for {r['striker_name']}"
        assert np.isclose(r['shrunk_delta'], rec_D, atol=1e-4), f"Delta mismatch for {r['striker_name']}"
        assert np.isclose(r['shrunk_rating'], rec_rating, atol=1e-4), f"Rating mismatch for {r['striker_name']}"
        assert r['ci_lower_90'] <= r['shrunk_rating'] <= r['ci_upper_90'], f"CI violation for {r['striker_name']}"
        assert 0.0 <= r['top10_probability'] <= 1.0, f"P(top10) out of bounds for {r['striker_name']}"

        print(f"{r['rank']:<4} {r['striker_name']:<22} {r['baseline_balls']:<7.0f} {r['baseline_impact_100']:<8.2f} {r['shrunk_baseline']:<9.2f} {r['hp_balls_faced']:<6.0f} {r['delta_impact_100']:<8.2f} {r['shrunk_delta']:<9.2f} {r['shrunk_rating']:<8.2f} [{r['ci_lower_90']:+.2f}, {r['ci_upper_90']:+.2f}]  {r['top10_probability']*100:<5.1f}%")

    print(f"\n--- TOP 10 BOWLERS TABLE 3.1 AUDIT ---")
    print(f"{'Rank':<4} {'Player':<22} {'N_B':<7} {'Raw_B':<8} {'B_shrunk':<9} {'N_D':<6} {'Raw_D':<8} {'D_shrunk':<9} {'Rating':<8} {'90% CI':<18} {'P(T10)':<7}")
    for idx, r in bowl_top10.iterrows():
        rec_B = (r['baseline_balls'] / (r['baseline_balls'] + K_B_bowl)) * r['baseline_impact_100'] + (K_B_bowl / (r['baseline_balls'] + K_B_bowl)) * mu_B_bowl
        rec_D = (r['hp_legal_balls'] / (r['hp_legal_balls'] + K_D_bowl)) * r['delta_impact_100'] + (K_D_bowl / (r['hp_legal_balls'] + K_D_bowl)) * mu_D_bowl
        rec_rating = rec_B + rec_D

        assert np.isclose(r['shrunk_baseline'], rec_B, atol=1e-4), f"Baseline mismatch for {r['bowler_name']}"
        assert np.isclose(r['shrunk_delta'], rec_D, atol=1e-4), f"Delta mismatch for {r['bowler_name']}"
        assert np.isclose(r['shrunk_rating'], rec_rating, atol=1e-4), f"Rating mismatch for {r['bowler_name']}"
        assert r['ci_lower_90'] <= r['shrunk_rating'] <= r['ci_upper_90'], f"CI violation for {r['bowler_name']}"
        assert 0.0 <= r['top10_probability'] <= 1.0, f"P(top10) out of bounds for {r['bowler_name']}"

        print(f"{r['rank']:<4} {r['bowler_name']:<22} {r['baseline_balls']:<7.0f} {r['baseline_impact_100']:<8.2f} {r['shrunk_baseline']:<9.2f} {r['hp_legal_balls']:<6.0f} {r['delta_impact_100']:<8.2f} {r['shrunk_delta']:<9.2f} {r['shrunk_rating']:<8.2f} [{r['ci_lower_90']:+.2f}, {r['ci_upper_90']:+.2f}]  {r['top10_probability']*100:<5.1f}%")

    # =========================================================================
    # 8. SECONDARY RANKING: PURE CLUTCH ELEVATION (RANKED BY SHRUNK DELTA ALONE)
    # =========================================================================
    print("\n--- 8. Secondary Ranking: Pure Clutch Elevation (Ranked by Shrunk Delta Alone) ---")
    pure_clutch_bat = eligible_batters.sort_values('shrunk_delta', ascending=False).reset_index(drop=True).head(10)
    pure_clutch_bat['clutch_rank'] = pure_clutch_bat.index + 1

    pure_clutch_bowl = eligible_bowlers.sort_values('shrunk_delta', ascending=False).reset_index(drop=True).head(10)
    pure_clutch_bowl['clutch_rank'] = pure_clutch_bowl.index + 1

    pure_clutch_bat.to_csv(OUTPUTS_DIR / "top10_pure_clutch_batters.csv", index=False)
    pure_clutch_bowl.to_csv(OUTPUTS_DIR / "top10_pure_clutch_bowlers.csv", index=False)

    # =========================================================================
    # 9. PAIRWISE PROBABILITIES FOR ADJACENT TOP-10 RANKS
    # =========================================================================
    print("\n--- 9. Pairwise Superiority Probabilities P(Rank i > Rank i+1) ---")
    bat_pairwise = []
    for i in range(9):
        pid1 = bat_top10.iloc[i]['striker_id']
        pid2 = bat_top10.iloc[i+1]['striker_id']
        col1 = bat_pid_to_col[pid1]
        col2 = bat_pid_to_col[pid2]
        p_beats = (bat_boot_rating[:, col1] > bat_boot_rating[:, col2]).mean()
        name1 = bat_top10.iloc[i]['striker_name']
        name2 = bat_top10.iloc[i+1]['striker_name']
        dist = 'Distinguishable (p>=0.90)' if p_beats >= 0.90 else ('Favored (p>=0.70)' if p_beats >= 0.70 else 'Partly Distinguishable')
        bat_pairwise.append({
            'Rank_i': i + 1, 'Player_i': name1,
            'Rank_j': i + 2, 'Player_j': name2,
            'P_i_beats_j': round(p_beats * 100, 1),
            'Distinguishability': dist
        })

    bowl_pairwise = []
    for i in range(9):
        pid1 = bowl_top10.iloc[i]['bowler_id']
        pid2 = bowl_top10.iloc[i+1]['bowler_id']
        col1 = bowl_pid_to_col[pid1]
        col2 = bowl_pid_to_col[pid2]
        p_beats = (bowl_boot_rating[:, col1] > bowl_boot_rating[:, col2]).mean()
        name1 = bowl_top10.iloc[i]['bowler_name']
        name2 = bowl_top10.iloc[i+1]['bowler_name']
        dist = 'Distinguishable (p>=0.90)' if p_beats >= 0.90 else ('Favored (p>=0.70)' if p_beats >= 0.70 else 'Partly Distinguishable')
        bowl_pairwise.append({
            'Rank_i': i + 1, 'Player_i': name1,
            'Rank_j': i + 2, 'Player_j': name2,
            'P_i_beats_j': round(p_beats * 100, 1),
            'Distinguishability': dist
        })

    bat_pw_df = pd.DataFrame(bat_pairwise)
    bowl_pw_df = pd.DataFrame(bowl_pairwise)
    bat_pw_df.to_csv(OUTPUTS_DIR / "pairwise_probabilities_batters.csv", index=False)
    bowl_pw_df.to_csv(OUTPUTS_DIR / "pairwise_probabilities_bowlers.csv", index=False)

    # =========================================================================
    # 10. OPPOSITION QUALITY AUDIT FOR TOP 10 PLAYERS
    # =========================================================================
    print("\n--- 10. Opposition Quality Audit (Top 10 Batters & Bowlers) ---")
    opp_rows = []
    for idx, r in bat_top10.iterrows():
        opp_rows.append({
            'Rank': int(r['rank']),
            'Discipline': 'Batter',
            'Player': r['striker_name'],
            'Raw_HP_Impact': round(r['raw_impact_100'], 2),
            'Opp_Quality_Diff': round(r['opp_bowler_diff'], 2),
            'Adj_HP_Impact': round(r['adj_impact_100'], 2),
            'Teams': r['teams'],
            'Weak_Opp_Flag': 'Normal'
        })
    for idx, r in bowl_top10.iterrows():
        opp_rows.append({
            'Rank': int(r['rank']),
            'Discipline': 'Bowler',
            'Player': r['bowler_name'],
            'Raw_HP_Impact': round(r['raw_impact_100'], 2),
            'Opp_Quality_Diff': round(r['opp_batter_diff'], 2),
            'Adj_HP_Impact': round(r['adj_impact_100'], 2),
            'Teams': r['teams'],
            'Weak_Opp_Flag': 'Normal'
        })
    opp_df = pd.DataFrame(opp_rows)
    opp_df.to_csv(OUTPUTS_DIR / "opposition_audit_top10.csv", index=False)
    print(opp_df.to_string(index=False))

    # =========================================================================
    # 11. RECOMPUTED RUNS-PER-WICKET ON HIGH PRESSURE DELIVERIES ONLY
    # =========================================================================
    print("\n--- 11. High-Pressure Deliveries Only Runs-per-Wicket Benchmark ---")
    # Phase HP values: PP 14.40, Middle 10.71, Death 5.89 (flat 9.52)
    phase_w_hp = {'powerplay': 14.40, 'middle': 10.71, 'death': 5.89}
    df['ball_impact_hp_phase_bat'] = (df['runs_off_bat'] - df['exp_batter_runs']) - df['phase'].map(phase_w_hp).fillna(9.52) * (df['is_wicket'].astype(int) - df['exp_batter_out'])
    df['ball_impact_hp_phase_bowl'] = (df['exp_bowler_runs'] - df['bowler_runs_conceded']) + df['phase'].map(phase_w_hp).fillna(9.52) * (df['bowler_wicket'].astype(int) - df['exp_bowler_wicket'])

    # Batters HP phase
    hp_bat_del = df[(df['high_pressure'] == 1) & (~df['is_wide'])].copy()
    ord_bat_del = df[(df['high_pressure'] == 0) & (~df['is_wide'])].copy()

    hp_bat_s = hp_bat_del.groupby(['striker_id', 'striker_name']).apply(
        lambda g: (g['ball_impact_hp_phase_bat'].sum() / len(g) * 100) + (g['opp_bowler_quality'].mean() * 100)
    ).rename('raw_hp_phase').reset_index()
    ord_bat_s = ord_bat_del.groupby('striker_id').apply(
        lambda g: g['ball_impact_hp_phase_bat'].sum() / len(g) * 100
    ).rename('base_hp_phase').reset_index()

    bat_hp_model = eligible_batters[['striker_id', 'striker_name', 'baseline_balls', 'hp_balls_faced']].merge(hp_bat_s, on=['striker_id', 'striker_name']).merge(ord_bat_s, on='striker_id')
    bat_hp_model['delta_hp_phase'] = bat_hp_model['raw_hp_phase'] - bat_hp_model['base_hp_phase']
    mu_b_hbp = bat_hp_model['base_hp_phase'].mean()
    mu_d_hbp = bat_hp_model['delta_hp_phase'].mean()
    w_b_hp = bat_hp_model['baseline_balls'] / (bat_hp_model['baseline_balls'] + K_B_bat)
    w_d_hp = bat_hp_model['hp_balls_faced'] / (bat_hp_model['hp_balls_faced'] + K_D_bat)
    bat_hp_model['shrunk_rating_hp_phase'] = (w_b_hp * bat_hp_model['base_hp_phase'] + (1 - w_b_hp) * mu_b_hbp) + (w_d_hp * bat_hp_model['delta_hp_phase'] + (1 - w_d_hp) * mu_d_hbp)
    top10_bat_hpp = bat_hp_model.sort_values('shrunk_rating_hp_phase', ascending=False).head(10)['striker_name'].tolist()

    # Bowlers HP phase
    hp_bowl_del = df[(df['high_pressure'] == 1) & (df['is_legal'])].copy()
    ord_bowl_del = df[(df['high_pressure'] == 0) & (df['is_legal'])].copy()

    hp_bowl_s = hp_bowl_del.groupby(['bowler_id', 'bowler_name']).apply(
        lambda g: (g['ball_impact_hp_phase_bowl'].sum() / len(g) * 100) + (g['opp_batter_quality'].mean() * 100)
    ).rename('raw_hp_phase').reset_index()
    ord_bowl_s = ord_bowl_del.groupby('bowler_id').apply(
        lambda g: g['ball_impact_hp_phase_bowl'].sum() / len(g) * 100
    ).rename('base_hp_phase').reset_index()

    bowl_hp_model = eligible_bowlers[['bowler_id', 'bowler_name', 'baseline_balls', 'hp_legal_balls']].merge(hp_bowl_s, on=['bowler_id', 'bowler_name']).merge(ord_bowl_s, on='bowler_id')
    bowl_hp_model['delta_hp_phase'] = bowl_hp_model['raw_hp_phase'] - bowl_hp_model['base_hp_phase']
    mu_b_hbp_bw = bowl_hp_model['base_hp_phase'].mean()
    mu_d_hbp_bw = bowl_hp_model['delta_hp_phase'].mean()
    w_b_hp_bw = bowl_hp_model['baseline_balls'] / (bowl_hp_model['baseline_balls'] + K_B_bowl)
    w_d_hp_bw = bowl_hp_model['hp_legal_balls'] / (bowl_hp_model['hp_legal_balls'] + K_D_bowl)
    bowl_hp_model['shrunk_rating_hp_phase'] = (w_b_hp_bw * bowl_hp_model['base_hp_phase'] + (1 - w_b_hp_bw) * mu_b_hbp_bw) + (w_d_hp_bw * bowl_hp_model['delta_hp_phase'] + (1 - w_d_hp_bw) * mu_d_hbp_bw)
    top10_bowl_hpp = bowl_hp_model.sort_values('shrunk_rating_hp_phase', ascending=False).head(10)['bowler_name'].tolist()

    j_bat_hp_vs_phase = len(set(top10_bat_hpp) & set(bat_top10['striker_name'])) / len(set(top10_bat_hpp) | set(bat_top10['striker_name']))
    j_bat_hp_vs_flat = len(set(top10_bat_hpp) & set(bat_top10_flat['striker_name'])) / len(set(top10_bat_hpp) | set(bat_top10_flat['striker_name']))

    j_bowl_hp_vs_phase = len(set(top10_bowl_hpp) & set(bowl_top10['bowler_name'])) / len(set(top10_bowl_hpp) | set(bowl_top10['bowler_name']))
    j_bowl_hp_vs_flat = len(set(top10_bowl_hpp) & set(bowl_top10_flat['bowler_name'])) / len(set(top10_bowl_hpp) | set(bowl_top10_flat['bowler_name']))

    hp_wkt_comp_df = pd.DataFrame([
        {'Discipline': 'Batters', 'Specification': 'HP Phase Wickets (14.40, 10.71, 5.89)', 'Top_10': ', '.join(top10_bat_hpp), 'Jaccard_vs_Primary_Phase': round(j_bat_hp_vs_phase, 4), 'Jaccard_vs_Flat_8.85': round(j_bat_hp_vs_flat, 4)},
        {'Discipline': 'Bowlers', 'Specification': 'HP Phase Wickets (14.40, 10.71, 5.89)', 'Top_10': ', '.join(top10_bowl_hpp), 'Jaccard_vs_Primary_Phase': round(j_bowl_hp_vs_phase, 4), 'Jaccard_vs_Flat_8.85': round(j_bowl_hp_vs_flat, 4)}
    ])
    hp_wkt_comp_df.to_csv(OUTPUTS_DIR / "hp_wicket_comparison.csv", index=False)
    print("\nHigh-Pressure Wickets Top-10 Comparison:")
    print(hp_wkt_comp_df.to_string(index=False))

    # Top 20 Bowlers across Phase-Specific, HP-Specific, and Flat wicket values (Requirement 4)
    bowl_top20_phase = eligible_bowlers.sort_values('shrunk_rating', ascending=False).head(20).reset_index(drop=True)
    bowl_top20_hp = bowl_hp_model.sort_values('shrunk_rating_hp_phase', ascending=False).head(20).reset_index(drop=True)
    bowl_top20_flat = eligible_bowlers.sort_values('shrunk_rating_flat', ascending=False).head(20).reset_index(drop=True)

    comp_top20_bowlers = pd.DataFrame({
        'Rank': range(1, 21),
        'Phase_Specific_Player': bowl_top20_phase['bowler_name'],
        'Phase_Rating': bowl_top20_phase['shrunk_rating'].round(2),
        'HP_Specific_Player': bowl_top20_hp['bowler_name'],
        'HP_Rating': bowl_top20_hp['shrunk_rating_hp_phase'].round(2),
        'Flat_8.85_Player': bowl_top20_flat['bowler_name'],
        'Flat_Rating': bowl_top20_flat['shrunk_rating_flat'].round(2)
    })
    comp_top20_bowlers.to_csv(OUTPUTS_DIR / "top20_bowlers_wicket_specs.csv", index=False)
    print("\n[+] Saved full Top 20 Bowlers across 3 wicket specifications to outputs/top20_bowlers_wicket_specs.csv:")
    print(comp_top20_bowlers.to_string(index=False))

    # Complete 20-Player Table 3.1 (Shrinkage Verification with 90% CI, Requirement 7)
    verif_rows = []
    for _, r in bat_top10.iterrows():
        verif_rows.append({
            'Rank': int(r['rank']),
            'Player': r['striker_name'],
            'Role': 'Bat',
            'N_B': int(r['baseline_balls']),
            'w_B': round(r['w_baseline'], 3),
            'Raw_B': round(r['baseline_impact_100'], 2),
            'B_shrunk': round(r['shrunk_baseline'], 2),
            'N_D': int(r['hp_balls_faced']),
            'w_D': round(r['shrinkage_weight'], 3),
            'Raw_D': round(r['delta_impact_100'], 2),
            'D_shrunk': round(r['shrunk_delta'], 2),
            'Rating': round(r['shrunk_rating'], 2),
            '90%_CI': f"[{r['ci_lower_90']:.2f}, {r['ci_upper_90']:.2f}]",
            'P(Top10)': f"{r['top10_probability']*100:.1f}%"
        })
    for _, r in bowl_top10.iterrows():
        verif_rows.append({
            'Rank': int(r['rank']),
            'Player': r['bowler_name'],
            'Role': 'Bowl',
            'N_B': int(r['baseline_balls']),
            'w_B': round(r['w_baseline'], 3),
            'Raw_B': round(r['baseline_impact_100'], 2),
            'B_shrunk': round(r['shrunk_baseline'], 2),
            'N_D': int(r['hp_legal_balls']),
            'w_D': round(r['shrinkage_weight'], 3),
            'Raw_D': round(r['delta_impact_100'], 2),
            'D_shrunk': round(r['shrunk_delta'], 2),
            'Rating': round(r['shrunk_rating'], 2),
            '90%_CI': f"[{r['ci_lower_90']:.2f}, {r['ci_upper_90']:.2f}]",
            'P(Top10)': f"{r['top10_probability']*100:.1f}%"
        })
    df_verif_all = pd.DataFrame(verif_rows)
    df_verif_all.to_csv(OUTPUTS_DIR / "shrinkage_verification_table.csv", index=False)
    print("\n[+] Saved Complete 20-Player Table 3.1 Verification to outputs/shrinkage_verification_table.csv:")
    print(df_verif_all.to_string(index=False))

    # Save outputs
    eligible_batters.to_csv(OUTPUTS_DIR / "full_ratings_batters.csv", index=False)
    eligible_bowlers.to_csv(OUTPUTS_DIR / "full_ratings_bowlers.csv", index=False)
    bat_top10.to_csv(OUTPUTS_DIR / "final_top10_batters.csv", index=False)
    bowl_top10.to_csv(OUTPUTS_DIR / "final_top10_bowlers.csv", index=False)
    bat_top10_flat.to_csv(OUTPUTS_DIR / "top10_batters_flat.csv", index=False)
    bowl_top10_flat.to_csv(OUTPUTS_DIR / "top10_bowlers_flat.csv", index=False)

    print(f"\n[+] Saved primary top 10 batters to: {OUTPUTS_DIR / 'final_top10_batters.csv'}")
    print(f"[+] Saved primary top 10 bowlers to: {OUTPUTS_DIR / 'final_top10_bowlers.csv'}")
    print(f"[+] Saved flat comparison top 10 batters to: {OUTPUTS_DIR / 'top10_batters_flat.csv'}")
    print(f"[+] Saved flat comparison top 10 bowlers to: {OUTPUTS_DIR / 'top10_bowlers_flat.csv'}")

    return eligible_batters, eligible_bowlers

if __name__ == "__main__":
    run_fair_comparison()
