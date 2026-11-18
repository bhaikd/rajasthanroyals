"""
Generates clean, publication-grade figures for the Methodology Report PDF:
1. Three separate calibration charts (xR deciles, xW deciles, Runs by Phase) and composite 1-row.
2. Full-width, high-resolution Top 10 Batters and Bowlers Forest Plots with null bands and aligned right-hand columns.
"""
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

OUTPUTS_DIR = Path(__file__).resolve().parent.parent / "outputs"

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Helvetica' if 'Helvetica' in plt.rcParams['font.sans-serif'] else 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#CCCCCC'
plt.rcParams['axes.linewidth'] = 0.8

def generate_clean_charts():
    print("Generating clean, high-resolution charts for PDF report...")

    # =========================================================================
    # 1. CALIBRATION CHARTS (from decile and phase CSVs)
    # =========================================================================
    dec_df = pd.read_csv(OUTPUTS_DIR / "decile_calibration_xR_xW.csv")
    phase_df = pd.read_csv(OUTPUTS_DIR / "expected_vs_actual_by_phase.csv")

    # Order phases: Powerplay, Middle, Death
    phase_order = {'powerplay': 0, 'middle': 1, 'death': 2}
    phase_df['order'] = phase_df['phase'].str.lower().map(phase_order)
    phase_df = phase_df.sort_values('order').reset_index(drop=True)

    # 1A. xR Decile Calibration
    fig, ax = plt.subplots(figsize=(3.4, 2.5), dpi=300)
    ax.plot([0.85, 1.95], [0.85, 1.95], '--', color='#777777', linewidth=1.2, label='Ideal (y = x)')
    ax.plot(dec_df['xR_Pred'], dec_df['Actual_Runs'], 'o-', color='#E21A5C', linewidth=1.8, markersize=5.5, label='Actual vs Pred')
    ax.set_title("Expected Runs (xR) Deciles", fontsize=9, fontweight='bold', pad=7)
    ax.set_xlabel("Mean Predicted Runs (xR)", fontsize=8, labelpad=4)
    ax.set_ylabel("Actual Runs Off Bat", fontsize=8, labelpad=4)
    ax.tick_params(labelsize=7.5)
    ax.legend(frameon=True, fontsize=7, loc='upper left')
    ax.grid(True, alpha=0.35, linestyle=':')
    plt.tight_layout()
    fig.savefig(OUTPUTS_DIR / "cal_xr_deciles.png", dpi=300)
    plt.close(fig)

    # 1B. xW Decile Calibration
    fig, ax = plt.subplots(figsize=(3.4, 2.5), dpi=300)
    ax.plot([3.0, 11.5], [3.0, 11.5], '--', color='#777777', linewidth=1.2, label='Ideal (y = x)')
    ax.plot(dec_df['xW_Pred_Pct'], dec_df['Actual_Out_Pct'], 's-', color='#004B87', linewidth=1.8, markersize=5.5, label='Actual vs Pred')
    ax.set_title("Expected Wickets (xW) Deciles", fontsize=9, fontweight='bold', pad=7)
    ax.set_xlabel("Mean Predicted Out % (xW)", fontsize=8, labelpad=4)
    ax.set_ylabel("Actual Out Rate %", fontsize=8, labelpad=4)
    ax.tick_params(labelsize=7.5)
    ax.legend(frameon=True, fontsize=7, loc='upper left')
    ax.grid(True, alpha=0.35, linestyle=':')
    plt.tight_layout()
    fig.savefig(OUTPUTS_DIR / "cal_xw_deciles.png", dpi=300)
    plt.close(fig)

    # 1C. Phase Runs Comparison
    fig, ax = plt.subplots(figsize=(3.4, 2.5), dpi=300)
    x = np.arange(len(phase_df))
    w = 0.32
    ax.bar(x - w/2, phase_df['runs_off_bat'], width=w, color='#E21A5C', alpha=0.85, label='Actual Runs/Ball')
    ax.bar(x + w/2, phase_df['exp_batter_runs'], width=w, color='#004B87', alpha=0.85, label='Expected (xR)')
    ax.set_xticks(x)
    ax.set_xticklabels([p.capitalize() for p in phase_df['phase']], fontsize=8, fontweight='bold')
    ax.set_title("Runs by Match Phase", fontsize=9, fontweight='bold', pad=7)
    ax.set_xlabel("Phase", fontsize=8, labelpad=4)
    ax.set_ylabel("Runs Per Delivery", fontsize=8, labelpad=4)
    ax.set_ylim(0, 1.8)
    ax.tick_params(labelsize=7.5)
    ax.legend(frameon=True, fontsize=7, loc='upper left')
    ax.grid(True, alpha=0.35, linestyle=':')
    plt.tight_layout()
    fig.savefig(OUTPUTS_DIR / "cal_runs_phase.png", dpi=300)
    plt.close(fig)

    # Composite 3-panel calibration chart
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.0), dpi=300)
    # Panel 1: xR
    axes[0].plot([0.85, 1.95], [0.85, 1.95], '--', color='#777777', linewidth=1.2, label='Ideal (y = x)')
    axes[0].plot(dec_df['xR_Pred'], dec_df['Actual_Runs'], 'o-', color='#E21A5C', linewidth=1.8, markersize=5.5, label='Actual vs Pred')
    axes[0].set_title("Panel A: Expected Runs (xR) Deciles", fontsize=8.5, fontweight='bold', pad=6)
    axes[0].set_xlabel("Mean Predicted Runs (xR)", fontsize=8, labelpad=3)
    axes[0].set_ylabel("Actual Runs Off Bat", fontsize=8, labelpad=3)
    axes[0].tick_params(labelsize=7.5)
    axes[0].legend(frameon=True, fontsize=7, loc='upper left')
    axes[0].grid(True, alpha=0.35, linestyle=':')

    # Panel 2: xW
    axes[1].plot([3.0, 11.5], [3.0, 11.5], '--', color='#777777', linewidth=1.2, label='Ideal (y = x)')
    axes[1].plot(dec_df['xW_Pred_Pct'], dec_df['Actual_Out_Pct'], 's-', color='#004B87', linewidth=1.8, markersize=5.5, label='Actual vs Pred')
    axes[1].set_title("Panel B: Expected Wickets (xW) Deciles", fontsize=8.5, fontweight='bold', pad=6)
    axes[1].set_xlabel("Mean Predicted Out % (xW)", fontsize=8, labelpad=3)
    axes[1].set_ylabel("Actual Out Rate %", fontsize=8, labelpad=3)
    axes[1].tick_params(labelsize=7.5)
    axes[1].legend(frameon=True, fontsize=7, loc='upper left')
    axes[1].grid(True, alpha=0.35, linestyle=':')

    # Panel 3: Phase
    axes[2].bar(x - w/2, phase_df['runs_off_bat'], width=w, color='#E21A5C', alpha=0.85, label='Actual Runs/Ball')
    axes[2].bar(x + w/2, phase_df['exp_batter_runs'], width=w, color='#004B87', alpha=0.85, label='Expected (xR)')
    axes[2].set_xticks(x)
    axes[2].set_xticklabels([p.capitalize() for p in phase_df['phase']], fontsize=8, fontweight='bold')
    axes[2].set_title("Panel C: Runs by Match Phase", fontsize=8.5, fontweight='bold', pad=6)
    axes[2].set_xlabel("Phase", fontsize=8, labelpad=3)
    axes[2].set_ylabel("Runs Per Delivery", fontsize=8, labelpad=3)
    axes[2].set_ylim(0, 1.8)
    axes[2].tick_params(labelsize=7.5)
    axes[2].legend(frameon=True, fontsize=7, loc='upper left')
    axes[2].grid(True, alpha=0.35, linestyle=':')

    plt.tight_layout()
    fig.savefig(OUTPUTS_DIR / "expected_value_calibration_deciles_phases.png", dpi=300)
    plt.close(fig)
    print("  [+] Saved calibration charts.")

    # =========================================================================
    # 2. FULL-WIDTH FOREST PLOTS (Batters & Bowlers)
    # =========================================================================
    top_bat = pd.read_csv(OUTPUTS_DIR / "final_top10_batters.csv")
    top_bowl = pd.read_csv(OUTPUTS_DIR / "final_top10_bowlers.csv")
    null_bands = pd.read_csv(OUTPUTS_DIR / "null_top10_bands.csv")

    # 2A. Batters Forest Plot
    top_b_rev = top_bat.iloc[::-1].reset_index(drop=True)
    null_b_rev = null_bands.iloc[::-1].reset_index(drop=True)
    y_pos = np.arange(len(top_b_rev))

    fig, ax = plt.subplots(figsize=(8.5, 3.2), dpi=300)
    null_width_b = null_b_rev['Batter_Null_Upper_95'] - null_b_rev['Batter_Null_Lower_95']
    ax.barh(y_pos, width=null_width_b, left=null_b_rev['Batter_Null_Lower_95'], height=0.45,
            color='#EEEEEE', edgecolor='#B0B0B0', linestyle=':', label='95% Null Band (Within-Match Permutation)')
    ax.scatter(null_b_rev['Batter_Null_Median'], y_pos, marker='|', color='#666666', s=90, label='Null Median', zorder=3)

    x_err_b = [
        np.maximum(0, top_b_rev['shrunk_rating'] - top_b_rev['ci_lower_90']),
        np.maximum(0, top_b_rev['ci_upper_90'] - top_b_rev['shrunk_rating'])
    ]
    ax.errorbar(top_b_rev['shrunk_rating'], y_pos, xerr=x_err_b, fmt='o', color='#E21A5C', ecolor='#222222',
                elinewidth=1.8, capsize=4, capthick=1.2, markersize=6.5, label='Posterior Rating (90% CI)', zorder=4)

    ax.set_yticks(y_pos)
    labels_b = [f"#{row['rank']} {row['striker_name']} ({str(row['teams']).split(',')[0].strip()})" for _, row in top_b_rev.iterrows()]
    ax.set_yticklabels(labels_b, fontsize=8, fontweight='bold')
    ax.set_xlabel("High-Pressure Rating (Runs Added / 100 Balls)", fontsize=8.5, fontweight='bold', labelpad=4)
    ax.set_title("Top 10 Batters Under Pressure: Posterior 90% CIs vs 95% Within-Match Null Band", fontsize=9.5, fontweight='bold', pad=7)
    ax.set_xlim(left=-2, right=49)
    ax.tick_params(labelsize=7.5)
    ax.grid(axis='x', linestyle='--', alpha=0.4)

    # Right column header and entries
    ax.text(38.5, 9.7, "Rating    P(T10)", va='bottom', ha='left', fontsize=7.5, fontweight='bold', color='#444444')
    for i, (_, row) in enumerate(top_b_rev.iterrows()):
        txt = f"{row['shrunk_rating']:+.2f}   {row['top10_probability']*100:.0f}%"
        ax.text(38.5, i, txt, va='center', ha='left', fontsize=7.5, fontweight='bold', color='#111111')

    ax.legend(loc='lower left', frameon=True, fontsize=7.2, facecolor='white', framealpha=0.92)
    plt.tight_layout()
    fig.savefig(OUTPUTS_DIR / "top10_batters_intervals.png", dpi=300)
    plt.close(fig)

    # 2B. Bowlers Forest Plot
    top_bw_rev = top_bowl.iloc[::-1].reset_index(drop=True)
    null_bw_rev = null_bands.iloc[::-1].reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(8.5, 3.2), dpi=300)
    null_width_bw = null_bw_rev['Bowler_Null_Upper_95'] - null_bw_rev['Bowler_Null_Lower_95']
    ax.barh(y_pos, width=null_width_bw, left=null_bw_rev['Bowler_Null_Lower_95'], height=0.45,
            color='#EEEEEE', edgecolor='#B0B0B0', linestyle=':', label='95% Null Band (Within-Match Permutation)')
    ax.scatter(null_bw_rev['Bowler_Null_Median'], y_pos, marker='|', color='#666666', s=90, label='Null Median', zorder=3)

    x_err_bw = [
        np.maximum(0, top_bw_rev['shrunk_rating'] - top_bw_rev['ci_lower_90']),
        np.maximum(0, top_bw_rev['ci_upper_90'] - top_bw_rev['shrunk_rating'])
    ]
    ax.errorbar(top_bw_rev['shrunk_rating'], y_pos, xerr=x_err_bw, fmt='s', color='#004B87', ecolor='#222222',
                elinewidth=1.8, capsize=4, capthick=1.2, markersize=6.5, label='Posterior Rating (90% CI)', zorder=4)

    ax.set_yticks(y_pos)
    labels_bw = [f"#{row['rank']} {row['bowler_name']} ({str(row['teams']).split(',')[0].strip()})" for _, row in top_bw_rev.iterrows()]
    ax.set_yticklabels(labels_bw, fontsize=8, fontweight='bold')
    ax.set_xlabel("High-Pressure Rating (Runs Saved / 100 Balls)", fontsize=8.5, fontweight='bold', labelpad=4)
    ax.set_title("Top 10 Bowlers Under Pressure: Posterior 90% CIs vs 95% Within-Match Null Band", fontsize=9.5, fontweight='bold', pad=7)
    ax.set_xlim(left=-2, right=38)
    ax.tick_params(labelsize=7.5)
    ax.grid(axis='x', linestyle='--', alpha=0.4)

    # Right column header and entries
    ax.text(29.0, 9.7, "Rating    P(T10)", va='bottom', ha='left', fontsize=7.5, fontweight='bold', color='#444444')
    for i, (_, row) in enumerate(top_bw_rev.iterrows()):
        txt = f"{row['shrunk_rating']:+.2f}   {row['top10_probability']*100:.0f}%"
        ax.text(29.0, i, txt, va='center', ha='left', fontsize=7.5, fontweight='bold', color='#111111')

    ax.legend(loc='lower left', frameon=True, fontsize=7.2, facecolor='white', framealpha=0.92)
    plt.tight_layout()
    fig.savefig(OUTPUTS_DIR / "top10_bowlers_intervals.png", dpi=300)
    plt.close(fig)
    print("  [+] Saved full-width batters and bowlers forest plots.")

if __name__ == "__main__":
    generate_clean_charts()
