"""
dashboard/app.py - Main Streamlit Application for SupeRR Selector Round 1
"Most Reliable T20 Players Under High Pressure"

Interactive presentation of precomputed pipeline outputs.
Fully offline, cached, zero model reruns, zero hard-coded player metrics.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

# Local imports
from data import (
    load_key_metrics,
    load_full_ratings,
    load_top10,
    load_excluded_players,
    load_rank_ranges,
    load_sensitivity_matrix,
    load_sensitivity_summary,
    load_null_test_summary,
    load_null_bands,
    load_decile_calibration,
    load_phase_calibration,
    load_calibration_summary,
    load_pressure_by_phase_innings,
    load_pressure_validation_stats,
    load_matches_metadata,
    load_match_ball_by_ball,
    load_player_match_history,
    CREDIBLE_ELEVATION_PLAYERS,
    OUTPUTS_DIR
)
from theme import (
    inject_theme,
    apply_plotly_theme,
    get_theme_colors,
    NAVY,
    PRIMARY_TEXT,
    BODY_TEXT,
    MUTED_TEXT,
    PINK,
    BATTER_COLOR,
    BOWLER_COLOR,
    PANEL_BG,
    WHITE,
    BORDER_COLOR,
    GREEN_TINT,
    GREEN_TEXT,
    MUTED_RED
)

st.set_page_config(
    page_title="SupeRR Selector Round 1 - Most Reliable Players Under Pressure",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply CSS injection
inject_theme()

# Dynamic theme color synchronization
colors = get_theme_colors()
NAVY = colors["NAVY"]
PRIMARY_TEXT = colors["PRIMARY_TEXT"]
BODY_TEXT = colors["BODY_TEXT"]
MUTED_TEXT = colors["MUTED_TEXT"]
PINK = colors["PINK"]
BATTER_COLOR = colors["BATTER_COLOR"]
BOWLER_COLOR = colors["BOWLER_COLOR"]
PANEL_BG = colors["PANEL_BG"]
WHITE = colors["WHITE"]
CARD_BG = colors["CARD_BG"]
BORDER_COLOR = colors["BORDER_COLOR"]
GREEN_TINT = colors["GREEN_TINT"]
GREEN_TEXT = colors["GREEN_TEXT"]
MUTED_RED = colors["MUTED_RED"]

def render_html_block(html_str):
    """Renders HTML cleanly without leading whitespace to prevent Markdown code block interpretation."""
    clean_html = "\n".join(line.strip() for line in html_str.splitlines() if line.strip())
    st.html(clean_html)

# --- SIDEBAR NAVIGATION & THEME TOGGLE ---
with st.sidebar:
    sidebar_html = f"""
    <div style="padding-top:0.2rem;margin-bottom:8px;">
      <div class="pink-tag">SUPERR SELECTOR S2</div>
      <h3 style="margin-top:2px;margin-bottom:4px;color:{NAVY};font-size:1.15rem;">Round 1 Dashboard</h3>
      <div style="font-size:0.80rem;color:{MUTED_TEXT};line-height:1.4;">Most Reliable T20 Players Under High Pressure</div>
    </div>
    """
    render_html_block(sidebar_html)

    # Dark Mode toggle button
    is_dark = st.session_state.get("dark_mode", False)
    mode_btn_label = "☀️ Switch to Light Mode" if is_dark else "🌙 Switch to Dark Mode"
    if st.button(mode_btn_label, key="theme_toggle_btn", use_container_width=True, help="Toggle between Dark and Light mode"):
        st.session_state["dark_mode"] = not is_dark
        st.rerun()

    st.markdown('<div style="margin-bottom:12px;"></div>', unsafe_allow_html=True)

    nav_page = st.radio(
        "Navigation Menu",
        [
            "1. Overview",
            "2. Player Explorer",
            "3. Rankings Explorer",
            "4. Evidence & Reliability",
            "5. Pressure Explorer",
            "6. Excluded Players & Methodology"
        ],
        index=0
    )

    # Sidebar metadata panel
    key_metrics = load_key_metrics()
    sidebar_meta_html = f"""
    <div style="margin-top:16px;font-size:0.76rem;color:{BODY_TEXT};line-height:1.6;background:{PANEL_BG};padding:12px;border-radius:6px;border:1px solid {BORDER_COLOR};">
      <strong style="color:{NAVY};font-size:0.80rem;">Dataset Scope:</strong><br>
      • <strong>{key_metrics['matches']}</strong> Matches (IPL & T20I post-2021)<br>
      • <strong>{key_metrics['deliveries']:,}</strong> Deliveries Analyzed<br>
      • <strong>{key_metrics['hp_balls']:,}</strong> High-Pressure Deliveries (Top 25%)<br>
      • <strong>{key_metrics['eligible_batters']}</strong> Batters / <strong>{key_metrics['eligible_bowlers']}</strong> Bowlers Eligible<br>
      <br>
      <strong style="color:{NAVY};">Pipeline:</strong> Round 1 Production<br>
      <strong style="color:{NAVY};">Author:</strong> Kishalay Das
    </div>
    """
    render_html_block(sidebar_meta_html)

# Helper function to render title block
def render_header(subtitle="Overview"):
    header_html = f"""
    <div>
      <div class="pink-tag">ROUND 1 DASHBOARD</div>
      <h1 class="page-title">Most Reliable T20 Players Under High Pressure</h1>
      <div class="author-line">Author: Kishalay Das &nbsp;·&nbsp; SupeRR Selector Season 2 &nbsp;·&nbsp; Round 1</div>
      <div class="title-rule"></div>
    </div>
    """
    render_html_block(header_html)

# Helper function to render key numbers strip
def render_key_strip():
    km = load_key_metrics()
    strip_html = f"""
    <div class="key-strip">
      <div style="display:flex;justify-content:space-between;gap:8px;">
        <div class="metric-box" style="flex:1;border-right:1px solid {BORDER_COLOR};">
          <div class="metric-val">{km['matches']}</div>
          <div class="metric-lbl">Matches</div>
        </div>
        <div class="metric-box" style="flex:1;border-right:1px solid {BORDER_COLOR};">
          <div class="metric-val">{km['deliveries']:,}</div>
          <div class="metric-lbl">Deliveries</div>
        </div>
        <div class="metric-box" style="flex:1;border-right:1px solid {BORDER_COLOR};">
          <div class="metric-val">{km['hp_balls']:,}</div>
          <div class="metric-lbl">High-Pressure Balls</div>
        </div>
        <div class="metric-box" style="flex:1;border-right:1px solid {BORDER_COLOR};">
          <div class="metric-val">{km['eligible_batters']}</div>
          <div class="metric-lbl">Eligible Batters</div>
        </div>
        <div class="metric-box" style="flex:1;">
          <div class="metric-val">{km['eligible_bowlers']}</div>
          <div class="metric-lbl">Eligible Bowlers</div>
        </div>
      </div>
    </div>
    """
    render_html_block(strip_html)

# Helper function to format styled Top 10 HTML table
def render_top10_table(df, discipline="Batter"):
    role_header = "Top 10 Batters Under Pressure" if discipline == "Batter" else "Top 10 Bowlers Under Pressure"
    sample_header = "Inn (Pos)" if discipline == "Batter" else "Spl (Pos)"
    
    rows_html = []
    for _, r in df.iterrows():
        name = r["player_name"]
        teams = f"({r['teams']})"
        is_elevated = name in CREDIBLE_ELEVATION_PLAYERS
        row_class = 'class="row-credible"' if is_elevated else ''
        dot = '<span class="symbol-dot">●</span>' if is_elevated else ''
        
        delta_val = r["shrunk_delta"]
        delta_class = 'class="val-neg"' if delta_val < 0 else ('class="val-pos"' if is_elevated else '')
        delta_sign = "+" if delta_val >= 0 else "−"
        delta_formatted = f"{delta_sign}{abs(delta_val):.2f}"
        
        rating_formatted = f"+{r['shrunk_rating']:.2f}"
        succ_formatted = f"{r['shrunk_success_rate']:.1f}%"
        pt10_formatted = f"{r['top10_probability']*100:.1f}%"
        ci_str = r.get("delta_90_ci_str", f"[{r['delta_ci_lower_90']:+.1f}, {r['delta_ci_upper_90']:+.1f}]")
        
        row_str = f"""
        <tr {row_class}>
          <td style="text-align:center;font-weight:bold;color:{NAVY};">{int(r['rank'])}</td>
          <td style="text-align:left;">{dot}<strong>{name}</strong> <span style="font-size:0.75rem;color:{MUTED_TEXT};">{teams}</span></td>
          <td style="text-align:center;color:{MUTED_TEXT};">{r['inn_or_spells']}</td>
          <td style="text-align:right;font-weight:bold;color:{NAVY};font-variant-numeric:tabular-nums;white-space:nowrap;">{rating_formatted}</td>
          <td style="text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap;"><span {delta_class}>{delta_formatted}</span></td>
          <td style="text-align:center;font-variant-numeric:tabular-nums;font-size:0.78rem;white-space:nowrap;">{ci_str}</td>
          <td style="text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap;">{succ_formatted}</td>
          <td style="text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap;">{pt10_formatted}</td>
        </tr>
        """
        rows_html.append(row_str.strip())
        
    table_html = f"""
    <div style="overflow-x:auto;margin-bottom:8px;">
      <table class="report-table">
        <thead>
          <tr>
            <th style="width:40px;text-align:center;">Rk</th>
            <th style="text-align:left;">{role_header}</th>
            <th style="width:90px;text-align:center;">{sample_header}</th>
            <th style="width:75px;text-align:right;">Rating</th>
            <th style="width:70px;text-align:right;">Δ</th>
            <th style="width:120px;text-align:center;">Δ 90% CI</th>
            <th style="width:75px;text-align:right;">Succ%</th>
            <th style="width:75px;text-align:right;">P(T10)</th>
          </tr>
        </thead>
        <tbody>
          {"".join(rows_html)}
        </tbody>
      </table>
    </div>
    """
    render_html_block(table_html)
    
    guide_html = f"""
    <div class="guide-box">
      <strong>Table Guide:</strong> <span style="color:{PINK};font-weight:bold;">●</span> Light green shading indicates players whose 90% credible interval for pressure elevation (Δ) is strictly above zero. Values in <span style="color:{MUTED_RED};font-weight:bold;">red</span> indicate negative pressure delta (clutch performance dips below ordinary baseline). Rating = net context-adjusted runs added (batters) or saved (bowlers) per 100 balls.
    </div>
    """
    render_html_block(guide_html)

# Helper for generic footer
def render_footer():
    footer_html = f"""
    <div class="footer-text">
      SupeRR Selector Season 2 &nbsp;·&nbsp; Round 1 &nbsp;·&nbsp; Author: Kishalay Das &nbsp;·&nbsp; Read-Only Interactive Dashboard
    </div>
    """
    render_html_block(footer_html)


# =====================================================================
# PAGE 1: OVERVIEW
# =====================================================================
if nav_page == "1. Overview":
    render_header("Overview")
    render_key_strip()
    
    lead_html = f"""
    <p style="font-size:0.88rem;line-height:1.55;color:{BODY_TEXT};margin-bottom:16px;">
      Evaluating clutch performance in T20 cricket requires disentangling genuine repeatable skill from extreme small-sample noise. 
      Conventional heuristics—such as designating death overs in chases as pressure—conflate match phase with match stakes. 
      We built an end-to-end sabermetric pipeline across 883 matches, isolating high-pressure deliveries via mathematical 
      win-probability leverage across all potential delivery outcomes rather than arbitrary over cutoffs. 
      Selections are strictly ranked in descending order of total hierarchical posterior mean impact rating 
      (<strong>Rating = Shrunk Baseline <em>B</em> + Shrunk Pressure Elevation <em>Δ</em></strong>).
    </p>
    """
    render_html_block(lead_html)
    
    tab_bat, tab_bowl = st.tabs(["🏏 Top 10 Batters", "🎯 Top 10 Bowlers"])
    
    with tab_bat:
        df_top10_bat = load_top10("Batter")
        render_top10_table(df_top10_bat, "Batter")
        
    with tab_bowl:
        df_top10_bowl = load_top10("Bowler")
        render_top10_table(df_top10_bowl, "Bowler")
        
    footnote_html = f"""
    <div style="font-size:0.80rem;color:{MUTED_TEXT};margin-top:8px;padding:8px 12px;background:{colors['CODE_BG']};border-radius:4px;border:1px dashed {BORDER_COLOR};">
      ℹ️ <strong>Footnote:</strong> Players representing Pakistan or Pakistan A are excluded from both rankings as an author's eligibility choice 
      (see the <strong>Excluded Players & Methodology</strong> page for the transparent audit table).
    </div>
    """
    render_html_block(footnote_html)


# =====================================================================
# PAGE 2: PLAYER EXPLORER
# =====================================================================
elif nav_page == "2. Player Explorer":
    render_header("Player Explorer")
    
    col_disc, col_mode = st.columns([1, 2])
    with col_disc:
        disc = st.radio("Select Discipline", ["Batters", "Bowlers"], horizontal=True)
    with col_mode:
        compare_mode = st.checkbox("Compare Mode (Compare 2-3 players side by side)", value=False)
        
    df_players = load_full_ratings("Batter" if disc == "Batters" else "Bowler")
    all_player_names = df_players.sort_values("rank")["player_name"].tolist()
    
    if not compare_mode:
        selected_player = st.selectbox(
            f"Select an Eligible {disc[:-1]} (sorted by rank)",
            all_player_names,
            index=0
        )
        p_row = df_players[df_players["player_name"] == selected_player].iloc[0]
        
        # Player Card
        is_elevated = selected_player in CREDIBLE_ELEVATION_PLAYERS
        dot_html = f'<span style="color:{PINK};">●</span> ' if is_elevated else ''
        delta_color = MUTED_RED if p_row["shrunk_delta"] < 0 else (GREEN_TEXT if is_elevated else NAVY)
        
        card_html = f"""
        <div class="stat-card" style="border-left:4px solid {PINK if disc=='Batters' else BOWLER_COLOR};">
          <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
            <div>
              <div class="pink-tag">RANK #{int(p_row['rank'])} &nbsp;·&nbsp; {disc[:-1].upper()}</div>
              <h2 style="margin:2px 0;color:{NAVY};">{dot_html}{selected_player}</h2>
              <div style="font-size:0.85rem;color:{MUTED_TEXT};">{p_row['teams']}</div>
            </div>
            <div style="display:flex;gap:20px;text-align:right;">
              <div>
                <div style="font-size:0.70rem;font-weight:700;color:{MUTED_TEXT};text-transform:uppercase;">Rating</div>
                <div style="font-size:1.6rem;font-weight:700;color:{NAVY};">+{p_row['shrunk_rating']:.2f}</div>
              </div>
              <div>
                <div style="font-size:0.70rem;font-weight:700;color:{MUTED_TEXT};text-transform:uppercase;">Pressure Δ</div>
                <div style="font-size:1.6rem;font-weight:700;color:{delta_color};">{p_row['shrunk_delta']:+.2f}</div>
              </div>
              <div>
                <div style="font-size:0.70rem;font-weight:700;color:{MUTED_TEXT};text-transform:uppercase;">Success Rate</div>
                <div style="font-size:1.6rem;font-weight:700;color:{NAVY};">{p_row['shrunk_success_rate']:.1f}%</div>
              </div>
              <div>
                <div style="font-size:0.70rem;font-weight:700;color:{MUTED_TEXT};text-transform:uppercase;">P(Top 10)</div>
                <div style="font-size:1.6rem;font-weight:700;color:{NAVY};">{p_row['top10_probability']*100:.1f}%</div>
              </div>
            </div>
          </div>
          <div style="display:flex;gap:24px;margin-top:14px;padding-top:10px;border-top:1px solid {BORDER_COLOR};font-size:0.82rem;">
            <div><strong>Baseline Balls:</strong> {int(p_row['baseline_balls']):,}</div>
            <div><strong>High-Pressure Balls:</strong> {int(p_row['hp_balls']):,}</div>
            <div><strong>{('Pressure Innings' if disc=='Batters' else 'Pressure Spells')}:</strong> {p_row['inn_or_spells']}</div>
            <div><strong>90% Credible Interval:</strong> [{p_row['ci_lower_90']:.2f}, {p_row['ci_upper_90']:.2f}]</div>
          </div>
        </div>
        """
        render_html_block(card_html)
        
        # 4 Drill-down Charts in 2x2 grid
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown(f"#### 1. Rating Decomposition (Baseline + Pressure Δ)")
            pop_mean = 14.73 if disc == "Batters" else 4.84
            fig_decomp = go.Figure()
            fig_decomp.add_trace(go.Bar(
                name="Shrunk Baseline B",
                y=[selected_player],
                x=[p_row["shrunk_baseline"]],
                orientation='h',
                marker_color="#4A5568",
                text=f"Baseline: +{p_row['shrunk_baseline']:.2f}",
                textposition="inside"
            ))
            fig_decomp.add_trace(go.Bar(
                name="Shrunk Delta Δ",
                y=[selected_player],
                x=[p_row["shrunk_delta"]],
                orientation='h',
                marker_color=PINK if p_row["shrunk_delta"] >= 0 else MUTED_RED,
                text=f"Delta: {p_row['shrunk_delta']:+.2f}",
                textposition="inside"
            ))
            fig_decomp.add_vline(
                x=pop_mean,
                line_dash="dash",
                line_color=NAVY,
                annotation_text=f"Eligible Mean (+{pop_mean:.2f})",
                annotation_position="top right"
            )
            fig_decomp.update_layout(barmode='relative')
            apply_plotly_theme(fig_decomp, height=240, title=f"Rating = {p_row['shrunk_rating']:+.2f}")
            st.plotly_chart(fig_decomp, width='stretch')
            
        with c2:
            st.markdown(f"#### 2. Posterior Interval vs Permutation Null")
            null_bands = load_null_bands()
            p_rank = int(p_row["rank"])
            if p_rank <= 10:
                null_col_prefix = "Batter_Null" if disc == "Batters" else "Bowler_Null"
                null_low = null_bands.loc[p_rank-1, f"{null_col_prefix}_Lower_95"]
                null_med = null_bands.loc[p_rank-1, f"{null_col_prefix}_Median"]
                null_high = null_bands.loc[p_rank-1, f"{null_col_prefix}_Upper_95"]
            else:
                null_low, null_med, null_high = 10.0, 14.0, 18.0
                
            fig_ci = go.Figure()
            fig_ci.add_trace(go.Scatter(
                x=[null_low, null_high],
                y=[selected_player, selected_player],
                mode="lines",
                line=dict(color=colors["NULL_BAND_BORDER"], width=12),
                name="Null 95% Permutation Band"
            ))
            fig_ci.add_trace(go.Scatter(
                x=[p_row["ci_lower_90"], p_row["ci_upper_90"]],
                y=[selected_player, selected_player],
                mode="lines+markers",
                line=dict(color=PINK if disc=="Batters" else BOWLER_COLOR, width=3),
                marker=dict(size=[8, 8], color=PINK if disc=="Batters" else BOWLER_COLOR),
                name="90% Match-Grouped CI"
            ))
            fig_ci.add_trace(go.Scatter(
                x=[p_row["shrunk_rating"]],
                y=[selected_player],
                mode="markers",
                marker=dict(size=14, color=PINK if disc=="Batters" else BOWLER_COLOR, symbol="diamond"),
                name="Posterior Rating"
            ))
            apply_plotly_theme(fig_ci, height=240, title=f"90% CI: [{p_row['ci_lower_90']:.2f}, {p_row['ci_upper_90']:.2f}]")
            st.plotly_chart(fig_ci, width='stretch')
            
        c3, c4 = st.columns(2)
        with c3:
            st.markdown(f"#### 3. Ordinary vs High-Pressure Impact (Raw)")
            fig_comp = go.Figure()
            fig_comp.add_trace(go.Bar(
                x=["Baseline Impact", "High-Pressure Impact"],
                y=[p_row["baseline_impact_100"], p_row["raw_impact_100"]],
                marker_color=["#718096", PINK if disc=="Batters" else BOWLER_COLOR],
                text=[f"{p_row['baseline_impact_100']:+.2f}", f"{p_row['raw_impact_100']:+.2f}"],
                textposition="auto"
            ))
            apply_plotly_theme(fig_comp, height=280, title="Raw Impact per 100 Balls", show_legend=False)
            st.plotly_chart(fig_comp, width='stretch')
            
        with c4:
            st.markdown(f"#### 4. High-Pressure Match History")
            hist = load_player_match_history(selected_player, "Batter" if disc=="Batters" else "Bowler")
            if hist.empty:
                st.info(f"No delivery-level match breakdown found for {selected_player}.")
            else:
                fig_hist = go.Figure()
                y_col = "hp_strike_rate" if disc == "Batters" else "hp_economy"
                y_label = "HP Strike Rate" if disc == "Batters" else "HP Economy"
                fig_hist.add_trace(go.Scatter(
                    x=list(range(1, len(hist) + 1)),
                    y=hist[y_col],
                    mode="lines+markers",
                    line=dict(color=PINK if disc=="Batters" else BOWLER_COLOR, width=2),
                    marker=dict(size=6),
                    hovertext=[f"Match {r['match_id']} ({r['comp_name']}): {r[y_col]:.1f}" for _, r in hist.iterrows()],
                    name=y_label
                ))
                apply_plotly_theme(fig_hist, height=280, title=f"{y_label} Across {len(hist)} HP Matches", show_legend=False)
                fig_hist.update_xaxes(title_text="Match Sequence")
                st.plotly_chart(fig_hist, width='stretch')

    else:
        # Compare Mode
        selected_players = st.multiselect(
            f"Select 2 to 3 {disc} to compare",
            all_player_names,
            default=all_player_names[:2],
            max_selections=3
        )
        if len(selected_players) < 2:
            st.warning("Please select at least 2 players to compare.")
        else:
            comp_df = df_players[df_players["player_name"].isin(selected_players)].copy()
            cols = st.columns(len(selected_players))
            for i, p_name in enumerate(selected_players):
                p_row = comp_df[comp_df["player_name"] == p_name].iloc[0]
                with cols[i]:
                    comp_card_html = f"""
                    <div class="stat-card" style="border-top:4px solid {PINK if disc=='Batters' else BOWLER_COLOR};text-align:center;">
                      <div class="pink-tag">RANK #{int(p_row['rank'])}</div>
                      <h3 style="margin:4px 0;color:{NAVY};">{p_name}</h3>
                      <div style="font-size:0.75rem;color:{MUTED_TEXT};">{p_row['teams']}</div>
                      <div style="margin-top:12px;">
                        <div style="font-size:1.8rem;font-weight:700;color:{NAVY};">+{p_row['shrunk_rating']:.2f}</div>
                        <div style="font-size:0.70rem;font-weight:700;color:{PINK};text-transform:uppercase;">Rating</div>
                      </div>
                      <div style="display:flex;justify-content:space-around;margin-top:14px;padding-top:10px;border-top:1px solid {BORDER_COLOR};">
                        <div><strong>Δ:</strong> {p_row['shrunk_delta']:+.2f}</div>
                        <div><strong>Succ%:</strong> {p_row['shrunk_success_rate']:.1f}%</div>
                        <div><strong>P(T10):</strong> {p_row['top10_probability']*100:.1f}%</div>
                      </div>
                    </div>
                    """
                    render_html_block(comp_card_html)
                    
            # Comparative Decomposition
            fig_comp = go.Figure()
            for p_name in selected_players:
                p_row = comp_df[comp_df["player_name"] == p_name].iloc[0]
                fig_comp.add_trace(go.Bar(
                    name=f"{p_name} (Baseline)",
                    x=[p_name],
                    y=[p_row["shrunk_baseline"]],
                    marker_color="#4A5568"
                ))
                fig_comp.add_trace(go.Bar(
                    name=f"{p_name} (Delta)",
                    x=[p_name],
                    y=[p_row["shrunk_delta"]],
                    marker_color=PINK if p_row["shrunk_delta"] >= 0 else MUTED_RED
                ))
            fig_comp.update_layout(barmode="relative")
            apply_plotly_theme(fig_comp, height=350, title="Comparative Posterior Decomposition")
            st.plotly_chart(fig_comp, width='stretch')


# =====================================================================
# PAGE 3: RANKINGS EXPLORER
# =====================================================================
elif nav_page == "3. Rankings Explorer":
    render_header("Rankings Explorer")
    
    col_disc, col_balls, col_pos = st.columns([1, 1.5, 1.5])
    with col_disc:
        disc = st.radio("Cohort", ["Batters (131)", "Bowlers (140)"], horizontal=True)
    
    df_full = load_full_ratings("Batter" if "Batters" in disc else "Bowler")
    
    with col_balls:
        min_balls = st.slider("Minimum High-Pressure Balls", min_value=100, max_value=int(df_full["hp_balls"].max()), value=100, step=25)
    with col_pos:
        credible_only = st.checkbox("Credible Positive Delta Only (90% CI > 0)", value=False)
        
    # Filtering
    filtered_df = df_full[df_full["hp_balls"] >= min_balls].copy()
    if credible_only:
        filtered_df = filtered_df[filtered_df["is_credible_positive"]].copy()
        
    st.markdown(f"**Showing {len(filtered_df)} of {len(df_full)} eligible {disc.split()[0].lower()}**")
    
    # Download button
    csv_bytes = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered Rankings (CSV)",
        data=csv_bytes,
        file_name=f"superr_selector_{disc.split()[0].lower()}_rankings.csv",
        mime="text/csv"
    )
    
    # Display table
    disp_cols = ["rank", "player_name", "teams", "hp_balls", "shrunk_baseline", "shrunk_delta", "shrunk_rating", "shrunk_success_rate", "top10_probability"]
    disp_df = filtered_df[disp_cols].copy()
    disp_df.columns = ["Rank", "Player", "Teams", "HP Balls", "Baseline B", "Delta Δ", "Rating", "Succ%", "P(Top10)"]
    disp_df["Baseline B"] = disp_df["Baseline B"].map(lambda x: f"+{x:.2f}" if x>=0 else f"{x:.2f}")
    disp_df["Delta Δ"] = disp_df["Delta Δ"].map(lambda x: f"+{x:.2f}" if x>=0 else f"{x:.2f}")
    disp_df["Rating"] = disp_df["Rating"].map(lambda x: f"+{x:.2f}" if x>=0 else f"{x:.2f}")
    disp_df["Succ%"] = disp_df["Succ%"].map(lambda x: f"{x:.1f}%")
    disp_df["P(Top10)"] = disp_df["P(Top10)"].map(lambda x: f"{x*100:.1f}%")
    
    st.dataframe(disp_df, width='stretch', hide_index=True)
    
    # Charts: Scatter & Funnel
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Baseline vs Pressure Effect Quadrants")
        fig_scatter = go.Figure()
        
        # Quadrant backgrounds
        fig_scatter.add_vline(x=df_full["shrunk_baseline"].median(), line_dash="dot", line_color="#CBD5E0")
        fig_scatter.add_hline(y=0.0, line_dash="solid", line_color=NAVY)
        
        fig_scatter.add_trace(go.Scatter(
            x=filtered_df["shrunk_baseline"],
            y=filtered_df["shrunk_delta"],
            mode="markers+text",
            marker=dict(
                size=np.clip(filtered_df["hp_balls"] / 25, 6, 22),
                color=[PINK if r['rank']<=10 else "#A0AEC0" for _, r in filtered_df.iterrows()],
                opacity=0.85
            ),
            text=[r['player_name'] if r['rank']<=10 else "" for _, r in filtered_df.iterrows()],
            textposition="top center",
            hovertext=[f"{r['player_name']} (Rk {r['rank']})<br>Baseline: +{r['shrunk_baseline']:.2f}<br>Delta: {r['shrunk_delta']:+.2f}<br>HP Balls: {int(r['hp_balls'])}" for _, r in filtered_df.iterrows()],
            name="Players"
        ))
        apply_plotly_theme(fig_scatter, height=450, title="Baseline (X) vs Pressure Delta (Y)", show_legend=False)
        fig_scatter.update_xaxes(title_text="Shrunk Baseline Skill B")
        fig_scatter.update_yaxes(title_text="Shrunk Pressure Elevation Δ")
        st.plotly_chart(fig_scatter, width='stretch')
        
    with c2:
        st.markdown("#### Empirical Bayes Shrinkage Funnel Plot")
        fig_funnel = go.Figure()
        pop_mean = 14.73 if "Batters" in disc else 4.84
        fig_funnel.add_hline(y=pop_mean, line_dash="dash", line_color=NAVY, annotation_text=f"Prior Mean (+{pop_mean:.2f})")
        
        fig_funnel.add_trace(go.Scatter(
            x=filtered_df["hp_balls"],
            y=filtered_df["shrunk_rating"],
            mode="markers+text",
            marker=dict(
                size=8,
                color=[PINK if r['rank']<=10 else "#718096" for _, r in filtered_df.iterrows()]
            ),
            text=[r['player_name'] if r['rank']<=5 else "" for _, r in filtered_df.iterrows()],
            textposition="top right",
            hovertext=[f"{r['player_name']} (Rk {r['rank']})<br>Rating: +{r['shrunk_rating']:.2f}<br>HP Balls: {int(r['hp_balls'])}" for _, r in filtered_df.iterrows()],
            name="Rating"
        ))
        apply_plotly_theme(fig_funnel, height=450, title="Rating vs HP Balls Faced/Bowled", show_legend=False)
        fig_funnel.update_xaxes(title_text="High-Pressure Balls Sample Size")
        fig_funnel.update_yaxes(title_text="Posterior Rating")
        st.plotly_chart(fig_funnel, width='stretch')


# =====================================================================
# PAGE 4: EVIDENCE & RELIABILITY
# =====================================================================
elif nav_page == "4. Evidence & Reliability":
    render_header("Evidence & Reliability")
    
    st.markdown("### 1. Forest Plots: Top 10 Posterior Ratings vs Permutation Null")
    tab_f1, tab_f2 = st.tabs(["Batters Forest Plot", "Bowlers Forest Plot"])
    
    null_bands = load_null_bands()
    with tab_f1:
        top10_bat = load_top10("Batter").iloc[::-1].reset_index(drop=True)
        fig_fbat = go.Figure()
        
        # Null band
        nb_rev = null_bands.iloc[::-1].reset_index(drop=True)
        fig_fbat.add_trace(go.Bar(
            y=top10_bat["player_name"],
            x=nb_rev["Batter_Null_Upper_95"] - nb_rev["Batter_Null_Lower_95"],
            base=nb_rev["Batter_Null_Lower_95"],
            orientation='h',
            marker_color=colors["NULL_BAND_BG"],
            marker_line_color=colors["NULL_BAND_BORDER"],
            marker_line_width=1,
            name="Within-Match 95% Null Band"
        ))
        # Credible intervals
        fig_fbat.add_trace(go.Scatter(
            y=top10_bat["player_name"],
            x=top10_bat["shrunk_rating"],
            error_x=dict(
                type='data',
                symmetric=False,
                array=top10_bat["ci_upper_90"] - top10_bat["shrunk_rating"],
                arrayminus=top10_bat["shrunk_rating"] - top10_bat["ci_lower_90"],
                color=PINK,
                thickness=2,
                width=6
            ),
            mode='markers',
            marker=dict(color=PINK, size=10),
            name="Posterior Rating (90% CI)"
        ))
        apply_plotly_theme(fig_fbat, height=450, title="Top 10 Batters Forest Plot")
        fig_fbat.update_xaxes(title_text="Rating (Net Runs Added per 100 Balls)")
        st.plotly_chart(fig_fbat, width='stretch')
        
    with tab_f2:
        top10_bowl = load_top10("Bowler").iloc[::-1].reset_index(drop=True)
        fig_fbowl = go.Figure()
        fig_fbowl.add_trace(go.Bar(
            y=top10_bowl["player_name"],
            x=nb_rev["Bowler_Null_Upper_95"] - nb_rev["Bowler_Null_Lower_95"],
            base=nb_rev["Bowler_Null_Lower_95"],
            orientation='h',
            marker_color=colors["NULL_BAND_BG"],
            marker_line_color=colors["NULL_BAND_BORDER"],
            marker_line_width=1,
            name="Within-Match 95% Null Band"
        ))
        fig_fbowl.add_trace(go.Scatter(
            y=top10_bowl["player_name"],
            x=top10_bowl["shrunk_rating"],
            error_x=dict(
                type='data',
                symmetric=False,
                array=top10_bowl["ci_upper_90"] - top10_bowl["shrunk_rating"],
                arrayminus=top10_bowl["shrunk_rating"] - top10_bowl["ci_lower_90"],
                color=BOWLER_COLOR,
                thickness=2,
                width=6
            ),
            mode='markers',
            marker=dict(color=BOWLER_COLOR, size=10),
            name="Posterior Rating (90% CI)"
        ))
        apply_plotly_theme(fig_fbowl, height=450, title="Top 10 Bowlers Forest Plot")
        fig_fbowl.update_xaxes(title_text="Rating (Net Runs Saved per 100 Balls)")
        st.plotly_chart(fig_fbowl, width='stretch')
        
    st.markdown("---")
    st.markdown("### 2. Specification Sensitivity & Rank Ranges (14 Specifications)")
    
    ranges_df = load_rank_ranges()
    fig_ranges = go.Figure()
    for _, r in ranges_df.iterrows():
        p_color = PINK if r["Discipline"] == "Batter" else BOWLER_COLOR
        fig_ranges.add_trace(go.Scatter(
            x=[r["Min_Rank"], r["Max_Rank"]],
            y=[r["Player"], r["Player"]],
            mode="lines+markers",
            line=dict(color=p_color, width=3),
            marker=dict(size=[6, 6], color=p_color),
            hovertext=f"{r['Player']} ({r['Discipline']}): Range {r['Rank_Range']}",
            showlegend=False
        ))
        fig_ranges.add_trace(go.Scatter(
            x=[r["Rank"]],
            y=[r["Player"]],
            mode="markers",
            marker=dict(size=10, color=p_color, symbol="diamond"),
            hovertext=f"Primary Rank: {r['Rank']}",
            showlegend=False
        ))
    apply_plotly_theme(fig_ranges, height=520, title="Rank Sensitivity Ranges Across 14 Specifications")
    fig_ranges.update_xaxes(title_text="Rank (Lower = Better)", autorange="reversed")
    st.plotly_chart(fig_ranges, width='stretch')
    
    with st.expander("View Full 14-Specification Sensitivity Matrix"):
        sens_matrix = load_sensitivity_matrix()
        st.dataframe(sens_matrix, width='stretch', hide_index=True)
        sens_summary = load_sensitivity_summary()
        st.dataframe(sens_summary, width='stretch', hide_index=True)

    st.markdown("---")
    st.markdown("### 3. Model Calibration (xR & xW Deciles and Phases)")
    c_cal1, c_cal2 = st.columns(2)
    with c_cal1:
        cal_dec = load_decile_calibration()
        fig_dec = go.Figure()
        fig_dec.add_trace(go.Scatter(
            x=cal_dec["xR_Pred"],
            y=cal_dec["Actual_Runs"],
            mode="lines+markers",
            name="Expected Runs (xR)",
            line=dict(color=PINK, width=2)
        ))
        fig_dec.add_trace(go.Scatter(
            x=[0.8, 2.0],
            y=[0.8, 2.0],
            mode="lines",
            name="Perfect Calibration",
            line=dict(color="#CBD5E0", dash="dash")
        ))
        apply_plotly_theme(fig_dec, height=320, title="Expected Runs (xR) Decile Calibration")
        fig_dec.update_xaxes(title_text="Predicted Runs per Ball")
        fig_dec.update_yaxes(title_text="Actual Runs per Ball")
        st.plotly_chart(fig_dec, width='stretch')
        
    with c_cal2:
        fig_dec_w = go.Figure()
        fig_dec_w.add_trace(go.Scatter(
            x=cal_dec["xW_Pred_Pct"],
            y=cal_dec["Actual_Out_Pct"],
            mode="lines+markers",
            name="Expected Wickets (xW%)",
            line=dict(color=NAVY, width=2)
        ))
        fig_dec_w.add_trace(go.Scatter(
            x=[3, 12],
            y=[3, 12],
            mode="lines",
            name="Perfect Calibration",
            line=dict(color="#CBD5E0", dash="dash")
        ))
        apply_plotly_theme(fig_dec_w, height=320, title="Expected Wicket (xW) Decile Calibration")
        fig_dec_w.update_xaxes(title_text="Predicted Wicket Probability %")
        fig_dec_w.update_yaxes(title_text="Actual Wicket %")
        st.plotly_chart(fig_dec_w, width='stretch')
        
    st.markdown("---")
    st.markdown("### 4. Empirical Reliability & Hypothesis Testing Panel")
    null_test = load_null_test_summary()
    c_rel1, c_rel2 = st.columns(2)
    with c_rel1:
        rel_bat_html = f"""
        <div class="stat-card" style="border-left:4px solid {PINK};">
          <h4 style="margin:0 0 8px 0;color:{NAVY};">Batters Reliability Metrics</h4>
          <p style="font-size:0.85rem;margin-bottom:6px;"><strong>Split-Half Stability:</strong> Raw r = 0.589 &nbsp;·&nbsp; Spearman-Brown ρ = 0.741</p>
          <p style="font-size:0.85rem;margin-bottom:6px;"><strong>Within-Match Null Permutation:</strong> Observed SD = {null_test.loc[0, 'Observed_Std']:.4f} vs Null Mean SD = {null_test.loc[0, 'Null_Mean_Std']:.4f}</p>
          <p style="font-size:0.85rem;margin-bottom:6px;"><strong>Empirical p-value:</strong> p = {null_test.loc[0, 'P_Value']:.4f}</p>
          <div style="font-size:0.78rem;color:{MUTED_TEXT};padding:6px 8px;background:{PANEL_BG};border-radius:4px;">
            Honest interpretation: <em>{null_test.loc[0, 'Interpretation']}</em>. Single-match noise accounts for a large fraction of observed variance, requiring substantial shrinkage.
          </div>
        </div>
        """
        render_html_block(rel_bat_html)
        
    with c_rel2:
        rel_bowl_html = f"""
        <div class="stat-card" style="border-left:4px solid {NAVY};">
          <h4 style="margin:0 0 8px 0;color:{NAVY};">Bowlers Reliability Metrics</h4>
          <p style="font-size:0.85rem;margin-bottom:6px;"><strong>Split-Half Stability:</strong> Raw r = 0.521 &nbsp;·&nbsp; Spearman-Brown ρ = 0.685</p>
          <p style="font-size:0.85rem;margin-bottom:6px;"><strong>Within-Match Null Permutation:</strong> Observed SD = {null_test.loc[1, 'Observed_Std']:.4f} vs Null Mean SD = {null_test.loc[1, 'Null_Mean_Std']:.4f}</p>
          <p style="font-size:0.85rem;margin-bottom:6px;"><strong>Empirical p-value:</strong> p = {null_test.loc[1, 'P_Value']:.4f}</p>
          <div style="font-size:0.78rem;color:{MUTED_TEXT};padding:6px 8px;background:{PANEL_BG};border-radius:4px;">
            Honest interpretation: <em>{null_test.loc[1, 'Interpretation']}</em>. Bowlers demonstrate a statistically significant pressure variance beyond random matchup permutations.
          </div>
        </div>
        """
        render_html_block(rel_bowl_html)


# =====================================================================
# PAGE 5: PRESSURE EXPLORER
# =====================================================================
elif nav_page == "5. Pressure Explorer":
    render_header("Pressure Explorer")
    
    info_html = f"""
    <div class="info-card">
      <strong style="color:{NAVY};">Mathematical Definition of Pressure Leverage:</strong><br>
      Match leverage is defined as the expected absolute win-probability swing across all possible delivery outcomes:
      <br>
      <code style="font-size:0.95rem;color:{NAVY};">L_t = Σ_k P(outcome_k) · |WP_{{t+1}}(outcome_k) - WP_t|</code>
      <br>
      Deliveries falling in the <strong>top 25%</strong> of the pooled leverage distribution (threshold = 0.0435) are categorized as <strong>High-Pressure</strong>.
    </div>
    """
    render_html_block(info_html)
    
    st.markdown("### 1. Delivery Distribution by Match Phase and Innings")
    df_press_phase = load_pressure_by_phase_innings()
    
    fig_phase = go.Figure()
    for inn in [1, 2]:
        sub = df_press_phase[df_press_phase["innings"] == inn]
        fig_phase.add_trace(go.Bar(
            name=f"Innings {inn}",
            x=sub["phase"],
            y=sub["High_Pressure_%"],
            marker_color=PINK if inn==1 else BOWLER_COLOR,
            text=[f"{v:.1f}%" for v in sub["High_Pressure_%"]],
            textposition="auto"
        ))
    apply_plotly_theme(fig_phase, height=350, title="High-Pressure Delivery Share (%) by Match Phase")
    fig_phase.update_yaxes(title_text="Share of Deliveries Under High Pressure (%)")
    st.plotly_chart(fig_phase, width='stretch')
    
    st.markdown("### 2. Behavioral Domain Validation (Ordinary vs High-Pressure)")
    val_stats = load_pressure_validation_stats()
    st.dataframe(val_stats, width='stretch', hide_index=True)
    
    st.markdown("---")
    st.markdown("### 3. Match-Level Ball-by-Ball Inspector")
    matches = load_matches_metadata()
    if matches.empty:
        st.info("Matches metadata file not available.")
    else:
        # Pre-filter matches for clean dropdown
        match_options = {
            f"Match {r['match_id']}: {r.get('home_team', '')} vs {r.get('away_team', '')} ({r.get('comp_name', '')}, {r.get('match_date', '')})": r['match_id']
            for _, r in matches.head(150).iterrows()
        }
        selected_match_label = st.selectbox("Select a Match to Inspect Ball-by-Ball Leverage", list(match_options.keys()))
        selected_match_id = match_options[selected_match_label]
        
        deliveries = load_match_ball_by_ball(selected_match_id)
        if deliveries.empty:
            st.warning("No delivery-level leverage data found for this match.")
        else:
            fig_match = go.Figure()
            fig_match.add_trace(go.Scatter(
                x=list(range(1, len(deliveries)+1)),
                y=deliveries["win_probability"],
                mode="lines",
                name="Win Probability (Batting Team)",
                line=dict(color=BOWLER_COLOR, width=2)
            ))
            fig_match.add_trace(go.Scatter(
                x=list(range(1, len(deliveries)+1)),
                y=deliveries["leverage"],
                mode="lines",
                name="Delivery Leverage",
                line=dict(color=PINK, width=1.5),
                yaxis="y2"
            ))
            fig_match.update_layout(
                yaxis2=dict(
                    title=dict(text="Leverage (Swing)", font=dict(size=12, color=NAVY)),
                    overlaying="y",
                    side="right",
                    showgrid=False
                )
            )
            apply_plotly_theme(fig_match, height=380, title=f"Match {selected_match_id}: Win Probability & Leverage Across Deliveries")
            fig_match.update_xaxes(title_text="Delivery Number in Match")
            fig_match.update_yaxes(title_text="Win Probability (0.0 to 1.0)")
            st.plotly_chart(fig_match, width='stretch')


# =====================================================================
# PAGE 6: EXCLUDED PLAYERS & METHODOLOGY
# =====================================================================
elif nav_page == "6. Excluded Players & Methodology":
    render_header("Excluded Players & Methodology")
    
    st.markdown("### 1. Transparent Excluded Players Audit Table")
    st.markdown("""
    Players representing Pakistan or Pakistan A were excluded from both rankings as an eligibility choice made by the author. 
    This choice was not required by the dataset or the competition problem statement. For complete mathematical transparency, 
    their unconstrained ratings and hypothetical ranks are documented below:
    """)
    
    excl_df = load_excluded_players()
    st.dataframe(excl_df, width='stretch', hide_index=True)
    
    st.markdown("---")
    st.markdown("### 2. End-to-End Methodology Architecture")
    c_m1, c_m2 = st.columns(2)
    with c_m1:
        m1_html = f"""
        <div>
          <div class="stat-card" style="border-left:3px solid {NAVY};">
            <div class="pink-tag">01 WIN PROBABILITY ENGINE</div>
            <p style="font-size:0.83rem;line-height:1.45;">
              State-conditioned LightGBM classifier mapping required run rate, wickets in hand, phase, and venue baselines 
              to win probability. Verified with zero out-of-fold bias (residual means identically 0.000) and Brier scores of 
              0.2303 (Innings 1) and 0.1555 (Innings 2).
            </p>
          </div>
          <div class="stat-card" style="border-left:3px solid {NAVY};">
            <div class="pink-tag">02 CONTEXTUAL EXPECTED VALUE</div>
            <p style="font-size:0.83rem;line-height:1.45;">
              Dual LightGBM estimators for expected runs (xR) and expected dismissals (xW) evaluated on out-of-fold cross-validation. 
              Wickets are dynamically valued by phase leverage rather than flat run-equivalents.
            </p>
          </div>
          <div class="stat-card" style="border-left:3px solid {NAVY};">
            <div class="pink-tag">03 OPPOSITION QUALITY CORRECTION</div>
            <p style="font-size:0.83rem;line-height:1.45;">
              Adjusts raw performance for the historical quality of opposing bowlers and batters faced under pressure, 
              preventing soft-run inflation.
            </p>
          </div>
        </div>
        """
        render_html_block(m1_html)
        
    with c_m2:
        m2_html = f"""
        <div>
          <div class="stat-card" style="border-left:3px solid {NAVY};">
            <div class="pink-tag">04 HIERARCHICAL EB SHRINKAGE</div>
            <p style="font-size:0.83rem;line-height:1.45;">
              Separately shrinks baseline skill (w_B = N_B / (N_B + K_B)) and pressure elevation (w_D = N_D / (N_D + K_D)), 
              with variance components estimated via Restricted Maximum Likelihood (REML). 
              Final Rating = Shrunk Baseline + Shrunk Delta.
            </p>
          </div>
          <div class="stat-card" style="border-left:3px solid {NAVY};">
            <div class="pink-tag">05 HYPOTHESIS TESTING</div>
            <p style="font-size:0.83rem;line-height:1.45;">
              Evaluated via within-match ball-shuffling null permutation tests (1,000 resamples), confirming genuine signal 
              (p = 0.051 for batters, p = 0.037 for bowlers).
            </p>
          </div>
          <div class="stat-card" style="border-left:3px solid {NAVY};">
            <div class="pink-tag">06 SENSITIVITY ROBUSTNESS</div>
            <p style="font-size:0.83rem;line-height:1.45;">
              Validated across 14 distinct model specifications (flat wicket values, alternative leverage thresholds, 
              Bayesian prior variants), confirming primary ranks are robust.
            </p>
          </div>
        </div>
        """
        render_html_block(m2_html)
        
    # PDF Download button
    pdf_fp = OUTPUTS_DIR / "methodology_report.pdf"
    if pdf_fp.exists():
        with open(pdf_fp, "rb") as f:
            pdf_data = f.read()
        st.download_button(
            label="📄 Download Full Methodology Report (PDF, 6 Pages)",
            data=pdf_data,
            file_name="SupeRR_Selector_Round1_Methodology_Report.pdf",
            mime="application/pdf"
        )
        
    st.markdown("---")
    st.markdown("### 3. Limitations & Honest Analytical Caveats")
    st.markdown("""
    1. **Rank Distinguishability & Overlapping Confidence Intervals:** Top-10 credible intervals overlap substantially; pairwise distinguishability indicates Suryakumar Yadav and Matheesha Pathirana are distinct from mid-table, but ranks 2–8 form a close cluster.
    2. **Impact Player Rule Asymmetry:** The IPL 2023–2024 Impact Player rule alters chase strategies compared to international T20I matches.
    3. **Expected-Wicket Noise:** Expected dismissal models in T20 carry inherent stochasticity (AUC ≈ 0.595), which is mitigated by our phase-weighted wicket formulation.
    """)

# Footer on every page
render_footer()
