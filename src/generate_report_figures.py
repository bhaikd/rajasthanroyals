"""
generate_report_figures.py - Generates all figures matching the SupeRR Selector problem-statement style.

Figures produced from actual output CSV data:
1. Pipeline Architecture Flowchart (Data -> State -> WP -> Leverage -> HP -> xR/xW -> Impact -> REML -> Ranking)
2. Forest Plot - Batters (Montserrat font, #E50695 pink markers/CIs, #F5F6FA null band, Rating & P(T10) right column)
3. Forest Plot - Bowlers (Montserrat font, #021D45 navy markers/CIs, #F5F6FA null band, Rating & P(T10) right column)
4. Stacked Decomposition Bar Chart (Shrunk Baseline + Shrunk Delta = Total Rating, negative Delta in red)
5. Specification Rank Ranges Chart (Min-Max line with marker at primary rank across 14 specifications)
"""
import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.font_manager as fm

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = BASE_DIR / "outputs"
FONTS_DIR = OUTPUTS_DIR / "fonts"

# Add Montserrat font files to matplotlib
for font_file in ["Montserrat-Regular.ttf", "Montserrat-Bold.ttf", "Montserrat-Medium.ttf", "Montserrat-SemiBold.ttf"]:
    fp = FONTS_DIR / font_file
    if fp.exists():
        fm.fontManager.addfont(str(fp))

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = ['Montserrat', 'DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['axes.edgecolor'] = '#D0DCE5'
plt.rcParams['axes.linewidth'] = 0.8

# Reference Color Palette
COLOR_NAVY = '#021D45'
COLOR_BODY = '#1F2A44'
COLOR_PINK = '#E50695'
COLOR_BOX_BG = '#F5F6FA'
COLOR_BORDER = '#E2E6EE'
COLOR_MUTED = '#606F89'
COLOR_GREEN = '#28A745'
COLOR_RED = '#DC3545'

def generate_pipeline_diagram():
    """Generates a clean, horizontal pipeline flow diagram matching the reference aesthetic."""
    fig, ax = plt.subplots(figsize=(11, 2.2), dpi=300)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 2.2)
    ax.axis('off')

    steps = [
        ("Raw Deliveries", "883 Matches\n200,999 Balls"),
        ("Match State", "Innings, Balls,\nTarget, Phase"),
        ("Win Probability", "GroupKFold LGBM\nBrier 0.23 / 0.16"),
        ("Outcome Leverage", "E[|ΔWP|] across\n7 outcomes"),
        ("High Pressure", "Top Quartile 25%\n50,241 Balls"),
        ("xR & xW Baselines", "Out-of-fold LGBM\nZero-mean error"),
        ("Net Impact", "Runs Added/Saved\nvs Expectation"),
        ("REML Shrinkage", "Baseline (B) +\nClutch Delta (Δ)"),
        ("Final Rankings", "Top 10 Bat / Bowl\n90% CI & P(T10)")
    ]

    box_w = 0.96
    box_h = 1.3
    y_center = 1.1

    colors_list = [
        COLOR_BOX_BG, COLOR_BOX_BG, COLOR_BOX_BG, COLOR_BOX_BG,
        '#FDF0F7', COLOR_BOX_BG, COLOR_BOX_BG, '#F4F0FA',
        COLOR_NAVY
    ]
    border_colors = [
        COLOR_BORDER, COLOR_BORDER, COLOR_BORDER, COLOR_BORDER,
        COLOR_PINK, COLOR_BORDER, COLOR_BORDER, '#7B42BC',
        COLOR_NAVY
    ]
    text_colors = [
        COLOR_NAVY, COLOR_NAVY, COLOR_NAVY, COLOR_NAVY,
        COLOR_PINK, COLOR_NAVY, COLOR_NAVY, '#4A154B',
        '#FFFFFF'
    ]

    for i, (title, desc) in enumerate(steps):
        x = 0.35 + i * 1.16
        bg_col = colors_list[i]
        bd_col = border_colors[i]
        txt_col = text_colors[i]

        rect = patches.FancyBboxPatch(
            (x, y_center - box_h / 2), box_w, box_h,
            boxstyle="round,pad=0.04,rounding_size=0.08",
            linewidth=1.2, edgecolor=bd_col, facecolor=bg_col, zorder=2
        )
        ax.add_patch(rect)

        ax.text(x + box_w / 2, y_center + 0.28, title, ha='center', va='center',
                fontsize=7.8, fontweight='bold', color=txt_col, fontfamily='Montserrat', zorder=3)
        desc_col = '#E0E0E0' if txt_col == '#FFFFFF' else COLOR_MUTED
        ax.text(x + box_w / 2, y_center - 0.22, desc, ha='center', va='center',
                fontsize=6.6, color=desc_col, fontfamily='Montserrat', zorder=3)

        if i < len(steps) - 1:
            ax.annotate('', xy=(x + box_w + 0.16, y_center), xytext=(x + box_w + 0.02, y_center),
                        arrowprops=dict(arrowstyle="->", color=COLOR_NAVY, lw=1.3, shrinkA=0, shrinkB=0),
                        zorder=4)

    plt.tight_layout()
    out_path = OUTPUTS_DIR / "pipeline_diagram.png"
    fig.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"[+] Saved pipeline diagram to: {out_path}")

def generate_forest_plots():
    """Generates standalone publication-grade forest plots for batters and bowlers."""
    top_bat = pd.read_csv(OUTPUTS_DIR / "final_top10_batters.csv")
    top_bowl = pd.read_csv(OUTPUTS_DIR / "final_top10_bowlers.csv")
    null_bands = pd.read_csv(OUTPUTS_DIR / "null_top10_bands.csv")

    # 1. Batters Forest Plot
    top_b_rev = top_bat.iloc[::-1].reset_index(drop=True)
    null_b_rev = null_bands.iloc[::-1].reset_index(drop=True)
    y_pos = np.arange(len(top_b_rev))

    fig, ax = plt.subplots(figsize=(9.2, 3.8), dpi=300)
    null_width_b = null_b_rev['Batter_Null_Upper_95'] - null_b_rev['Batter_Null_Lower_95']
    
    # Solid light null band
    ax.barh(y_pos, width=null_width_b, left=null_b_rev['Batter_Null_Lower_95'], height=0.55,
            color=COLOR_BOX_BG, edgecolor=COLOR_BORDER, linewidth=0.8,
            label='95% Within-Match Null Band (1,000 Permutations)')
    ax.scatter(null_b_rev['Batter_Null_Median'], y_pos, marker='|', color=COLOR_MUTED, s=100, linewidths=1.8,
               label='Null Median', zorder=3)

    x_err_b = [
        np.maximum(0, top_b_rev['shrunk_rating'] - top_b_rev['ci_lower_90']),
        np.maximum(0, top_b_rev['ci_upper_90'] - top_b_rev['shrunk_rating'])
    ]
    ax.errorbar(top_b_rev['shrunk_rating'], y_pos, xerr=x_err_b, fmt='o', color=COLOR_PINK, ecolor=COLOR_BODY,
                elinewidth=1.8, capsize=4.5, capthick=1.4, markersize=7.0, label='Posterior Rating (90% Match-Grouped CI)', zorder=4)

    ax.set_yticks(y_pos)
    labels_b = [f"#{row['rank']} {row['striker_name']} ({str(row['teams']).split(',')[0].strip()})" for _, row in top_b_rev.iterrows()]
    ax.set_yticklabels(labels_b, fontsize=8.5, fontweight='bold', color=COLOR_NAVY, fontfamily='Montserrat')
    ax.set_xlabel("High-Pressure Impact Rating (Runs Added / 100 Balls Above Context)", fontsize=8.5, fontweight='bold', color=COLOR_BODY, fontfamily='Montserrat', labelpad=5)
    ax.set_xlim(left=-4, right=54)
    ax.tick_params(labelsize=8, colors=COLOR_BODY)
    ax.grid(axis='x', linestyle='--', alpha=0.45, color=COLOR_BORDER)

    # Right column header and entries
    ax.text(42.0, 9.75, "Rating     P(T10)", va='bottom', ha='left', fontsize=8.2, fontweight='bold', color=COLOR_NAVY, fontfamily='Montserrat')
    for i, (_, row) in enumerate(top_b_rev.iterrows()):
        txt = f"{row['shrunk_rating']:+6.2f}    {row['top10_probability']*100:4.1f}%"
        ax.text(42.0, i, txt, va='center', ha='left', fontsize=8.0, fontfamily='monospace', fontweight='bold', color=COLOR_BODY)

    # Legend placed BELOW axes
    ax.legend(loc='upper center', bbox_to_anchor=(0.42, -0.16), ncol=3, frameon=True, fontsize=8.0, facecolor='#FFFFFF', edgecolor=COLOR_BORDER)
    plt.tight_layout()
    out_b = OUTPUTS_DIR / "forest_plot_batters.png"
    fig.savefig(out_b, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"[+] Saved batters forest plot to: {out_b}")

    # 2. Bowlers Forest Plot
    top_bw_rev = top_bowl.iloc[::-1].reset_index(drop=True)
    null_bw_rev = null_bands.iloc[::-1].reset_index(drop=True)
    y_pos_w = np.arange(len(top_bw_rev))

    fig, ax = plt.subplots(figsize=(9.2, 3.8), dpi=300)
    null_width_bw = null_bw_rev['Bowler_Null_Upper_95'] - null_bw_rev['Bowler_Null_Lower_95']
    
    # Solid light null band
    ax.barh(y_pos_w, width=null_width_bw, left=null_bw_rev['Bowler_Null_Lower_95'], height=0.55,
            color=COLOR_BOX_BG, edgecolor=COLOR_BORDER, linewidth=0.8,
            label='95% Within-Match Null Band (1,000 Permutations)')
    ax.scatter(null_bw_rev['Bowler_Null_Median'], y_pos_w, marker='|', color=COLOR_MUTED, s=100, linewidths=1.8,
               label='Null Median', zorder=3)

    x_err_bw = [
        np.maximum(0, top_bw_rev['shrunk_rating'] - top_bw_rev['ci_lower_90']),
        np.maximum(0, top_bw_rev['ci_upper_90'] - top_bw_rev['shrunk_rating'])
    ]
    ax.errorbar(top_bw_rev['shrunk_rating'], y_pos_w, xerr=x_err_bw, fmt='s', color=COLOR_NAVY, ecolor=COLOR_BODY,
                elinewidth=1.8, capsize=4.5, capthick=1.4, markersize=6.8, label='Posterior Rating (90% Match-Grouped CI)', zorder=4)

    ax.set_yticks(y_pos_w)
    labels_bw = [f"#{row['rank']} {row['bowler_name']} ({str(row['teams']).split(',')[0].strip()})" for _, row in top_bw_rev.iterrows()]
    ax.set_yticklabels(labels_bw, fontsize=8.5, fontweight='bold', color=COLOR_NAVY, fontfamily='Montserrat')
    ax.set_xlabel("High-Pressure Impact Rating (Runs Saved / 100 Balls Below Context)", fontsize=8.5, fontweight='bold', color=COLOR_BODY, fontfamily='Montserrat', labelpad=5)
    ax.set_xlim(left=-4, right=44)
    ax.tick_params(labelsize=8, colors=COLOR_BODY)
    ax.grid(axis='x', linestyle='--', alpha=0.45, color=COLOR_BORDER)

    # Right column header and entries
    ax.text(34.0, 9.75, "Rating     P(T10)", va='bottom', ha='left', fontsize=8.2, fontweight='bold', color=COLOR_NAVY, fontfamily='Montserrat')
    for i, (_, row) in enumerate(top_bw_rev.iterrows()):
        txt = f"{row['shrunk_rating']:+6.2f}    {row['top10_probability']*100:4.1f}%"
        ax.text(34.0, i, txt, va='center', ha='left', fontsize=8.0, fontfamily='monospace', fontweight='bold', color=COLOR_BODY)

    # Legend placed BELOW axes
    ax.legend(loc='upper center', bbox_to_anchor=(0.42, -0.16), ncol=3, frameon=True, fontsize=8.0, facecolor='#FFFFFF', edgecolor=COLOR_BORDER)
    plt.tight_layout()
    out_bw = OUTPUTS_DIR / "forest_plot_bowlers.png"
    fig.savefig(out_bw, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"[+] Saved bowlers forest plot to: {out_bw}")

def generate_stacked_decomposition_chart():
    """Generates a horizontal stacked bar chart: Shrunk Baseline + Shrunk Delta = Total Rating."""
    df_verif = pd.read_csv(OUTPUTS_DIR / "shrinkage_verification_table.csv")
    bat_df = df_verif[df_verif['Role'] == 'Bat'].iloc[::-1].reset_index(drop=True)
    bowl_df = df_verif[df_verif['Role'] == 'Bowl'].iloc[::-1].reset_index(drop=True)

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.4), dpi=300)

    # Batters panel
    y_bat = np.arange(len(bat_df))
    axes[0].barh(y_bat, bat_df['B_shrunk'], height=0.52, color=COLOR_NAVY, alpha=0.88, label='Shrunk Baseline (B)')
    for i, row in bat_df.iterrows():
        d_val = row['D_shrunk']
        b_val = row['B_shrunk']
        tot = row['Rating']
        if d_val >= 0:
            axes[0].barh(i, d_val, left=b_val, height=0.52, color=COLOR_GREEN, alpha=0.9)
        else:
            axes[0].barh(i, abs(d_val), left=tot, height=0.52, color=COLOR_RED, alpha=0.9)
        axes[0].text(tot + 0.8, i, f"{tot:+.1f}", va='center', ha='left', fontsize=7.6, fontweight='bold', color=COLOR_BODY, fontfamily='Montserrat')

    axes[0].set_yticks(y_bat)
    axes[0].set_yticklabels([f"#{r['Rank']} {r['Player']}" for _, r in bat_df.iterrows()], fontsize=8.2, fontweight='bold', color=COLOR_NAVY, fontfamily='Montserrat')
    axes[0].set_xlabel("Impact Rating (Runs Added / 100 Balls)", fontsize=8.5, fontweight='bold', color=COLOR_BODY, fontfamily='Montserrat')
    axes[0].set_title("Top 10 Batters: Baseline + Pressure Elevation", fontsize=9.2, fontweight='bold', color=COLOR_NAVY, fontfamily='Montserrat', pad=6)
    axes[0].set_xlim(-1, 35)
    axes[0].grid(axis='x', linestyle='--', alpha=0.4, color=COLOR_BORDER)

    # Bowlers panel
    y_bowl = np.arange(len(bowl_df))
    axes[1].barh(y_bowl, bowl_df['B_shrunk'], height=0.52, color=COLOR_NAVY, alpha=0.88, label='Shrunk Baseline (B)')
    for i, row in bowl_df.iterrows():
        d_val = row['D_shrunk']
        b_val = row['B_shrunk']
        tot = row['Rating']
        if d_val >= 0:
            axes[1].barh(i, d_val, left=b_val, height=0.52, color=COLOR_GREEN, alpha=0.9)
        else:
            axes[1].barh(i, abs(d_val), left=tot, height=0.52, color=COLOR_RED, alpha=0.9)
        axes[1].text(tot + 0.6, i, f"{tot:+.1f}", va='center', ha='left', fontsize=7.6, fontweight='bold', color=COLOR_BODY, fontfamily='Montserrat')

    axes[1].set_yticks(y_bowl)
    axes[1].set_yticklabels([f"#{r['Rank']} {r['Player']}" for _, r in bowl_df.iterrows()], fontsize=8.2, fontweight='bold', color=COLOR_NAVY, fontfamily='Montserrat')
    axes[1].set_xlabel("Impact Rating (Runs Saved / 100 Balls)", fontsize=8.5, fontweight='bold', color=COLOR_BODY, fontfamily='Montserrat')
    axes[1].set_title("Top 10 Bowlers: Baseline + Pressure Elevation", fontsize=9.2, fontweight='bold', color=COLOR_NAVY, fontfamily='Montserrat', pad=6)
    axes[1].set_xlim(-1, 25)
    axes[1].grid(axis='x', linestyle='--', alpha=0.4, color=COLOR_BORDER)

    # Custom legend across bottom
    handles = [
        patches.Patch(facecolor=COLOR_NAVY, alpha=0.88, label='Shrunk Baseline (B_shrunk)'),
        patches.Patch(facecolor=COLOR_GREEN, alpha=0.9, label='Positive Pressure Elevation (+Δ_shrunk)'),
        patches.Patch(facecolor=COLOR_RED, alpha=0.9, label='Negative Pressure Dip (-Δ_shrunk)')
    ]
    fig.legend(handles=handles, loc='upper center', bbox_to_anchor=(0.5, 0.02), ncol=3, frameon=True, fontsize=8.2, facecolor='#FFFFFF', edgecolor=COLOR_BORDER)

    plt.tight_layout(rect=[0, 0.05, 1, 1])
    out_path = OUTPUTS_DIR / "stacked_decomposition_chart.png"
    fig.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"[+] Saved stacked decomposition chart to: {out_path}")

def generate_rank_ranges_chart():
    """Generates a rank-range chart (min-max line with primary rank marker) across 14 specifications."""
    df_ranges = pd.read_csv(OUTPUTS_DIR / "top10_rank_ranges.csv")
    bat_ranges = df_ranges[df_ranges['Discipline'] == 'Batter'].iloc[::-1].reset_index(drop=True)
    bowl_ranges = df_ranges[df_ranges['Discipline'] == 'Bowler'].iloc[::-1].reset_index(drop=True)

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.4), dpi=300)

    # Batters
    y_bat = np.arange(len(bat_ranges))
    for i, row in bat_ranges.iterrows():
        min_r = row['Min_Rank']
        max_r = row['Max_Rank']
        pri_r = row['Rank']
        axes[0].plot([min_r, max_r], [i, i], color=COLOR_PINK, lw=2.2, solid_capstyle='round')
        axes[0].scatter([min_r, max_r], [i, i], color=COLOR_PINK, s=35, zorder=3)
        axes[0].scatter(pri_r, i, color=COLOR_NAVY, s=65, edgecolors='white', linewidth=1.2, zorder=4)
        axes[0].text(max_r + 0.6, i, f"[{min_r}, {max_r}]", va='center', ha='left', fontsize=7.4, color=COLOR_MUTED, fontfamily='Montserrat')

    axes[0].set_yticks(y_bat)
    axes[0].set_yticklabels([f"#{r['Rank']} {r['Player']}" for _, r in bat_ranges.iterrows()], fontsize=8.2, fontweight='bold', color=COLOR_NAVY, fontfamily='Montserrat')
    axes[0].set_xlabel("Rank Across 14 Specifications (Lower = Better)", fontsize=8.5, fontweight='bold', color=COLOR_BODY, fontfamily='Montserrat')
    axes[0].set_title("Batters: Rank Sensitivity Range Across 14 Specifications", fontsize=9.2, fontweight='bold', color=COLOR_PINK, fontfamily='Montserrat', pad=6)
    axes[0].set_xlim(0, 26)
    axes[0].set_xticks([1, 5, 10, 15, 20, 25])
    axes[0].grid(axis='x', linestyle='--', alpha=0.4, color=COLOR_BORDER)

    # Bowlers
    y_bowl = np.arange(len(bowl_ranges))
    for i, row in bowl_ranges.iterrows():
        min_r = row['Min_Rank']
        max_r = row['Max_Rank']
        pri_r = row['Rank']
        axes[1].plot([min_r, max_r], [i, i], color=COLOR_NAVY, lw=2.2, solid_capstyle='round')
        axes[1].scatter([min_r, max_r], [i, i], color=COLOR_NAVY, s=35, zorder=3)
        axes[1].scatter(pri_r, i, color=COLOR_PINK, s=65, edgecolors='white', linewidth=1.2, zorder=4)
        axes[1].text(max_r + 0.6, i, f"[{min_r}, {max_r}]", va='center', ha='left', fontsize=7.4, color=COLOR_MUTED, fontfamily='Montserrat')

    axes[1].set_yticks(y_bowl)
    axes[1].set_yticklabels([f"#{r['Rank']} {r['Player']}" for _, r in bowl_ranges.iterrows()], fontsize=8.2, fontweight='bold', color=COLOR_NAVY, fontfamily='Montserrat')
    axes[1].set_xlabel("Rank Across 14 Specifications (Lower = Better)", fontsize=8.5, fontweight='bold', color=COLOR_BODY, fontfamily='Montserrat')
    axes[1].set_title("Bowlers: Rank Sensitivity Range Across 14 Specifications", fontsize=9.2, fontweight='bold', color=COLOR_NAVY, fontfamily='Montserrat', pad=6)
    axes[1].set_xlim(0, 29)
    axes[1].set_xticks([1, 5, 10, 15, 20, 25])
    axes[1].grid(axis='x', linestyle='--', alpha=0.4, color=COLOR_BORDER)

    # Custom legend
    handles = [
        plt.Line2D([0], [0], color=COLOR_MUTED, lw=2.2, marker='o', markersize=5, label='[Min, Max] Sensitivity Range'),
        plt.Line2D([0], [0], color='none', marker='o', markerfacecolor=COLOR_NAVY, markeredgecolor='white', markersize=7, label='Primary Base Rank')
    ]
    fig.legend(handles=handles, loc='upper center', bbox_to_anchor=(0.5, 0.02), ncol=2, frameon=True, fontsize=8.2, facecolor='#FFFFFF', edgecolor=COLOR_BORDER)

    plt.tight_layout(rect=[0, 0.05, 1, 1])
    out_path = OUTPUTS_DIR / "rank_ranges_chart.png"
    fig.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"[+] Saved rank ranges chart to: {out_path}")

if __name__ == "__main__":
    print("[*] Generating all figures from dataset CSV files with reference styling...")
    generate_pipeline_diagram()
    generate_forest_plots()
    generate_stacked_decomposition_chart()
    generate_rank_ranges_chart()
    print("[✓] All figures generated successfully.")
