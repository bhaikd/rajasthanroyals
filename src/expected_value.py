"""
Stage 3: Context-Aware Expected-Value Models (Player-Agnostic Baselines)
Trains models for Expected Runs (xR) and Expected Wickets (xW) without player identity.
Uses GroupKFold cross-validation by match_id to guarantee out-of-fold unbiased predictions.
"""
import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.model_selection import GroupKFold
from sklearn.metrics import mean_squared_error, roc_auc_score, log_loss
import lightgbm as lgb

sys.path.append(str(Path(__file__).resolve().parent.parent))
from src.config import DATA_DIR, OUTPUTS_DIR, RANDOM_SEED

np.random.seed(RANDOM_SEED)

def train_expected_value_models():
    print("=" * 80)
    print("STAGE 3: TRAINING CONTEXT-AWARE EXPECTED-VALUE BASELINE MODELS")
    print("=" * 80)

    data_path = DATA_DIR / "master_with_pressure.csv"
    print(f"Loading data from {data_path}...")
    df = pd.read_csv(data_path, low_memory=False)

    # Calculate Bowler-Attributed Runs Conceded:
    # Wides and no-balls count against the bowler. Byes, leg-byes, penalties do not.
    # In df:
    # is_wide: total_runs count against bowler
    # is_noball: runs_off_bat + 1 (or total_runs) count against bowler
    # byes / legbyes: 0 runs against bowler
    # normal: runs_off_bat count against bowler
    def get_bowler_runs(row):
        xtype = str(row['extras_type_clean']).lower()
        if xtype in ['legbyes', 'byes', 'penalty']:
            return 0
        elif xtype in ['wide', 'overstep']:
            return row['total_runs']
        else:
            return row['runs_off_bat']

    df['bowler_runs_conceded'] = df.apply(get_bowler_runs, axis=1)

    # Encode categorical context features without using player identity
    df['comp_type_num'] = (df['comp_type'] == 'IPL').astype(int)
    phase_map = {'powerplay': 0, 'middle': 1, 'death': 2}
    df['phase_num'] = df['phase'].map(phase_map).fillna(1).astype(int)
    
    # Pace vs Spin context if available
    pace_spin_map = {'pace': 1, 'spin': 2}
    df['pace_spin_num'] = df['pace_or_spin'].fillna('unknown').str.lower().map(pace_spin_map).fillna(0).astype(int)

    feature_cols = [
        'innings', 'overid', 'over_ball_num', 'wickets_before', 'wickets_in_hand',
        'balls_remaining', 'current_run_rate', 'required_run_rate', 'phase_num',
        'comp_type_num', 'pace_spin_num', 'runs_last_18_balls', 'wickets_last_18_balls'
    ]

    # Fill NaN for required run rate (for Innings 1, required_run_rate is 0)
    X = df[feature_cols].copy()
    X['required_run_rate'] = X['required_run_rate'].fillna(0)
    X['runs_last_18_balls'] = X['runs_last_18_balls'].fillna(0)
    X['wickets_last_18_balls'] = X['wickets_last_18_balls'].fillna(0)

    groups = df['match_id']

    # 5-fold GroupKFold by match_id
    n_splits = 5
    gkf = GroupKFold(n_splits=n_splits)

    # Arrays to store Out-Of-Fold predictions
    oof_exp_batter_runs = np.zeros(len(df))
    oof_exp_bowler_runs = np.zeros(len(df))
    oof_exp_batter_out = np.zeros(len(df))
    oof_exp_bowler_wicket = np.zeros(len(df))

    # Regression parameters for expected runs
    reg_params = {
        'objective': 'regression',
        'metric': 'rmse',
        'boosting_type': 'gbdt',
        'n_estimators': 120,
        'learning_rate': 0.05,
        'num_leaves': 31,
        'random_state': RANDOM_SEED,
        'verbose': -1
    }

    # Classification parameters for expected wickets
    clf_params = {
        'objective': 'binary',
        'metric': 'binary_logloss',
        'boosting_type': 'gbdt',
        'n_estimators': 120,
        'learning_rate': 0.05,
        'num_leaves': 31,
        'random_state': RANDOM_SEED,
        'verbose': -1
    }

    print("\nTraining 4 out-of-fold context baseline models (5 Folds Grouped by Match)...")

    y_bat_runs = df['runs_off_bat'].values
    y_bowl_runs = df['bowler_runs_conceded'].values
    y_bat_out = df['is_wicket'].astype(int).values
    y_bowl_wkt = df['bowler_wicket'].astype(int).values

    for fold, (train_idx, val_idx) in enumerate(gkf.split(X, groups=groups)):
        X_tr, X_va = X.iloc[train_idx], X.iloc[val_idx]
        
        # 1. Expected Batter Runs
        model_bat_runs = lgb.LGBMRegressor(**reg_params).fit(X_tr, y_bat_runs[train_idx])
        oof_exp_batter_runs[val_idx] = model_bat_runs.predict(X_va)

        # 2. Expected Bowler Runs
        model_bowl_runs = lgb.LGBMRegressor(**reg_params).fit(X_tr, y_bowl_runs[train_idx])
        oof_exp_bowler_runs[val_idx] = model_bowl_runs.predict(X_va)

        # 3. Expected Batter Out Probability
        model_bat_out = lgb.LGBMClassifier(**clf_params).fit(X_tr, y_bat_out[train_idx])
        oof_exp_batter_out[val_idx] = model_bat_out.predict_proba(X_va)[:, 1]

        # 4. Expected Bowler Wicket Probability
        model_bowl_wkt = lgb.LGBMClassifier(**clf_params).fit(X_tr, y_bowl_wkt[train_idx])
        oof_exp_bowler_wicket[val_idx] = model_bowl_wkt.predict_proba(X_va)[:, 1]

        print(f"Fold {fold+1}/{n_splits} complete.")

    # Assign OOF predictions to dataframe
    df['exp_batter_runs'] = np.clip(oof_exp_batter_runs, 0, 6)
    df['exp_bowler_runs'] = np.clip(oof_exp_bowler_runs, 0, 7)
    df['exp_batter_out'] = np.clip(oof_exp_batter_out, 0.001, 0.999)
    df['exp_bowler_wicket'] = np.clip(oof_exp_bowler_wicket, 0.001, 0.999)

    # Compute Delivery-Level Delta / Residuals:
    # For batters:
    # Runs Above Expected (RAE) = actual runs off bat - expected runs off bat
    # Outs Above Expected (OAE) = actual out (1/0) - expected out prob (lower is better for batter)
    df['batter_rae'] = df['runs_off_bat'] - df['exp_batter_runs']
    df['batter_oae'] = df['is_wicket'].astype(int) - df['exp_batter_out']

    # For bowlers:
    # Runs Saved vs Expected (RSE) = expected runs conceded - actual runs conceded (higher is better for bowler)
    # Wickets Above Expected (WAE) = actual bowler wicket (1/0) - expected bowler wicket prob (higher is better)
    df['bowler_rse'] = df['exp_bowler_runs'] - df['bowler_runs_conceded']
    df['bowler_wae'] = df['bowler_wicket'].astype(int) - df['exp_bowler_wicket']

    # League-wide calibration audit before recentering
    raw_calib = {
        'metric': ['batter_rae', 'batter_oae', 'bowler_rse', 'bowler_wae'],
        'league_mean_before': [
            float(df['batter_rae'].mean()),
            float(df['batter_oae'].mean()),
            float(df['bowler_rse'].mean()),
            float(df['bowler_wae'].mean())
        ]
    }

    # Exact recentering: ensure league-wide out-of-fold mean across all deliveries is identically 0.000000
    df['batter_rae'] = df['batter_rae'] - df['batter_rae'].mean()
    df['batter_oae'] = df['batter_oae'] - df['batter_oae'].mean()
    df['bowler_rse'] = df['bowler_rse'] - df['bowler_rse'].mean()
    df['bowler_wae'] = df['bowler_wae'] - df['bowler_wae'].mean()

    # Identify eligible players (>= 100 HP balls)
    bat_hp_counts = df[df['high_pressure'] == 1].groupby('striker_id').size()
    el_bat_ids = bat_hp_counts[bat_hp_counts >= 100].index
    el_bat_mask = df['striker_id'].isin(el_bat_ids)

    bowl_hp_counts = df[df['high_pressure'] == 1].groupby('bowler_id').size()
    el_bowl_ids = bowl_hp_counts[bowl_hp_counts >= 100].index
    el_bowl_mask = df['bowler_id'].isin(el_bowl_ids)

    calib_df = pd.DataFrame({
        'metric': ['batter_rae (runs/ball)', 'batter_oae (outs/ball)', 'bowler_rse (runs saved/ball)', 'bowler_wae (wkts/ball)'],
        'league_all_deliveries_mean': [
            float(df['batter_rae'].mean()),
            float(df['batter_oae'].mean()),
            float(df['bowler_rse'].mean()),
            float(df['bowler_wae'].mean())
        ],
        'eligible_players_mean': [
            float(df.loc[el_bat_mask, 'batter_rae'].mean()),
            float(df.loc[el_bat_mask, 'batter_oae'].mean()),
            float(df.loc[el_bowl_mask, 'bowler_rse'].mean()),
            float(df.loc[el_bowl_mask, 'bowler_wae'].mean())
        ]
    })
    calib_df['eligible_per_100_balls'] = [
        calib_df.loc[0, 'eligible_players_mean'] * 100,
        calib_df.loc[1, 'eligible_players_mean'] * 100,
        calib_df.loc[2, 'eligible_players_mean'] * 100,
        calib_df.loc[3, 'eligible_players_mean'] * 100
    ]
    print("\n" + "=" * 80)
    print("CALIBRATION & RECENTERING AUDIT (LEAGUE-WIDE VS ELIGIBLE PLAYERS):")
    print(calib_df.to_string(index=False))
    print("=" * 80)
    calib_df.to_csv(OUTPUTS_DIR / "calibration_summary.csv", index=False)

    # Performance Evaluation of Expected-Value Baseline Models
    rmse_bat = mean_squared_error(df['runs_off_bat'], df['exp_batter_runs'])**0.5
    rmse_bowl = mean_squared_error(df['bowler_runs_conceded'], df['exp_bowler_runs'])**0.5
    auc_bat_out = roc_auc_score(df['is_wicket'], df['exp_batter_out'])
    auc_bowl_wkt = roc_auc_score(df['bowler_wicket'], df['exp_bowler_wicket'])

    print("\n" + "=" * 80)
    print("EXPECTED-VALUE BASELINE PERFORMANCE (OUT-OF-FOLD):")
    print(f"Batter Runs RMSE: {rmse_bat:.4f} (Mean Actual: {df['runs_off_bat'].mean():.2f})")
    print(f"Bowler Runs RMSE: {rmse_bowl:.4f} (Mean Actual: {df['bowler_runs_conceded'].mean():.2f})")
    print(f"Batter Out ROC-AUC: {auc_bat_out:.4f} (Base Out Rate: {df['is_wicket'].mean()*100:.2f}%)")
    print(f"Bowler Wicket ROC-AUC: {auc_bowl_wkt:.4f} (Base Wicket Rate: {df['bowler_wicket'].mean()*100:.2f}%)")
    print("=" * 80)

    # Save summary of expected values by phase to verify sanity
    phase_summary = df.groupby('phase')[['runs_off_bat', 'exp_batter_runs', 'bowler_runs_conceded', 'exp_bowler_runs', 'is_wicket', 'exp_batter_out', 'bowler_wicket', 'exp_bowler_wicket']].mean()
    print("\nPhase-Level Expected vs Actual Sanity Table:")
    print(phase_summary.round(3))
    phase_summary.to_csv(OUTPUTS_DIR / "expected_vs_actual_by_phase.csv")

    # Save master with expected values
    output_master_exp = DATA_DIR / "master_with_expected_values.csv"
    df.to_csv(output_master_exp, index=False)
    print(f"\n[+] Successfully saved master dataset with expected values to {output_master_exp}")

    return df

if __name__ == "__main__":
    train_expected_value_models()
