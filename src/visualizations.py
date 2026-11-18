"""
Stage 7 (Revised): Publication-Quality Visualizations Engine
Generates:
1. Rating vs Sample Size Funnel Plot (demonstrating Empirical Bayes Shrinkage)
2. Top 10 Batters & Bowlers Forest Plot with 90% Match-Grouped Bootstrap Credible Intervals AND 95% Null Permutation Band
3. Rank Stability & Sensitivity Heatmap
4. Baseline vs High-Pressure Scatter Plot (Clutch Elevation vs Choke)
"""
import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.append(str(Path(__file__).resolve().parent.parent))
from src.config import OUTPUTS_DIR

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#333333'
plt.rcParams['axes.linewidth'] = 0.8

def generate_visualizations():
    print("=" * 80)
    print("GENERATING REVISED PUBLICATION-QUALITY CHARTS")
    print("=" * 80)

    batters = pd.read_csv(OUTPUTS_DIR / "full_ratings_batters.csv")
    bowlers = pd.read_csv(OUTPUTS_DIR / "full_ratings_bowlers.csv")
    top_bat = pd.read_csv(OUTPUTS_DIR / "final_top10_batters.csv")
    top_bowl = pd.read_csv(OUTPUTS_DIR / "final_top10_bowlers.csv")
    null_bands = pd.read_csv(OUTPUTS_DIR / "null_top10_bands.csv")

    # 1. Funnel Plot
    print("Generating Rating vs Sample Size Funnel Plots...")
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    # Batters Funnel
    axes[0].scatter(batters['hp_balls_faced'], batters['adj_impact_100'], color='#6C757D', alpha=0.45, label='Raw Adj. Impact', s=35)
    axes[0].scatter(batters['hp_balls_faced'], batters['shrunk_rating'], color='#E21A5C', alpha=0.85, label='Hierarchical Shrunk Rating', s=45)
    top10_b = batters.head(10)
    axes[0].scatter(top10_b['hp_balls_faced'], top10_b['shrunk_rating'], color='#FFD700', edgecolors='#000', s=90, label='Top 10 Batters', zorder=5)
    for _, r in top10_b.head(5).iterrows():
        axes[0].annotate(r['striker_name'].split()[-1], (r['hp_balls_faced'], r['shrunk_rating']), textcoords="offset points", xytext=(5, 5), fontsize=9, fontweight='bold')
    
    axes[0].axhline(batters['shrunk_rating'].mean(), color='blue', linestyle='--', alpha=0.7, label=f"Population Mean ({batters['shrunk_rating'].mean():.1f})")
    axes[0].set_title("Batters: High-Pressure Impact vs Sample Size (Shrinkage Funnel)", fontsize=12, fontweight='bold', pad=12)
    axes[0].set_xlabel("High-Pressure Balls Faced", fontsize=11)
    axes[0].set_ylabel("Rating (Runs Added / 100 Balls)", fontsize=11)
    axes[0].legend(loc='lower right', frameon=True)

    # Bowlers Funnel
    axes[1].scatter(bowlers['hp_legal_balls'], bowlers['adj_impact_100'], color='#6C757D', alpha=0.45, label='Raw Adj. Impact', s=35)
    axes[1].scatter(bowlers['hp_legal_balls'], bowlers['shrunk_rating'], color='#004B87', alpha=0.85, label='Hierarchical Shrunk Rating', s=45)
    top10_bw = bowlers.head(10)
    axes[1].scatter(top10_bw['hp_legal_balls'], top10_bw['shrunk_rating'], color='#FFD700', edgecolors='#000', s=90, label='Top 10 Bowlers', zorder=5)
    for _, r in top10_bw.head(5).iterrows():
        axes[1].annotate(r['bowler_name'].split()[-1], (r['hp_legal_balls'], r['shrunk_rating']), textcoords="offset points", xytext=(5, 5), fontsize=9, fontweight='bold')
    
    axes[1].axhline(bowlers['shrunk_rating'].mean(), color='blue', linestyle='--', alpha=0.7, label=f"Population Mean ({bowlers['shrunk_rating'].mean():.1f})")
    axes[1].set_title("Bowlers: High-Pressure Impact vs Sample Size (Shrinkage Funnel)", fontsize=12, fontweight='bold', pad=12)
    axes[1].set_xlabel("High-Pressure Legal Deliveries Bowled", fontsize=11)
    axes[1].set_ylabel("Rating (Runs Saved / 100 Balls)", fontsize=11)
    axes[1].legend(loc='lower right', frameon=True)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    funnel_path = OUTPUTS_DIR / "rating_vs_samplesize_funnel.png"
    plt.savefig(funnel_path, dpi=300)
    plt.close()
    print(f"[+] Saved funnel plot to: {funnel_path}")

    # 2. Top 10 Batters Forest Plot with Null Distribution Band
    print("Generating Top 10 Forest Plots with Null Distribution Band...")
    fig, ax = plt.subplots(figsize=(11.5, 6.8))
    top_b_rev = top_bat.iloc[::-1].reset_index(drop=True)
    null_b_rev = null_bands.iloc[::-1].reset_index(drop=True)
    y_pos = np.arange(len(top_b_rev))

    # Plot 95% null band
    null_width_b = null_b_rev['Batter_Null_Upper_95'] - null_b_rev['Batter_Null_Lower_95']
    ax.barh(y_pos, width=null_width_b, left=null_b_rev['Batter_Null_Lower_95'], height=0.45, color='#E5E5E5', edgecolor='#B0B0B0', linestyle=':', label='95% Null Permutation Band (Chance Expectation)')
    ax.scatter(null_b_rev['Batter_Null_Median'], y_pos, marker='|', color='#777777', s=120, label='Null Permutation Median', zorder=3)

    x_err = [
        np.maximum(0, top_b_rev['shrunk_rating'] - top_b_rev['ci_lower_90']),
        np.maximum(0, top_b_rev['ci_upper_90'] - top_b_rev['shrunk_rating'])
    ]
    ax.errorbar(top_b_rev['shrunk_rating'], y_pos, xerr=x_err, fmt='o', color='#E21A5C', ecolor='#222222', elinewidth=2.2, capsize=5, capthick=1.5, markersize=8, label='Posterior Rating (90% Credible Interval)', zorder=4)
    ax.set_yticks(y_pos)
    labels = [f"#{row['rank']} {row['striker_name']} ({str(row['teams']).split(',')[0]}) [{row['delta_label'].upper()}]" for _, row in top_b_rev.iterrows()]
    ax.set_yticklabels(labels, fontsize=10, fontweight='bold')
    ax.set_xlabel("High-Pressure Batting Rating (Runs Added / 100 Balls)", fontsize=11, fontweight='bold')
    ax.set_title("Top 10 Batters Under Pressure: Posterior 90% CIs vs 95% Within-Match Null Band", fontsize=12, fontweight='bold', pad=14)
    ax.set_xlim(left=0, right=max(top_b_rev['ci_upper_90']) + 8.0)
    ax.grid(axis='x', linestyle='--', alpha=0.5)

    for i, (_, row) in enumerate(top_b_rev.iterrows()):
        ax.text(row['ci_upper_90'] + 0.45, i, f"{row['shrunk_rating']:.2f} (P(T10): {row['top10_probability']*100:.0f}%)", va='center', fontsize=9, fontweight='bold')

    ax.legend(loc='lower right', frameon=True, fontsize=9)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    forest_bat_path = OUTPUTS_DIR / "top10_batters_intervals.png"
    plt.savefig(forest_bat_path, dpi=300)
    plt.close()
    print(f"[+] Saved batters forest plot to: {forest_bat_path}")

    # 3. Top 10 Bowlers Forest Plot with Null Distribution Band
    fig, ax = plt.subplots(figsize=(11.5, 6.8))
    top_bw_rev = top_bowl.iloc[::-1].reset_index(drop=True)
    null_bw_rev = null_bands.iloc[::-1].reset_index(drop=True)
    y_pos = np.arange(len(top_bw_rev))

    null_width_bw = null_bw_rev['Bowler_Null_Upper_95'] - null_bw_rev['Bowler_Null_Lower_95']
    ax.barh(y_pos, width=null_width_bw, left=null_bw_rev['Bowler_Null_Lower_95'], height=0.45, color='#E5E5E5', edgecolor='#B0B0B0', linestyle=':', label='95% Null Permutation Band (Chance Expectation)')
    ax.scatter(null_bw_rev['Bowler_Null_Median'], y_pos, marker='|', color='#777777', s=120, label='Null Permutation Median', zorder=3)

    x_err_bw = [
        np.maximum(0, top_bw_rev['shrunk_rating'] - top_bw_rev['ci_lower_90']),
        np.maximum(0, top_bw_rev['ci_upper_90'] - top_bw_rev['shrunk_rating'])
    ]
    ax.errorbar(top_bw_rev['shrunk_rating'], y_pos, xerr=x_err_bw, fmt='s', color='#004B87', ecolor='#222222', elinewidth=2.2, capsize=5, capthick=1.5, markersize=8, label='Posterior Rating (90% Credible Interval)', zorder=4)
    ax.set_yticks(y_pos)
    labels_bw = [f"#{row['rank']} {row['bowler_name']} ({str(row['teams']).split(',')[0]}) [{row['delta_label'].upper()}]" for _, row in top_bw_rev.iterrows()]
    ax.set_yticklabels(labels_bw, fontsize=10, fontweight='bold')
    ax.set_xlabel("High-Pressure Bowling Rating (Runs Saved / 100 Balls)", fontsize=11, fontweight='bold')
    ax.set_title("Top 10 Bowlers Under Pressure: Posterior 90% CIs vs 95% Within-Match Null Band", fontsize=12, fontweight='bold', pad=14)
    ax.set_xlim(left=0, right=max(top_bw_rev['ci_upper_90']) + 8.0)
    ax.grid(axis='x', linestyle='--', alpha=0.5)

    for i, (_, row) in enumerate(top_bw_rev.iterrows()):
        ax.text(row['ci_upper_90'] + 0.45, i, f"{row['shrunk_rating']:.2f} (P(T10): {row['top10_probability']*100:.0f}%)", va='center', fontsize=9, fontweight='bold')

    ax.legend(loc='lower right', frameon=True, fontsize=9)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    forest_bowl_path = OUTPUTS_DIR / "top10_bowlers_intervals.png"
    plt.savefig(forest_bowl_path, dpi=300)
    plt.close()
    print(f"[+] Saved bowlers forest plot to: {forest_bowl_path}")

    # 4. Baseline vs Pressure Scatter Plot
    print("Generating Baseline vs Pressure Scatter Plot...")
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    axes[0].scatter(batters['baseline_impact_100'], batters['adj_impact_100'], color='#6C757D', alpha=0.45, s=35)
    axes[0].scatter(top_bat['baseline_impact_100'], top_bat['adj_impact_100'], color='#E21A5C', s=80, edgecolors='black', label='Top 10 Batters')
    axes[0].plot([-30, 80], [-30, 80], linestyle='--', color='black', alpha=0.6, label='Equal Performance Line (y=x)')
    for _, r in top_bat.head(5).iterrows():
        axes[0].annotate(r['striker_name'].split()[-1], (r['baseline_impact_100'], r['adj_impact_100']), textcoords="offset points", xytext=(5, 5), fontsize=9, fontweight='bold')
    
    axes[0].set_title("Batters: Ordinary Baseline Impact vs High-Pressure Impact", fontsize=12, fontweight='bold', pad=12)
    axes[0].set_xlabel("Ordinary Baseline Impact (Runs / 100 Balls)", fontsize=11)
    axes[0].set_ylabel("High-Pressure Impact (Runs / 100 Balls)", fontsize=11)
    axes[0].legend(loc='lower right', frameon=True)
    axes[0].grid(True, alpha=0.3)

    axes[1].scatter(bowlers['baseline_impact_100'], bowlers['adj_impact_100'], color='#6C757D', alpha=0.45, s=35)
    axes[1].scatter(top_bowl['baseline_impact_100'], top_bowl['adj_impact_100'], color='#004B87', s=80, edgecolors='black', label='Top 10 Bowlers')
    axes[1].plot([-30, 80], [-30, 80], linestyle='--', color='black', alpha=0.6, label='Equal Performance Line (y=x)')
    for _, r in top_bowl.head(5).iterrows():
        axes[1].annotate(r['bowler_name'].split()[-1], (r['baseline_impact_100'], r['adj_impact_100']), textcoords="offset points", xytext=(5, 5), fontsize=9, fontweight='bold')
    
    axes[1].set_title("Bowlers: Ordinary Baseline Impact vs High-Pressure Impact", fontsize=12, fontweight='bold', pad=12)
    axes[1].set_xlabel("Ordinary Baseline Impact (Runs Saved / 100 Balls)", fontsize=11)
    axes[1].set_ylabel("High-Pressure Impact (Runs Saved / 100 Balls)", fontsize=11)
    axes[1].legend(loc='lower right', frameon=True)
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    scatter_path = OUTPUTS_DIR / "baseline_vs_pressure_scatter.png"
    plt.savefig(scatter_path, dpi=300)
    plt.close()
    print(f"[+] Saved baseline vs pressure scatter to: {scatter_path}")

    # 5. Rank Stability Heatmap
    sens = pd.read_csv(OUTPUTS_DIR / "sensitivity_analysis.csv")
    sens_pivot = sens.set_index('Specification')[['Batters_Jaccard', 'Bowlers_Jaccard']]

    fig, ax = plt.subplots(figsize=(9, 7.2))
    sns.heatmap(sens_pivot, annot=True, fmt=".2f", cmap="Blues", cbar_kws={'label': 'Top-10 Jaccard Similarity Index'}, annot_kws={'size': 11, 'weight': 'bold'}, ax=ax)
    ax.set_title("Rank Stability: Top 10 Overlap Across 14 Specifications", fontsize=12, fontweight='bold', pad=14)
    ax.set_ylabel("Model Specification", fontsize=10, fontweight='bold')
    ax.set_xlabel("Player Discipline", fontsize=10, fontweight='bold')
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    heatmap_rank_path = OUTPUTS_DIR / "rank_stability_heatmap.png"
    plt.savefig(heatmap_rank_path, dpi=300)
    plt.close()
    print(f"[+] Saved rank stability heatmap to: {heatmap_rank_path}")

    # 6. Expected Value Calibration by Decile and Phase
    print("Generating Expected Value Calibration by Decile and Phase...")
    df_exp = pd.read_csv(Path(__file__).resolve().parent.parent / "data" / "master_with_expected_values.csv", 
                         usecols=['runs_off_bat', 'exp_batter_runs', 'is_wicket', 'exp_batter_out', 
                                  'bowler_runs_conceded', 'exp_bowler_runs', 'bowler_wicket', 'exp_bowler_wicket', 
                                  'phase', 'is_legal', 'is_wide'])
    
    df_bat = df_exp[~df_exp['is_wide']].copy()
    df_bowl = df_exp[df_exp['is_legal']].copy()

    df_bat['r_decile'] = pd.qcut(df_bat['exp_batter_runs'], q=10, duplicates='drop')
    df_bat['w_decile'] = pd.qcut(df_bat['exp_batter_out'], q=10, duplicates='drop')

    r_cal = df_bat.groupby('r_decile', observed=False).agg(
        pred=('exp_batter_runs', 'mean'),
        actual=('runs_off_bat', 'mean')
    ).reset_index()

    w_cal = df_bat.groupby('w_decile', observed=False).agg(
        pred=('exp_batter_out', 'mean'),
        actual=('is_wicket', 'mean')
    ).reset_index()

    exp_phase = pd.read_csv(OUTPUTS_DIR / "expected_vs_actual_by_phase.csv")

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    # Panel 1: Runs by Decile
    axes[0].plot(r_cal['pred'], r_cal['actual'], 'o-', color='#E21A5C', linewidth=2, markersize=7, label='Observed vs Expected')
    r_min, r_max = min(r_cal['pred'].min(), r_cal['actual'].min()), max(r_cal['pred'].max(), r_cal['actual'].max())
    axes[0].plot([r_min, r_max], [r_min, r_max], '--', color='#555555', alpha=0.7, label='Perfect Calibration (y=x)')
    axes[0].set_title("Expected Runs (xR) Calibration by Decile", fontsize=11, fontweight='bold', pad=12)
    axes[0].set_xlabel("Mean Predicted Runs (xR)", fontsize=10)
    axes[0].set_ylabel("Mean Actual Runs Off Bat", fontsize=10)
    axes[0].legend(frameon=True, fontsize=9)
    axes[0].grid(True, alpha=0.3)

    # Panel 2: Wickets by Decile
    axes[1].plot(w_cal['pred'], w_cal['actual'], 's-', color='#004B87', linewidth=2, markersize=7, label='Observed vs Expected')
    w_min, w_max = min(w_cal['pred'].min(), w_cal['actual'].min()), max(w_cal['pred'].max(), w_cal['actual'].max())
    axes[1].plot([w_min, w_max], [w_min, w_max], '--', color='#555555', alpha=0.7, label='Perfect Calibration (y=x)')
    axes[1].set_title("Expected Wickets (xW) Calibration by Decile", fontsize=11, fontweight='bold', pad=12)
    axes[1].set_xlabel("Mean Predicted Out Probability (xW)", fontsize=10)
    axes[1].set_ylabel("Mean Actual Out Rate", fontsize=10)
    axes[1].legend(frameon=True, fontsize=9)
    axes[1].grid(True, alpha=0.3)

    # Panel 3: Actual vs Expected by Phase
    phases = exp_phase['phase'].str.capitalize().values
    x_ph = np.arange(len(phases))
    w_bar = 0.35
    axes[2].bar(x_ph - w_bar/2, exp_phase['runs_off_bat'], width=w_bar, color='#E21A5C', alpha=0.85, label='Actual Runs/Ball')
    axes[2].bar(x_ph + w_bar/2, exp_phase['exp_batter_runs'], width=w_bar, color='#004B87', alpha=0.85, label='Expected Runs/Ball')
    axes[2].set_xticks(x_ph)
    axes[2].set_xticklabels(phases, fontsize=10, fontweight='bold')
    axes[2].set_title("Expected vs Actual Runs by Phase", fontsize=11, fontweight='bold', pad=12)
    axes[2].set_xlabel("Match Phase", fontsize=10)
    axes[2].set_ylabel("Runs Per Delivery", fontsize=10)
    axes[2].legend(frameon=True, fontsize=9)
    axes[2].grid(True, alpha=0.3)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    cal_fig_path = OUTPUTS_DIR / "expected_value_calibration_deciles_phases.png"
    plt.savefig(cal_fig_path, dpi=300)
    plt.close()
    print(f"[+] Saved expected value calibration chart to: {cal_fig_path}")

if __name__ == "__main__":
    generate_visualizations()
