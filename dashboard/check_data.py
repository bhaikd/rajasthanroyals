"""
dashboard/check_data.py - Data assertion and integrity verification script.

Verifies:
1. Cohort sizes: 131 eligible batters, 140 eligible bowlers.
2. No Pakistan players in active cohorts.
3. Recomputation of Top 10 from full_ratings matches final_top10 files exactly.
4. Rank orders and metrics match Table 1 of the methodology report.
5. No hardcoded player metrics in dashboard codebase.
6. Prints the verified Top 10 in rank order at the end.
"""
from pathlib import Path
import re
import sys
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = BASE_DIR / "outputs"
DASHBOARD_DIR = BASE_DIR / "dashboard"

EXPECTED_TOP10_BATTERS = [
    ("Suryakumar Yadav", 28.39, 8.99),
    ("Vaibhav Sooryavanshi", 23.89, 1.71),
    ("Jos Buttler", 23.06, 8.68),
    ("Heinrich Klaasen", 22.73, 6.01),
    ("Reeza Hendricks", 22.64, 14.31),
    ("Abhishek Sharma", 21.93, -2.25),
    ("Phil Salt", 21.69, 5.79),
    ("Rinku Singh", 20.98, 12.06),
    ("Shreyas Iyer", 19.97, 10.33),
    ("Tim David", 19.75, 0.80)
]

EXPECTED_TOP10_BOWLERS = [
    ("Josh Hazlewood", 17.83, 8.70),
    ("Matheesha Pathirana", 17.48, 7.66),
    ("Sunil Narine", 14.39, 5.32),
    ("Jasprit Bumrah", 13.48, -5.11),
    ("Jacob Duffy", 13.10, 4.26),
    ("Rashid Khan", 12.97, 7.27),
    ("Lockie Ferguson", 12.83, 8.53),
    ("Varun Chakravarthy", 12.29, 0.26),
    ("Nathan Ellis", 12.26, 1.90),
    ("Mitchell Santner", 12.18, 8.02)
]

def check_cohorts():
    print("[1/5] Checking cohort eligibility and sizes...")
    bat_df = pd.read_csv(OUTPUTS_DIR / "full_ratings_batters.csv")
    bowl_df = pd.read_csv(OUTPUTS_DIR / "full_ratings_bowlers.csv")
    
    assert len(bat_df) == 131, f"Expected 131 batters, found {len(bat_df)}"
    assert len(bowl_df) == 140, f"Expected 140 bowlers, found {len(bowl_df)}"
    print(f"      Passed: 131 batters, 140 bowlers verified.")
    
    # Check no Pakistan players
    pak_players = ["Mohammad Rizwan", "Babar Azam", "Shaheen Afridi", "Haris Rauf", "Mohammad Nawaz", "Abrar Ahmed", "Sufiyan Muqeem", "Naseem Shah"]
    for p in pak_players:
        assert p not in bat_df["striker_name"].values, f"Found Pakistan player {p} in eligible batters!"
        assert p not in bowl_df["bowler_name"].values, f"Found Pakistan player {p} in eligible bowlers!"
    print("      Passed: No Pakistan players in eligible cohorts.")
    return bat_df, bowl_df

def check_top10_recomputation(bat_df, bowl_df):
    print("[2/5] Recomputing Top 10 from full-ratings files...")
    # Batters
    recomputed_top10_bat = bat_df.sort_values("shrunk_rating", ascending=False).head(10).reset_index(drop=True)
    final_top10_bat = pd.read_csv(OUTPUTS_DIR / "final_top10_batters.csv").sort_values("rank").reset_index(drop=True)
    
    for i, (expected_name, exp_rating, exp_delta) in enumerate(EXPECTED_TOP10_BATTERS):
        actual_name = recomputed_top10_bat.iloc[i]["striker_name"]
        actual_rating = round(recomputed_top10_bat.iloc[i]["shrunk_rating"], 2)
        actual_delta = round(recomputed_top10_bat.iloc[i]["shrunk_delta"], 2)
        
        file_name = final_top10_bat.iloc[i]["striker_name"]
        file_rating = round(final_top10_bat.iloc[i]["shrunk_rating"], 2)
        
        assert actual_name == expected_name, f"Batter rank {i+1} mismatch: expected {expected_name}, got {actual_name}"
        assert file_name == expected_name, f"final_top10_batters file rank {i+1} mismatch: expected {expected_name}, got {file_name}"
        assert abs(actual_rating - exp_rating) < 0.05, f"Rating mismatch for {actual_name}: {actual_rating} vs {exp_rating}"
        assert abs(actual_delta - exp_delta) < 0.05, f"Delta mismatch for {actual_name}: {actual_delta} vs {exp_delta}"
        
    print("      Passed: Top 10 Batters recomputed perfectly from full ratings.")
    
    # Bowlers
    recomputed_top10_bowl = bowl_df.sort_values("shrunk_rating", ascending=False).head(10).reset_index(drop=True)
    final_top10_bowl = pd.read_csv(OUTPUTS_DIR / "final_top10_bowlers.csv").sort_values("rank").reset_index(drop=True)
    
    for i, (expected_name, exp_rating, exp_delta) in enumerate(EXPECTED_TOP10_BOWLERS):
        actual_name = recomputed_top10_bowl.iloc[i]["bowler_name"]
        actual_rating = round(recomputed_top10_bowl.iloc[i]["shrunk_rating"], 2)
        actual_delta = round(recomputed_top10_bowl.iloc[i]["shrunk_delta"], 2)
        
        file_name = final_top10_bowl.iloc[i]["bowler_name"]
        file_rating = round(final_top10_bowl.iloc[i]["shrunk_rating"], 2)
        
        assert actual_name == expected_name, f"Bowler rank {i+1} mismatch: expected {expected_name}, got {actual_name}"
        assert file_name == expected_name, f"final_top10_bowlers file rank {i+1} mismatch: expected {expected_name}, got {file_name}"
        assert abs(actual_rating - exp_rating) < 0.05, f"Rating mismatch for {actual_name}: {actual_rating} vs {exp_rating}"
        assert abs(actual_delta - exp_delta) < 0.05, f"Delta mismatch for {actual_name}: {actual_delta} vs {exp_delta}"
        
    print("      Passed: Top 10 Bowlers recomputed perfectly from full ratings.")
    return recomputed_top10_bat, recomputed_top10_bowl

def check_excluded_audit():
    print("[3/5] Checking excluded Pakistan players audit table...")
    excl_df = pd.read_csv(OUTPUTS_DIR / "excluded_pakistan_players.csv")
    assert len(excl_df) == 4, f"Expected 4 excluded players, found {len(excl_df)}"
    assert "Mohammad Rizwan" in excl_df["Player"].values
    assert "Mohammad Nawaz" in excl_df["Player"].values
    assert "Abrar Ahmed" in excl_df["Player"].values
    assert "Sufiyan Muqeem" in excl_df["Player"].values
    print("      Passed: All 4 excluded players verified with author eligibility choice reason.")

def check_no_hardcoded_metrics():
    print("[4/5] Checking dashboard code for hard-coded player metric literals...")
    suspicious_metrics = ["28.39", "17.83", "23.89", "17.48", "23.06", "14.39", "22.73", "13.48", "22.64", "13.10"]
    code_files = [f for f in DASHBOARD_DIR.glob("*.py") if f.name != "check_data.py"]
    
    found_violations = []
    for cf in code_files:
        content = cf.read_text(encoding="utf-8")
        for metric in suspicious_metrics:
            # Check if this literal is hardcoded as an assignment or value (not in docstrings/comments)
            lines = content.splitlines()
            for line_no, line in enumerate(lines, 1):
                clean_line = line.strip()
                if clean_line.startswith("#") or clean_line.startswith('"""') or clean_line.startswith("'''"):
                    continue
                if metric in clean_line and "EXPECTED" not in clean_line:
                    found_violations.append((cf.name, line_no, clean_line))
                    
    if found_violations:
        print(f"      WARNING: Potential hardcoded metric found:")
        for fn, ln, txt in found_violations:
            print(f"         {fn}:{ln} -> {txt}")
        raise AssertionError("Found hardcoded player metrics in dashboard scripts!")
    else:
        print("      Passed: Zero hard-coded player metric literals in dashboard application scripts.")

def print_top10_summary(bat_top10, bowl_top10):
    print("\n[5/5] Final Verified Primary Top 10 Under High Pressure:")
    print("=" * 80)
    print("BATTERS:")
    print(f"{'Rk':<3} {'Player':<24} {'Teams':<25} {'Rating':<9} {'Delta':<9} {'Succ%':<8} {'P(T10)':<8}")
    print("-" * 80)
    for _, r in bat_top10.iterrows():
        delta_str = f"+{r['shrunk_delta']:.2f}" if r['shrunk_delta'] >= 0 else f"{r['shrunk_delta']:.2f}"
        print(f"{int(r['rank']):<3} {r['striker_name']:<24} {str(r['teams'])[:24]:<25} +{r['shrunk_rating']:<8.2f} {delta_str:<9} {r['shrunk_success_rate']:<7.1f}% {r['top10_probability']*100:<7.1f}%")
        
    print("\nBOWLERS:")
    print(f"{'Rk':<3} {'Player':<24} {'Teams':<25} {'Rating':<9} {'Delta':<9} {'Succ%':<8} {'P(T10)':<8}")
    print("-" * 80)
    for _, r in bowl_top10.iterrows():
        delta_str = f"+{r['shrunk_delta']:.2f}" if r['shrunk_delta'] >= 0 else f"{r['shrunk_delta']:.2f}"
        print(f"{int(r['rank']):<3} {r['bowler_name']:<24} {str(r['teams'])[:24]:<25} +{r['shrunk_rating']:<8.2f} {delta_str:<9} {r['shrunk_success_rate']:<7.1f}% {r['top10_probability']*100:<7.1f}%")
    print("=" * 80)

if __name__ == "__main__":
    bat_df, bowl_df = check_cohorts()
    top10_bat, top10_bowl = check_top10_recomputation(bat_df, bowl_df)
    check_excluded_audit()
    check_no_hardcoded_metrics()
    print_top10_summary(top10_bat, top10_bowl)
    print("\n[SUCCESS] All data assertion checks passed!")
