"""
Master Execution Pipeline: SupeRR Selector Season 2 – Round 1
Executes all stages end-to-end with full reproducibility.
"""
import sys
import time
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

from src.data_audit import run_data_audit
from src.match_state import compute_match_state_features
from src.pressure_model import train_win_probability_and_pressure
from src.expected_value import train_expected_value_models
from src.player_metrics import compute_player_metrics
from src.fair_comparison import run_fair_comparison
from src.reliability import run_reliability_tests
from src.visualizations import generate_visualizations
from src.build_notebook import create_analysis_notebook
from src.export_report_pdf import export_pdf

def main():
    start_time = time.time()
    print("=" * 80)
    print("STARTING END-TO-END PIPELINE: SUPERR SELECTOR SEASON 2 (ROUND 1)")
    print("=" * 80)

    print("\n>>> Running Stage 0: Data Audit...")
    run_data_audit()

    print("\n>>> Running Stage 1: Pre-Ball Match-State Feature Engineering...")
    compute_match_state_features()

    print("\n>>> Running Stage 2: Win-Probability Modeling & Pressure Definition...")
    train_win_probability_and_pressure()

    print("\n>>> Running Stage 3: Context-Aware Expected-Value Models...")
    train_expected_value_models()

    print("\n>>> Running Stage 4: Raw Player Metrics Engine...")
    compute_player_metrics()

    print("\n>>> Running Stage 5: Fair Comparisons, Shrinkage & Bootstrap...")
    run_fair_comparison()

    print("\n>>> Running Stage 6: Reliability & Sensitivity Tests...")
    run_reliability_tests()

    print("\n>>> Running Stage 7: Publication Visualizations...")
    generate_visualizations()

    print("\n>>> Building Narrative Analysis Notebook...")
    create_analysis_notebook()

    print("\n>>> Compiling Publication PDF Methodology Report...")
    export_pdf()

    # Print Final Unstop Lists in Rank Order
    import pandas as pd
    out_dir = BASE_DIR / "outputs"
    final_bat = pd.read_csv(out_dir / "final_top10_batters.csv")
    final_bowl = pd.read_csv(out_dir / "final_top10_bowlers.csv")

    print("\n" + "=" * 90)
    print("FINAL UNSTOP SUBMISSION: TOP 10 BATTERS UNDER PRESSURE (2022 ONWARDS)")
    print("=" * 90)
    print(f"{'Rk':<3} {'Player Name':<22} {'Team(s)':<30} {'HP Balls':<9} {'Inn':<4} {'HP SR':<7} {'Rating':<8} {'90% Credible Interval':<22} {'Delta':<7} {'Delta CI':<16} {'Label':<8} {'Succ%':<6} {'P(T10)':<6}")
    print("-" * 155)
    for _, r in final_bat.iterrows():
        team_str = str(r['teams']).split(',')[0].strip()
        print(f"{int(r['rank']):<3} {r['striker_name']:<22} {team_str:<30} {int(r['hp_balls_faced']):<9} {int(r['pressure_innings_count']):<4} {r['hp_strike_rate']:<7.1f} {r['shrunk_rating']:<+8.2f} [{r['ci_lower_90']:+.2f}, {r['ci_upper_90']:+.2f}]        {r['shrunk_delta']:<+7.2f} [{r['delta_ci_lower_90']:+.1f}, {r['delta_ci_upper_90']:+.1f}]  {r['delta_label']:<8} {r['shrunk_success_rate']:<6.1f} {r['top10_probability']*100:<5.1f}%")

    print("\n" + "=" * 90)
    print("FINAL UNSTOP SUBMISSION: TOP 10 BOWLERS UNDER PRESSURE (2022 ONWARDS)")
    print("=" * 90)
    print(f"{'Rk':<3} {'Player Name':<22} {'Team(s)':<30} {'HP Balls':<9} {'Spl':<4} {'HP Econ':<8} {'Rating':<8} {'90% Credible Interval':<22} {'Delta':<7} {'Delta CI':<16} {'Label':<8} {'Succ%':<6} {'P(T10)':<6}")
    print("-" * 155)
    for _, r in final_bowl.iterrows():
        team_str = str(r['teams']).split(',')[0].strip()
        print(f"{int(r['rank']):<3} {r['bowler_name']:<22} {team_str:<30} {int(r['hp_legal_balls']):<9} {int(r['pressure_spells_count']):<4} {r['hp_economy']:<8.2f} {r['shrunk_rating']:<+8.2f} [{r['ci_lower_90']:+.2f}, {r['ci_upper_90']:+.2f}]        {r['shrunk_delta']:<+7.2f} [{r['delta_ci_lower_90']:+.1f}, {r['delta_ci_upper_90']:+.1f}]  {r['delta_label']:<8} {r['shrunk_success_rate']:<6.1f} {r['top10_probability']*100:<5.1f}%")

    if (out_dir / "excluded_pakistan_players.csv").exists():
        excl_df = pd.read_csv(out_dir / "excluded_pakistan_players.csv")
        print("\n" + "=" * 90)
        print("EXCLUDED PAKISTAN PLAYERS IN TOP 20 (AUTHOR'S ELIGIBILITY CHOICE AUDIT)")
        print("=" * 90)
        print(f"{'Role':<8} {'Player Name':<22} {'Unc. Rk':<9} {'HP Balls':<9} {'Rating':<8} {'Baseline':<9} {'Delta':<8} {'Teams':<25}")
        print("-" * 105)
        for _, r in excl_df.iterrows():
            print(f"{r['Discipline']:<8} {r['Player']:<22} {int(r['Unconstrained_Rank']):<9} {int(r['HP_Balls']):<9} {r['Shrunk_Rating']:<+8.2f} {r['Shrunk_Baseline']:<+9.2f} {r['Shrunk_Delta']:<+8.2f} {str(r['Teams']):<25}")

    elapsed = time.time() - start_time
    print("\n" + "=" * 90)
    print(f"PIPELINE COMPLETED SUCCESSFULLY IN {elapsed:.1f} SECONDS!")
    print("=" * 90)

if __name__ == "__main__":
    main()
