"""
upload_pipeline.py - Sequentially commits and pushes files one by one to GitHub.
Each file gets an individual commit message and is pushed to origin main so it
registers as individual contribution history on GitHub.
"""
import subprocess
import os
import sys
import time

COMMIT_SEQUENCE = [
    # 1. Root configuration & build
    ("requirements.txt", "build: add project dependencies (streamlit, plotly, pandas, numpy)"),
    (".streamlit/config.toml", "chore: configure streamlit light theme and minimal toolbar"),
    ("run_all.py", "ci: add end-to-end sabermetric pipeline runner script"),
    ("README.md", "docs: add comprehensive project methodology and execution README"),

    # 2. Source code pipeline (src/)
    ("src/config.py", "feat(src): add global project configuration and path constants"),
    ("src/match_state.py", "feat(src): implement state-conditioned win probability feature engineering"),
    ("src/expected_value.py", "feat(src): implement dual expected runs (xR) and wickets (xW) LightGBM models"),
    ("src/pressure_model.py", "feat(src): implement win-probability leverage and pressure definition"),
    ("src/player_metrics.py", "feat(src): calculate raw and contextual performance metrics across phases"),
    ("src/fair_comparison.py", "feat(src): implement hierarchical empirical Bayes shrinkage and rating formula"),
    ("src/reliability.py", "feat(src): implement split-half reliability and within-match permutation tests"),
    ("src/visualizations.py", "feat(src): add core data visualization helper functions"),
    ("src/generate_report_figures.py", "feat(src): add publication chart generators (forest plots, rank ranges)"),
    ("src/generate_clean_charts.py", "feat(src): add chart generation utilities for pipeline"),
    ("src/data_audit.py", "feat(src): add delivery-level data reconciliation and validation audit"),
    ("src/export_report_pdf.py", "feat(src): add ReportLab publication report exporter"),
    ("src/export_report_html.py", "feat(src): add publication HTML to PDF exporter with Playwright"),
    ("src/build_notebook.py", "feat(src): add automated Jupyter notebook generator from pipeline"),
    ("src/qa_verification.py", "test(src): add automated QA verification suite"),
    ("src/qa_reference_compare.py", "test(src): add reference comparison test script"),

    # 3. Interactive Dashboard (dashboard/)
    ("dashboard/theme.py", "feat(dashboard): add custom CSS and Plotly layout formatting"),
    ("dashboard/data.py", "feat(dashboard): add cached offline data-loading module"),
    ("dashboard/check_data.py", "test(dashboard): add data assertion suite verifying ratings and cohorts"),
    ("dashboard/qa_dashboard.py", "test(dashboard): add Playwright automated UI and responsiveness test runner"),
    ("dashboard/README.md", "docs(dashboard): add dashboard architecture and run instructions"),
    ("dashboard/app.py", "feat(dashboard): implement 6-page interactive Streamlit dashboard application"),

    # 4. Notebooks
    ("notebooks/SupeRR_Selector_Methodology_Notebook.ipynb", "docs(notebooks): add complete runnable methodology and analytical notebook"),

    # 5. Report deliverables
    ("report/methodology_report.md", "docs(report): add complete methodology report in Markdown"),
    ("report/methodology_report.pdf", "docs(report): add publication-grade 6-page methodology report PDF"),
    ("report/methodology_report_old.pdf", "docs(report): add prior revision baseline PDF"),

    # 6. Primary outputs (CSVs)
    ("outputs/final_top10_batters.csv", "data(outputs): add primary Top 10 Batters under pressure dataset"),
    ("outputs/final_top10_bowlers.csv", "data(outputs): add primary Top 10 Bowlers under pressure dataset"),
    ("outputs/full_ratings_batters.csv", "data(outputs): add full ratings for all 131 eligible batters"),
    ("outputs/full_ratings_bowlers.csv", "data(outputs): add full ratings for all 140 eligible bowlers"),
    ("outputs/excluded_pakistan_players.csv", "data(outputs): add transparent audit table for excluded Pakistan players"),
    ("outputs/top10_rank_ranges.csv", "data(outputs): add rank ranges across 14 specifications"),
    ("outputs/top10_sensitivity_matrix.csv", "data(outputs): add sensitivity matrix across 14 specifications"),
    ("outputs/sensitivity_analysis.csv", "data(outputs): add Jaccard overlap summary across specifications"),
    ("outputs/null_test_summary.csv", "data(outputs): add permutation test summary statistics and p-values"),
    ("outputs/null_top10_bands.csv", "data(outputs): add 95% permutation null bands for top 10 ranks"),
    ("outputs/decile_calibration_xR_xW.csv", "data(outputs): add decile calibration predictions and actuals"),
    ("outputs/expected_vs_actual_by_phase.csv", "data(outputs): add phase-level calibration statistics"),
    ("outputs/calibration_summary.csv", "data(outputs): add residual calibration summary statistics"),
    ("outputs/pressure_by_phase_innings.csv", "data(outputs): add pressure delivery share by phase and innings"),
    ("outputs/pressure_validation_stats.csv", "data(outputs): add behavioral domain validation statistics"),
    ("outputs/clean_deliveries_sample.csv", "data(outputs): add sample clean deliveries dataset"),
    ("outputs/data_exclusion_log.csv", "data(outputs): add data exclusion audit log"),
    ("outputs/hp_wicket_comparison.csv", "data(outputs): add wicket formulation comparison metrics"),
    ("outputs/opposition_audit_top10.csv", "data(outputs): add opposition quality audit dataset"),
    ("outputs/opposition_sensitivity_batters.csv", "data(outputs): add opposition sensitivity dataset for batters"),
    ("outputs/opposition_sensitivity_bowlers.csv", "data(outputs): add opposition sensitivity dataset for bowlers"),
    ("outputs/pairwise_probabilities_batters.csv", "data(outputs): add pairwise distinguishability probabilities for batters"),
    ("outputs/pairwise_probabilities_bowlers.csv", "data(outputs): add pairwise distinguishability probabilities for bowlers"),
    ("outputs/phase_vs_flat_comparison_batters.csv", "data(outputs): add phase vs flat valuation comparison for batters"),
    ("outputs/phase_vs_flat_comparison_bowlers.csv", "data(outputs): add phase vs flat valuation comparison for bowlers"),
    ("outputs/raw_player_metrics_batters.csv", "data(outputs): add raw performance metrics for all batters"),
    ("outputs/raw_player_metrics_bowlers.csv", "data(outputs): add raw performance metrics for all bowlers"),
    ("outputs/sanity_table_famous_batters.csv", "data(outputs): add famous batter benchmark diagnostics"),
    ("outputs/sanity_table_famous_bowlers.csv", "data(outputs): add famous bowler benchmark diagnostics"),
    ("outputs/shrinkage_verification_table.csv", "data(outputs): add empirical Bayes shrinkage calculation audit"),
    ("outputs/top10_batters_flat.csv", "data(outputs): add flat-specification top 10 batters"),
    ("outputs/top10_bowlers_flat.csv", "data(outputs): add flat-specification top 10 bowlers"),
    ("outputs/top10_clutch_constrained_batters.csv", "data(outputs): add clutch-constrained top 10 batters"),
    ("outputs/top10_clutch_constrained_bowlers.csv", "data(outputs): add clutch-constrained top 10 bowlers"),
    ("outputs/top10_pure_clutch_batters.csv", "data(outputs): add pure-clutch top 10 batters"),
    ("outputs/top10_pure_clutch_bowlers.csv", "data(outputs): add pure-clutch top 10 bowlers"),
    ("outputs/top20_bowlers_wicket_specs.csv", "data(outputs): add top 20 bowlers across wicket value specifications"),
    ("outputs/wicket_value_sensitivity.csv", "data(outputs): add wicket value sensitivity analysis"),
    ("outputs/schema_notes.md", "docs(outputs): add schema documentation notes"),
    ("outputs/methodology_report.pdf", "docs(outputs): add methodology report PDF artifact"),
    ("outputs/methodology_report_KishalayDas.pdf", "docs(outputs): add methodology report named PDF artifact"),
    ("outputs/methodology_report_old.pdf", "docs(outputs): add methodology report baseline PDF artifact"),

    # 7. Output figures & fonts
    ("outputs/pipeline_diagram.png", "assets(outputs): add pipeline architecture diagram"),
    ("outputs/expected_value_calibration_deciles_phases.png", "assets(outputs): add expected value calibration multi-panel figure"),
    ("outputs/stacked_decomposition_chart.png", "assets(outputs): add posterior rating stacked decomposition chart"),
    ("outputs/forest_plot_batters.png", "assets(outputs): add top 10 batters forest plot"),
    ("outputs/forest_plot_bowlers.png", "assets(outputs): add top 10 bowlers forest plot"),
    ("outputs/rank_ranges_chart.png", "assets(outputs): add 14-specification rank ranges sensitivity plot"),
    ("outputs/baseline_vs_pressure_scatter.png", "assets(outputs): add baseline vs pressure delta quadrant scatter plot"),
    ("outputs/rating_vs_samplesize_funnel.png", "assets(outputs): add empirical Bayes shrinkage funnel plot"),
    ("outputs/pressure_by_phase_heatmap.png", "assets(outputs): add leverage distribution by phase heatmap"),
    ("outputs/splithalf_correlation.png", "assets(outputs): add split-half reliability correlation plot"),
    ("outputs/win_probability_calibration.png", "assets(outputs): add win probability calibration curve"),
    ("outputs/rank_stability_heatmap.png", "assets(outputs): add rank stability heatmap"),
    ("outputs/pressure_vs_ordinary_comparison.png", "assets(outputs): add pressure vs ordinary domain comparison figure"),

    # 8. Raw & Reference Data
    ("data/competitions.csv", "data(raw): add competitions metadata"),
    ("data/teams.csv", "data(raw): add teams directory"),
    ("data/matches.csv", "data(raw): add matches dataset (883 matches)"),
    ("data/playing_eleven.csv", "data(raw): add match playing elevens dataset"),
    ("data/competition_team_player_mapping.csv", "data(raw): add competition team player directory"),
    ("data/ball_by_ball.csv", "data(raw): add raw ball-by-ball delivery log"),
    ("data/master_clean_deliveries.csv", "data(processed): add cleaned delivery-level match dataset"),
    ("data/master_with_match_state.csv", "data(processed): add state-engineered delivery dataset")
]

def run_git(args):
    result = subprocess.run(["git"] + args, capture_output=True, text=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()

def upload_all():
    print(f"[*] Starting individual file-by-file commit sequence ({len(COMMIT_SEQUENCE)} files)...")
    success_count = 0
    
    for i, (rel_path, msg) in enumerate(COMMIT_SEQUENCE, 1):
        if not os.path.exists(rel_path):
            print(f"[{i}/{len(COMMIT_SEQUENCE)}] Skipping missing: {rel_path}")
            continue
            
        # Add single file
        code, out, err = run_git(["add", rel_path])
        if code != 0:
            print(f"[{i}/{len(COMMIT_SEQUENCE)}] Error adding {rel_path}: {err}")
            continue
            
        # Commit single file
        code, out, err = run_git(["commit", "-m", msg])
        if code != 0:
            if "nothing to commit" in out or "nothing to commit" in err:
                print(f"[{i}/{len(COMMIT_SEQUENCE)}] Already up to date: {rel_path}")
            else:
                print(f"[{i}/{len(COMMIT_SEQUENCE)}] Commit error on {rel_path}: {err}")
            continue
            
        print(f"[{i}/{len(COMMIT_SEQUENCE)}] Committed: {rel_path} -> '{msg}'")
        success_count += 1
        
    # Also add remaining untracked assets (fonts, dashboard screens, inspect images) in small batches
    print("\n[*] Checking for remaining asset files (fonts, screenshots, inspect images)...")
    status_code, status_out, _ = run_git(["status", "--porcelain"])
    remaining = [line[3:].strip() for line in status_out.splitlines() if line.strip()]
    
    for item in remaining:
        # Strip quotes if present
        clean_item = item.strip('"')
        if not os.path.exists(clean_item):
            continue
        msg = f"assets: add {clean_item}"
        run_git(["add", clean_item])
        c_code, _, _ = run_git(["commit", "-m", msg])
        if c_code == 0:
            print(f"    Committed asset: {clean_item}")
            success_count += 1
            
    print(f"\n[+] Created {success_count} individual commits!")
    print("[*] Pushing all commits to remote https://github.com/bhaikd/rajasthanroyals.git (origin main)...")
    push_code, push_out, push_err = run_git(["push", "origin", "main"])
    if push_code == 0:
        print("[SUCCESS] All files successfully uploaded to GitHub repository!")
        print(push_out)
        return True
    else:
        print(f"[ERROR] Push failed: {push_err}")
        return False

if __name__ == "__main__":
    ok = upload_all()
    sys.exit(0 if ok else 1)
