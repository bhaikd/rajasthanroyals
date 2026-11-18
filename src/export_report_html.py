"""
export_report_html.py - Publication-Grade HTML+CSS to PDF Methodology Report Generator

Builds a restyled 7-page methodology report visually matching the SupeRR Selector problem-statement aesthetic:
- US Letter format with generous ~22 mm white margins.
- Clean geometric typography using embedded Montserrat fonts.
- Navy (#021D45), pink (#E50695), and light grey-blue (#F5F6FA) shaded info boxes.
- Full-width stacked top-10 tables with light grey-blue headers and pink bold uppercase labels.
- Zero-loss preservation of all analytical numbers, rankings, intervals, and empirical claims.
- Exports to PDF via Playwright/Chromium and syncs to report/.
"""
import os
import sys
import base64
import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = BASE_DIR / "outputs"
REPORT_DIR = BASE_DIR / "report"
FONTS_DIR = OUTPUTS_DIR / "fonts"

def get_base64_font(font_filename):
    """Encodes a TTF font file to a base64 Data URI."""
    fp = FONTS_DIR / font_filename
    if not fp.exists():
        raise FileNotFoundError(f"Font not found: {fp}")
    with open(fp, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    return f"data:font/truetype;charset=utf-8;base64,{encoded}"

def get_base64_image(image_name):
    """Encodes an image file to a base64 Data URI."""
    img_path = OUTPUTS_DIR / image_name
    if not img_path.exists():
        raise FileNotFoundError(f"Image not found: {img_path}")
    with open(img_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"

def build_html_content():
    """Constructs the complete semantic HTML report matching the problem-statement aesthetic."""
    # Load fonts
    font_reg = get_base64_font("Montserrat-Regular.ttf")
    font_med = get_base64_font("Montserrat-Medium.ttf")
    font_semi = get_base64_font("Montserrat-SemiBold.ttf")
    font_bold = get_base64_font("Montserrat-Bold.ttf")
    font_italic = get_base64_font("Montserrat-Italic.ttf")

    # Load images
    img_pipeline = get_base64_image("pipeline_diagram.png")
    img_cal = get_base64_image("expected_value_calibration_deciles_phases.png")
    img_stacked = get_base64_image("stacked_decomposition_chart.png")
    img_forest_bat = get_base64_image("forest_plot_batters.png")
    img_forest_bowl = get_base64_image("forest_plot_bowlers.png")
    img_ranges = get_base64_image("rank_ranges_chart.png")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>SupeRR Selector Season 2 – Round 1 Methodology Report</title>
  <style>
    @font-face {{
      font-family: 'Montserrat';
      src: url('{font_reg}') format('truetype');
      font-weight: 400;
      font-style: normal;
    }}
    @font-face {{
      font-family: 'Montserrat';
      src: url('{font_med}') format('truetype');
      font-weight: 500;
      font-style: normal;
    }}
    @font-face {{
      font-family: 'Montserrat';
      src: url('{font_semi}') format('truetype');
      font-weight: 600;
      font-style: normal;
    }}
    @font-face {{
      font-family: 'Montserrat';
      src: url('{font_bold}') format('truetype');
      font-weight: 700;
      font-style: normal;
    }}
    @font-face {{
      font-family: 'Montserrat';
      src: url('{font_italic}') format('truetype');
      font-weight: 400;
      font-style: italic;
    }}

    @page {{
      size: letter portrait;
    }}

    *, *:before, *:after {{
      box-sizing: border-box;
    }}

    body {{
      font-family: 'Montserrat', -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
      font-size: 8.4pt;
      line-height: 1.35;
      color: #1F2A44;
      margin: 0;
      padding: 0;
      background-color: #FFFFFF;
      -webkit-font-smoothing: antialiased;
    }}

    .page {{
      padding: 0;
      margin: 0;
    }}

    

    /* Title Block */
    .top-tag {{
      font-size: 9.2pt;
      font-weight: 700;
      color: #E50695;
      text-transform: uppercase;
      letter-spacing: 0.8px;
      margin-bottom: 5px;
    }}

    .main-title {{
      font-size: 19.5pt;
      font-weight: 700;
      line-height: 1.14;
      color: #021D45;
      margin: 0 0 3px 0;
      letter-spacing: -0.3px;
    }}

    .author-line {{
      font-size: 8.4pt;
      font-weight: 500;
      color: #606F89;
      margin-bottom: 4px;
    }}

    .title-divider {{
      border-bottom: 1px solid #E2E6EE;
      margin-bottom: 4px;
    }}

    /* Shaded Info Boxes (Reference Style) */
    .info-box {{
      background-color: #F5F6FA;
      border-radius: 4px;
      padding: 4px 6px;
      margin-bottom: 5px;
      break-inside: avoid;
    }}

    .key-metrics-grid {{
      display: flex;
      justify-content: space-between;
      gap: 8px;
    }}
    .key-metric-item {{
      flex: 1;
      text-align: center;
      border-right: 1px solid #E2E6EE;
      padding: 2px 4px;
    }}
    .key-metric-item:last-child {{
      border-right: none;
    }}
    .metric-number {{
      font-size: 10.5pt;
      font-weight: 700;
      color: #021D45;
      font-variant-numeric: tabular-nums;
      display: block;
      line-height: 1.15;
    }}
    .metric-label {{
      font-size: 6.5pt;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.3px;
      color: #E50695;
      margin-top: 1px;
      display: block;
    }}

    /* Method At A Glance 2-Column Grid Box (Page 1) */
    .submission-box {{
      background-color: #F5F6FA;
      border-radius: 4px;
      padding: 4px 6px;
      margin-top: 4px;
      margin-bottom: 2px;
      break-inside: avoid;
    }}
    .submission-box-header {{
      font-size: 8.0pt;
      font-weight: 700;
      color: #021D45;
      margin-bottom: 2px;
      display: flex;
      justify-content: space-between;
      align-items: baseline;
    }}
    .submission-box-subheader {{
      font-size: 6.6pt;
      color: #606F89;
      font-weight: 400;
    }}
    .submission-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      column-gap: 8px;
      row-gap: 2px;
    }}
    .submission-item {{
      display: flex;
      align-items: flex-start;
      font-size: 6.4pt;
      line-height: 1.14;
    }}
    .submission-col-label {{
      width: 78px;
      flex-shrink: 0;
      font-size: 5.9pt;
      font-weight: 700;
      color: #E50695;
      text-transform: uppercase;
      letter-spacing: 0.2px;
      padding-top: 0.5px;
    }}
    .submission-col-text {{
      flex-grow: 1;
      color: #1F2A44;
    }}

    /* Section Typography */
    .section-tag {{
      font-size: 7.0pt;
      font-weight: 700;
      color: #E50695;
      text-transform: uppercase;
      letter-spacing: 0.8px;
      margin-top: 5px;
      margin-bottom: 1px;
      break-after: avoid;
      break-after: avoid;
    }}
    h2.section-title {{
      font-size: 11.8pt;
      font-weight: 700;
      color: #021D45;
      margin: 0 0 3px 0;
      break-after: avoid;
      letter-spacing: -0.2px;
      break-after: avoid;
    }}
    h3.sub-title {{
      font-size: 9.6pt;
      font-weight: 700;
      color: #021D45;
      margin: 6px 0 2px 0;
      break-after: avoid;
      break-after: avoid;
    }}

    p {{
      margin: 0 0 3.5px 0;
      text-align: left;
      orphans: 3;
      widows: 3;
    }}

    /* Bullets with small pink dot markers */
    ul.styled-list {{
      list-style: none;
      margin: 2px 0 3.5px 0;
      padding-left: 0;
    }}
    ul.styled-list li {{
      orphans: 3;
      widows: 3;
      position: relative;
      padding-left: 12px;
      margin-bottom: 2.5px;
      line-height: 1.30;
    }}
    ul.styled-list li::before {{
      content: "•";
      position: absolute;
      left: 0;
      top: -1px;
      color: #E50695;
      font-size: 12pt;
      line-height: 1;
    }}

    ol.styled-num-list {{
      margin: 2px 0 3.5px 0;
      padding-left: 15px;
    }}
    ol.styled-num-list li {{
      margin-bottom: 2.2px;
      line-height: 1.30;
    }}

    .lead-text {{
      font-size: 8.4pt;
      line-height: 1.35;
      margin-bottom: 8px;
      color: #1F2A44;
    }}

    /* Tables (Matching Reference Aesthetic) */
    table.data-table {{
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 3.5px;
      font-size: 7.2pt;
      line-height: 1.18;
    }}
    table.data-table thead {{
      display: table-header-group;
    }}
    table.data-table tr {{
      break-inside: avoid;
      page-break-inside: avoid;
    }}
    table.data-table th {{
      background-color: #F5F6FA;
      color: #E50695;
      font-weight: 700;
      font-size: 6.6pt;
      text-transform: uppercase;
      letter-spacing: 0.4px;
      padding: 2.2px 3.5px;
      text-align: left;
      border-top: 1px solid #E2E6EE;
      border-bottom: 1.5px solid #021D45;
    }}
    table.data-table td {{
      padding: 1.4px 3.5px;
      border-bottom: 0.5px solid #EAEFF5;
      vertical-align: middle;
      color: #1F2A44;
    }}
    table.data-table tbody tr:hover {{
      background-color: #FAFAFC;
    }}
    table.data-table td.num, table.data-table th.num {{
      text-align: right;
      font-variant-numeric: tabular-nums;
      white-space: nowrap;
    }}
    table.data-table td.center, table.data-table th.center {{
      text-align: center;
      font-variant-numeric: tabular-nums;
      white-space: nowrap;
    }}

    .player-name {{
      font-weight: 600;
      color: #021D45;
    }}
    .player-team {{
      font-size: 7.5pt;
      color: #606F89;
      font-weight: 400;
    }}

    .row-elevated {{
      background-color: #F2FBF5 !important;
    }}
    .symbol-clutch {{
      color: #28A745;
      font-size: 7.5pt;
      margin-right: 3px;
    }}
    .val-negative {{
      color: #DC3545;
      font-weight: 700;
    }}
    .val-bold {{
      font-weight: 700;
      color: #021D45;
    }}

    .table-caption {{
      font-size: 7.8pt;
      font-style: italic;
      color: #606F89;
      margin: 2px 0 4px 0;
      break-after: avoid;
    }}
    .figure-caption {{
      font-size: 7.8pt;
      font-style: italic;
      color: #606F89;
      margin: 2px 0 5px 0;
      break-after: auto;
    }}

    .table-legend {{
      break-inside: avoid;
      font-size: 7.6pt;
      color: #444444;
      background-color: #F5F6FA;
      border-left: 3px solid #E50695;
      padding: 4px 8px;
      margin: 4px 0 8px 0;
      border-radius: 0 3px 3px 0;
      line-height: 1.35;
    }}

    /* Figures */
    .figure-container {{
      width: 100%;
      text-align: center;
      margin: 4px 0;
      break-inside: avoid;
    }}
    .figure-container img {{
      max-width: 100%;
      height: auto;
      display: block;
      margin: 0 auto;
    }}

    /* Appendix Table Styling */
    .appendix-table {{
      font-size: 5.6pt !important;
      line-height: 1.04 !important;
    }}
    .appendix-table th, .appendix-table td {{
      padding: 0.8px 2.0px !important;
    }}
    h2.appendix-main-title {{
      font-size: 10.5pt;
      font-weight: 700;
      color: #021D45;
      margin: 0 0 2px 0;
      break-after: avoid;
    }}
    h3.appendix-sub-title {{
      font-size: 8.8pt;
      font-weight: 700;
      color: #021D45;
      margin: 4px 0 1px 0;
      break-after: avoid;
    }}

    .signoff-line {{
      margin-top: 6px;
      padding: 4px 8px;
      background-color: #F5F6FA;
      border-left: 3px solid #021D45;
      font-size: 7.4pt;
      color: #021D45;
      font-weight: 600;
      border-radius: 0 3px 3px 0;
    }}
  </style>
</head>
<body>

  <!-- ===================================================================== -->
  <!-- PAGE 1: TITLE BLOCK, KEY METRICS, SUMMARY, STACKED TOP 10 TABLES     -->
  <!-- ===================================================================== -->
  <div class="content-flow">
    <div class="top-tag">ROUND 1 METHODOLOGY REPORT</div>
    <h1 class="main-title">Identify the Most Reliable T20 Players Under High Pressure</h1>
    <div class="author-line">Author: Kishalay Das &nbsp;·&nbsp; SupeRR Selector Season 2 &nbsp;·&nbsp; Round 1 Submission</div>
    <div class="title-divider"></div>

    <div class="info-box">
      <div class="key-metrics-grid">
        <div class="key-metric-item">
          <span class="metric-number">883</span>
          <span class="metric-label">Matches</span>
        </div>
        <div class="key-metric-item">
          <span class="metric-number">200,999</span>
          <span class="metric-label">Deliveries</span>
        </div>
        <div class="key-metric-item">
          <span class="metric-number">50,241</span>
          <span class="metric-label">High-Pressure Balls</span>
        </div>
        <div class="key-metric-item">
          <span class="metric-number">131</span>
          <span class="metric-label">Eligible Batters</span>
        </div>
        <div class="key-metric-item">
          <span class="metric-number">140</span>
          <span class="metric-label">Eligible Bowlers</span>
        </div>
      </div>
    </div>

    <p class="lead-text">
      Evaluating clutch performance in T20 cricket requires disentangling genuine repeatable skill from extreme small-sample noise. Conventional heuristics—such as designating death overs in chases as pressure—conflate match phase with match stakes. We built an end-to-end sabermetric pipeline across 883 IPL and T20I matches from 2022 onwards (200,999 deliveries), isolating high-pressure situations via mathematical win-probability leverage across all potential delivery outcomes rather than arbitrary over cutoffs. Primary selections are strictly ranked in descending order of total hierarchical posterior mean impact rating (Rating = Shrunk Baseline <em>B</em> + Shrunk Pressure Elevation <em>Δ</em>).
    </p>

    <!-- Table 1.1: Final Top 10 Batters -->
    <table class="data-table">
      <thead>
        <tr>
          <th style="width: 28px;" class="center">Rk</th>
          <th style="width: 185px;">Top 10 Batters Under Pressure</th>
          <th style="width: 65px;" class="center">Inn (Pos)</th>
          <th style="width: 55px;" class="num">Rating</th>
          <th style="width: 55px;" class="num">Δ</th>
          <th style="width: 120px;" class="center">Δ 90% CI</th>
          <th style="width: 50px;" class="num">Succ%</th>
          <th style="width: 50px;" class="num">P(T10)</th>
        </tr>
      </thead>
      <tbody>
        <tr class="row-elevated">
          <td class="center val-bold">1</td>
          <td><span class="symbol-clutch">●</span><span class="player-name">Suryakumar Yadav</span> <span class="player-team">(MI, India)</span></td>
          <td class="center">40 (29)</td>
          <td class="num val-bold">+28.39</td>
          <td class="num">+8.99</td>
          <td class="center">[+0.4, +17.1]</td>
          <td class="num">69.4%</td>
          <td class="num">90.3%</td>
        </tr>
        <tr>
          <td class="center val-bold">2</td>
          <td><span class="player-name">Vaibhav Sooryavanshi</span> <span class="player-team">(RR, India)</span></td>
          <td class="center">14 (10)</td>
          <td class="num val-bold">+23.89</td>
          <td class="num">+1.71</td>
          <td class="center">[−8.5, +11.3]</td>
          <td class="num">65.3%</td>
          <td class="num">63.2%</td>
        </tr>
        <tr>
          <td class="center val-bold">3</td>
          <td><span class="player-name">Jos Buttler</span> <span class="player-team">(RR, Eng, GT)</span></td>
          <td class="center">27 (19)</td>
          <td class="num val-bold">+23.06</td>
          <td class="num">+8.68</td>
          <td class="center">[−1.5, +17.0]</td>
          <td class="num">66.7%</td>
          <td class="num">62.5%</td>
        </tr>
        <tr>
          <td class="center val-bold">4</td>
          <td><span class="player-name">Heinrich Klaasen</span> <span class="player-team">(SRH, SA)</span></td>
          <td class="center">18 (15)</td>
          <td class="num val-bold">+22.73</td>
          <td class="num">+6.01</td>
          <td class="center">[−2.9, +13.6]</td>
          <td class="num">74.2%</td>
          <td class="num">58.3%</td>
        </tr>
        <tr class="row-elevated">
          <td class="center val-bold">5</td>
          <td><span class="symbol-clutch">●</span><span class="player-name">Reeza Hendricks</span> <span class="player-team">(SA)</span></td>
          <td class="center">14 (11)</td>
          <td class="num val-bold">+22.64</td>
          <td class="num">+14.31</td>
          <td class="center">[+5.5, +22.5]</td>
          <td class="num">69.7%</td>
          <td class="num">57.1%</td>
        </tr>
        <tr>
          <td class="center val-bold">6</td>
          <td><span class="player-name">Abhishek Sharma</span> <span class="player-team">(SRH, India)</span></td>
          <td class="center">36 (22)</td>
          <td class="num val-bold">+21.93</td>
          <td class="num val-negative">−2.25</td>
          <td class="center">[−17.6, +11.4]</td>
          <td class="num">60.0%</td>
          <td class="num">53.6%</td>
        </tr>
        <tr>
          <td class="center val-bold">7</td>
          <td><span class="player-name">Phil Salt</span> <span class="player-team">(Eng, DC, KKR)</span></td>
          <td class="center">25 (16)</td>
          <td class="num val-bold">+21.69</td>
          <td class="num">+5.79</td>
          <td class="center">[−6.1, +16.9]</td>
          <td class="num">61.8%</td>
          <td class="num">49.5%</td>
        </tr>
        <tr class="row-elevated">
          <td class="center val-bold">8</td>
          <td><span class="symbol-clutch">●</span><span class="player-name">Rinku Singh</span> <span class="player-team">(KKR, India)</span></td>
          <td class="center">16 (15)</td>
          <td class="num val-bold">+20.98</td>
          <td class="num">+12.06</td>
          <td class="center">[+3.7, +18.7]</td>
          <td class="num">80.1%</td>
          <td class="num">44.9%</td>
        </tr>
        <tr class="row-elevated">
          <td class="center val-bold">9</td>
          <td><span class="symbol-clutch">●</span><span class="player-name">Shreyas Iyer</span> <span class="player-team">(India, KKR)</span></td>
          <td class="center">25 (19)</td>
          <td class="num val-bold">+19.97</td>
          <td class="num">+10.33</td>
          <td class="center">[+0.5, +19.8]</td>
          <td class="num">70.7%</td>
          <td class="num">36.5%</td>
        </tr>
        <tr>
          <td class="center val-bold">10</td>
          <td><span class="player-name">Tim David</span> <span class="player-team">(MI, Aus, RCB)</span></td>
          <td class="center">29 (20)</td>
          <td class="num val-bold">+19.75</td>
          <td class="num">+0.80</td>
          <td class="center">[−8.6, +9.8]</td>
          <td class="num">65.8%</td>
          <td class="num">35.1%</td>
        </tr>
      </tbody>
    </table>

    <!-- Table 1.2: Final Top 10 Bowlers -->
    <table class="data-table">
      <thead>
        <tr>
          <th style="width: 28px;" class="center">Rk</th>
          <th style="width: 185px;">Top 10 Bowlers Under Pressure</th>
          <th style="width: 65px;" class="center">Spl (Pos)</th>
          <th style="width: 55px;" class="num">Rating</th>
          <th style="width: 55px;" class="num">Δ</th>
          <th style="width: 120px;" class="center">Δ 90% CI</th>
          <th style="width: 50px;" class="num">Succ%</th>
          <th style="width: 50px;" class="num">P(T10)</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td class="center val-bold">1</td>
          <td><span class="player-name">Josh Hazlewood</span> <span class="player-team">(RCB, Aus)</span></td>
          <td class="center">26 (14)</td>
          <td class="num val-bold">+17.83</td>
          <td class="num">+8.70</td>
          <td class="center">[−0.8, +17.9]</td>
          <td class="num">53.5%</td>
          <td class="num">73.5%</td>
        </tr>
        <tr class="row-elevated">
          <td class="center val-bold">2</td>
          <td><span class="symbol-clutch">●</span><span class="player-name">Matheesha Pathirana</span> <span class="player-team">(CSK, SL)</span></td>
          <td class="center">20 (14)</td>
          <td class="num val-bold">+17.48</td>
          <td class="num">+7.66</td>
          <td class="center">[+0.7, +14.2]</td>
          <td class="num">64.9%</td>
          <td class="num">82.7%</td>
        </tr>
        <tr>
          <td class="center val-bold">3</td>
          <td><span class="player-name">Sunil Narine</span> <span class="player-team">(KKR)</span></td>
          <td class="center">27 (15)</td>
          <td class="num val-bold">+14.39</td>
          <td class="num">+5.32</td>
          <td class="center">[−1.4, +11.9]</td>
          <td class="num">54.8%</td>
          <td class="num">56.8%</td>
        </tr>
        <tr>
          <td class="center val-bold">4</td>
          <td><span class="player-name">Jasprit Bumrah</span> <span class="player-team">(MI, India)</span></td>
          <td class="center">34 (17)</td>
          <td class="num val-bold">+13.48</td>
          <td class="num val-negative">−5.11</td>
          <td class="center">[−13.7, +4.0]</td>
          <td class="num">50.4%</td>
          <td class="num">51.3%</td>
        </tr>
        <tr>
          <td class="center val-bold">5</td>
          <td><span class="player-name">Jacob Duffy</span> <span class="player-team">(NZ, RCB)</span></td>
          <td class="center">16 (8)</td>
          <td class="num val-bold">+13.10</td>
          <td class="num">+4.26</td>
          <td class="center">[−5.2, +14.2]</td>
          <td class="num">50.7%</td>
          <td class="num">47.1%</td>
        </tr>
        <tr>
          <td class="center val-bold">6</td>
          <td><span class="player-name">Rashid Khan</span> <span class="player-team">(GT, Afg)</span></td>
          <td class="center">43 (27)</td>
          <td class="num val-bold">+12.97</td>
          <td class="num">+7.27</td>
          <td class="center">[−0.4, +14.9]</td>
          <td class="num">61.1%</td>
          <td class="num">44.7%</td>
        </tr>
        <tr>
          <td class="center val-bold">7</td>
          <td><span class="player-name">Lockie Ferguson</span> <span class="player-team">(GT, NZ, RCB)</span></td>
          <td class="center">18 (10)</td>
          <td class="num val-bold">+12.83</td>
          <td class="num">+8.53</td>
          <td class="center">[−1.1, +18.6]</td>
          <td class="num">54.5%</td>
          <td class="num">43.1%</td>
        </tr>
        <tr>
          <td class="center val-bold">8</td>
          <td><span class="player-name">Varun Chakravarthy</span> <span class="player-team">(KKR)</span></td>
          <td class="center">42 (25)</td>
          <td class="num val-bold">+12.29</td>
          <td class="num">+0.26</td>
          <td class="center">[−7.9, +8.1]</td>
          <td class="num">58.3%</td>
          <td class="num">39.1%</td>
        </tr>
        <tr>
          <td class="center val-bold">9</td>
          <td><span class="player-name">Nathan Ellis</span> <span class="player-team">(PBKS, Aus)</span></td>
          <td class="center">15 (10)</td>
          <td class="num val-bold">+12.26</td>
          <td class="num">+1.90</td>
          <td class="center">[−7.0, +9.7]</td>
          <td class="num">61.6%</td>
          <td class="num">33.9%</td>
        </tr>
        <tr class="row-elevated">
          <td class="center val-bold">10</td>
          <td><span class="symbol-clutch">●</span><span class="player-name">Mitchell Santner</span> <span class="player-team">(CSK, NZ)</span></td>
          <td class="center">36 (22)</td>
          <td class="num val-bold">+12.18</td>
          <td class="num">+8.02</td>
          <td class="center">[+0.3, +15.8]</td>
          <td class="num">59.5%</td>
          <td class="num">39.7%</td>
        </tr>
      </tbody>
    </table>

    <div class="table-legend">
      <strong>Table 1 Guide:</strong> <span class="symbol-clutch">●</span> Light green shading indicates players whose 90% credible interval for pressure elevation (Δ) is strictly above zero. Values in <span class="val-negative">red</span> indicate negative pressure delta (clutch performance dips below ordinary baseline). Rating = net context-adjusted runs added (batters) or saved (bowlers) per 100 balls. <em>Footnote:</em> Players representing Pakistan or Pakistan A are excluded from both rankings as an eligibility choice made by the author (see Section 3).
    </div>

    <div class="submission-box">
      <div class="submission-box-header">
        <span>Methodology at a Glance</span>
        <span class="submission-box-subheader">End-to-end mathematical framework for identifying clutch performance:</span>
      </div>
      <div class="submission-grid">
        <div class="submission-item">
          <div class="submission-col-label">01 WIN PROBABILITY</div>
          <div class="submission-col-text">Out-of-fold LightGBM Win Probability model conditioned on match state; residual means identically 0.000 (1.7 × 10⁻¹⁷ runs/ball, −1.3 × 10⁻¹⁸ outs/ball); win probability Brier scores of 0.2303 (Innings 1) and 0.1555 (Innings 2).</div>
        </div>
        <div class="submission-item">
          <div class="submission-col-label">04 HIERARCHICAL EB</div>
          <div class="submission-col-text">Empirical Bayes REML shrinking baseline (<em>K<sub>B</sub></em> = 1717.4 bat, 1312.9 bowl) and pressure delta (<em>K<sub>Δ</sub></em> = 773.0 bat, 1041.4 bowl; typical weight 24.8% bat, 19.1% bowl); Rating = Shrunk Baseline + Shrunk Delta.</div>
        </div>
        <div class="submission-item">
          <div class="submission-col-label">02 HIGH PRESSURE</div>
          <div class="submission-col-text">Expected absolute outcome swing across all 7 delivery outcomes (Leverage ≥ 75th percentile, 50,241 deliveries); confirmed by 6 non-circular behavioral validation checks.</div>
        </div>
        <div class="submission-item">
          <div class="submission-col-label">05 STATISTICAL RIGOR</div>
          <div class="submission-col-text">1,000 within-match permutations confirm bowling control (<em>p</em> = 0.0300 filtered, 0.0060 full) vs batting variance (<em>p</em> = 0.0440 filtered, 0.0500 full); single seed-42 bootstrap sets all intervals and P(T10).</div>
        </div>
        <div class="submission-item">
          <div class="submission-col-label">03 WICKET VALUATION</div>
          <div class="submission-col-text">Phase-specific values (Powerplay 14.36, Middle 8.13, Death 2.92 runs; weighted mean 8.85 runs; HP recomputed: PP 14.40, Mid 10.71, Death 5.89).</div>
        </div>
        <div class="submission-item">
          <div class="submission-col-label">06 ELIGIBILITY CHOICE</div>
          <div class="submission-col-text">Minimum 100 HP balls, 6 HP matches, and 10 career matches yield 131 eligible batters and 140 eligible bowlers; Pakistan national/A players excluded as author's choice.</div>
        </div>
      </div>
    </div>
  </div>

  <!-- ===================================================================== -->
  <!-- PAGE 2: METHOD AT A GLANCE (REFERENCE STYLE) & SECTION 1 PART A       -->
  <!-- ===================================================================== -->
  <div class="content-flow">
    <div class="section-tag">SECTION 1 · CRISIS IDENTIFICATION</div>
    <h2 class="section-title">1. Pressure Definition: Objective Outcome Leverage</h2>
    <p class="lead-text">
      To isolate high pressure objectively without confounding match stakes with match phase, delivery leverage is formulated across all potential outcomes rather than relying on arbitrary over cutoffs:
    </p>

    <ul class="styled-list">
      <li><strong>Outcome Leverage Formulation:</strong> Rather than designating all death overs as pressure, leverage is defined strictly as the expected absolute win-probability swing across all 7 delivery outcomes, weighted by phase transition probabilities:
      <div style="text-align: center; margin: 6px 0; font-weight: 700; color: #021D45; font-size: 8.8pt;">
        Leverage = ∑ P(outcome | phase) × |WP<sub>sim</sub> − WP<sub>now</sub>|
      </div>
      GroupKFold LightGBM models evaluated on out-of-fold data yield Brier scores of 0.2303 (Innings 1) and 0.1555 (Innings 2). The top quartile (≥ 75th percentile, 50,241 balls) defines High Pressure.</li>
    </ul>

    <!-- Figure 1: Pipeline Diagram -->
    <div class="figure-container">
      <img src="{img_pipeline}" alt="End-to-End Analytics Pipeline Architecture" style="max-height: 65px;">
      <div class="figure-caption">Figure 1: End-to-end sabermetric pipeline architecture from raw delivery tracking to hierarchical shrinkage ratings.</div>
    </div>
  </div>

  <!-- ===================================================================== -->
  <!-- PAGE 3: BEHAVIORAL CHECKS & SECTION 2 PERFORMANCE MEASUREMENT         -->
  <!-- ===================================================================== -->
  <div class="content-flow">
    <div class="section-tag">SECTION 1 (CONT.) · BEHAVIORAL VALIDATION</div>
    <h2 class="section-title">Non-Circular Behavioral Validation &amp; Sample Criteria</h2>
    <p class="lead-text">
      To confirm that high-leverage balls isolate genuine psychological and tactical crisis rather than statistical artifacts, player behavior was compared across ordinary and high-pressure contexts without referencing player ratings:
    </p>

    <ol class="styled-num-list">
      <li><strong>Strike Rotation:</strong> Batters significantly increase singles and twos running from 41.85% to 43.24% (+1.39 pp, <em>d</em> = 0.028, <em>p</em> &lt; 10⁻¹⁰).</li>
      <li><strong>Dot Ball Reduction:</strong> Dot ball percentage drops from 35.59% to 34.42% (−1.17 pp, <em>d</em> = −0.024, <em>p</em> &lt; 10⁻¹⁰).</li>
      <li><strong>Runs Per Ball Variance:</strong> Outcome variance narrows from 3.037 to 2.974 (−0.064 var, Levene <em>p</em> = 0.0038), reflecting risk mitigation.</li>
      <li><strong>Desperation Dismissals:</strong> Run-outs and stumpings rise from 7.22% to 8.22% (+1.00 pp, <em>d</em> = 0.038), but <em>p</em> = 0.0951 (labeled <strong>Not Statistically Significant</strong>).</li>
      <li><strong>Scoring Rates:</strong> Overall run rate is 8.52 vs 8.53 (<em>p</em> = 0.799); boundary percentage is 18.01% vs 17.81% (<em>p</em> = 0.325), confirming disciplined risk management.</li>
      <li><strong>Win Probability Volatility (Definitional):</strong> Average absolute win-probability swing per ball surges +126% from 1.59% to 3.60% (+2.00 pp/ball, <em>d</em> = 0.528, <em>p</em> &lt; 10⁻¹⁰).</li>
    </ol>

    <p style="margin-top: 6px;">
      <strong>Consistency Metrics &amp; Innings Counts:</strong> Success % is defined as Beta-Binomial shrunk positive-impact match rate (α = 4.97, β = 3.95 bat; α = 4.22, β = 3.86 bowl). Requiring ≥ 5 HP balls ensures per-match statistical validity (Suryakumar Yadav has 40 qualifying innings with 29 positive, 72.5% raw, 69.4% shrunk; Jos Buttler has 27 qualifying innings with 19 positive, 70.4% raw, 66.7% shrunk; total appearances ≥ 1 ball are 86 and 82).
    </p>

    <div class="section-tag">SECTION 2 · VALUATION &amp; CALIBRATION</div>
    <h2 class="section-title">2. Performance Measurement: Context Models &amp; Wickets</h2>
    <p class="lead-text">
      Delivery impact is measured by comparing observed scoring and dismissal events against machine-learning context expectations:
    </p>

    <!-- Figure 2: Calibration Deciles -->
    <div class="figure-container">
      <img src="{img_cal}" alt="Out-of-Fold Expected Value Calibration" style="max-height: 75px;">
      <div class="figure-caption">Figure 2: Out-of-fold Expected Value Calibration Deciles (Panel A: xR deciles; Panel B: xW deciles; Panel C: Runs by match phase).</div>
    </div>

    <ul class="styled-list">
      <li><strong>Context Calibration &amp; Residual Integrity:</strong> Out-of-fold GroupKFold LightGBM models for Expected Runs (xR) and Expected Wickets (xW) condition on match state, venue, phase, wickets in hand, and required run rate. All models were recentred by subtracting residual means so league-wide residuals average identically 0.000 (1.7 × 10⁻¹⁷ runs/ball, −1.3 × 10⁻¹⁸ outs/ball). Expected wicket models achieve ROC-AUC 0.595, reflecting that dismissals carry substantial single-delivery noise. Non-Pakistan regulars (≥ 100 HP balls) hold positive baseline means (+3.51 runs/100b bat, +1.57 runs saved/100b bowl) because lower-order tailenders absorb negative residuals.</li>
      <li><strong>Phase-Specific Wicket Valuation:</strong> Wickets are credited based on empirical runs prevented in subsequent overs: Powerplay = 14.36 runs, Middle = 8.13 runs, Death = 2.92 runs (weighted mean 8.85 runs; high-pressure recomputation yields PP 14.40, Mid 10.71, Death 5.89). Top 20 bowler evaluation confirms moderate sensitivity to wicket valuation (8/10 overlap vs HP-specific, 7/10 vs Flat). Middle-overs spinners gain when middle-overs wickets are credited at 8.85 or 10.71 runs rather than the phase-calibrated 8.13 runs; Phase-Specific valuation is adopted because it empirically reflects the actual subsequent innings run-penalty.</li>
    </ul>
  </div>

  <!-- ===================================================================== -->
  <!-- PAGE 4: SECTION 3 FAIR COMPARISONS & RECONCILIATIONS                  -->
  <!-- ===================================================================== -->
  <div class="content-flow">
    <div class="section-tag">SECTION 3 · EQUITABLE EVALUATION</div>
    <h2 class="section-title">3. Fair Comparisons: Qualification &amp; Opposition</h2>
    <p class="lead-text">
      To ensure equitable comparisons across disparate leagues and international environments, rigorous qualification thresholds and opposition quality corrections are applied:
    </p>

    <ul class="styled-list">
      <li><strong>Eligibility Rules &amp; Cohort Counts:</strong> Players must satisfy three volume cutoffs: (1) ≥ 100 High-Pressure balls faced or legal balls bowled; (2) ≥ 6 High-Pressure matches/innings; and (3) ≥ 10 career matches in the 2022–26 master database across IPL and Tier-1 T20Is.</li>
      <li><strong>Pakistan Player Exclusion:</strong> Players representing Pakistan or Pakistan A are excluded from both rankings as an eligibility choice made by the author; this is not required by the dataset or the problem statement. This leaves exactly 131 eligible batters and 140 eligible bowlers (8 batters and 8 bowlers excluded). A transparent audit of excluded players who would have ranked in the unconstrained top 20 is detailed in Table 3.</li>
      <li><strong>Opposition Quality Diagnostics:</strong> High-pressure opposition strength has mean = +6.07 runs/100b (SD = 3.79) as high-pressure deliveries face established top/middle-order batters (+6.07 runs/100b above league average). Batters HP opp strength has mean = +0.46 runs/100b (SD = 1.89). Baseline impact (Raw_B) is unadjusted; bowler ordinary-opposition mean is +5.82 runs/100b (and batter ordinary opp is −0.16 runs/100b), so bowler pressure effects are shifted up by a similar amount for everyone, and rankings are largely unaffected (demonstrated by the 8/10 bowler overlap without opp adjustment and 9/10 overlap under symmetric recentering). Evaluating without opposition adjustment leaves batter rankings 100% identical (10/10 overlap); in bowlers, 8 of 10 players are retained (Pathirana #1 11.43 vs Hazlewood #2 11.40; Varun drops #8 to #13 and Santner drops #10 to #12, with Hasaranga entering at #9 and Kuldeep at #10). Under symmetric recentered adjustment, 9 of 10 bowlers are retained (Hazlewood #1 12.10, Pathirana #2 11.40; Ellis drops to #12 and Archer enters at #10).</li>
    </ul>

    <!-- Table 2: Opposition Quality Audit -->
    <table class="data-table" style="font-size: 7.4pt; margin-top: 4px;">
      <thead>
        <tr>
          <th style="width: 22px;" class="center">Rk</th>
          <th style="width: 110px;">Batter (Top 10)</th>
          <th style="width: 38px;" class="num">Raw_B</th>
          <th style="width: 38px;" class="num">Raw_D</th>
          <th style="width: 35px;" class="num">Opp</th>
          <th style="width: 42px;" class="num">Adj HP</th>
          <th style="width: 60px;">Team</th>
          <th style="width: 22px;" class="center">Rk</th>
          <th style="width: 110px;">Bowler (Top 10)</th>
          <th style="width: 38px;" class="num">Raw_B</th>
          <th style="width: 38px;" class="num">Raw_D</th>
          <th style="width: 35px;" class="num">Opp</th>
          <th style="width: 42px;" class="num">Adj HP</th>
          <th style="width: 60px;">Team</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td class="center val-bold">1</td><td>Suryakumar Yadav</td><td class="num">+29.69</td><td class="num">+15.01</td><td class="num">−0.43</td><td class="num">+44.70</td><td>MI, India</td>
          <td class="center val-bold">1</td><td>Josh Hazlewood</td><td class="num">+17.17</td><td class="num">+28.42</td><td class="num">+7.37</td><td class="num">+45.59</td><td>Aus, RCB</td>
        </tr>
        <tr>
          <td class="center val-bold">2</td><td>Vaibhav Sooryavanshi</td><td class="num">+73.40</td><td class="num">−6.83</td><td class="num">+0.82</td><td class="num">+66.57</td><td>RR, India</td>
          <td class="center val-bold">2</td><td>Matheesha Pathirana</td><td class="num">+21.03</td><td class="num">+31.75</td><td class="num">+5.99</td><td class="num">+52.78</td><td>CSK, SL</td>
        </tr>
        <tr>
          <td class="center val-bold">3</td><td>Jos Buttler</td><td class="num">+19.93</td><td class="num">+15.78</td><td class="num">+0.07</td><td class="num">+35.71</td><td>RR, Eng</td>
          <td class="center val-bold">3</td><td>Sunil Narine</td><td class="num">+17.15</td><td class="num">+14.62</td><td class="num">+9.37</td><td class="num">+31.78</td><td>KKR</td>
        </tr>
        <tr>
          <td class="center val-bold">4</td><td>Heinrich Klaasen</td><td class="num">+31.12</td><td class="num">+13.25</td><td class="num">+0.60</td><td class="num">+44.37</td><td>SRH, SA</td>
          <td class="center val-bold">4</td><td>Jasprit Bumrah</td><td class="num">+35.18</td><td class="num val-negative">−19.93</td><td class="num">+9.20</td><td class="num">+15.25</td><td>MI, India</td>
        </tr>
        <tr>
          <td class="center val-bold">5</td><td>Reeza Hendricks</td><td class="num">+11.98</td><td class="num">+51.38</td><td class="num">−0.44</td><td class="num">+63.36</td><td>SA</td>
          <td class="center val-bold">5</td><td>Jacob Duffy</td><td class="num">+20.90</td><td class="num">+21.28</td><td class="num">+9.01</td><td class="num">+42.17</td><td>NZ, RCB</td>
        </tr>
        <tr>
          <td class="center val-bold">6</td><td>Abhishek Sharma</td><td class="num">+40.33</td><td class="num val-negative">−11.35</td><td class="num">−0.60</td><td class="num">+28.98</td><td>SRH, Ind</td>
          <td class="center val-bold">6</td><td>Rashid Khan</td><td class="num">+7.69</td><td class="num">+16.97</td><td class="num">+3.45</td><td class="num">+24.66</td><td>GT, Afg</td>
        </tr>
        <tr>
          <td class="center val-bold">7</td><td>Phil Salt</td><td class="num">+28.13</td><td class="num">+10.10</td><td class="num">−0.11</td><td class="num">+38.23</td><td>Eng, KKR</td>
          <td class="center val-bold">7</td><td>Lockie Ferguson</td><td class="num">+7.15</td><td class="num">+37.05</td><td class="num">+6.44</td><td class="num">+44.20</td><td>GT, NZ</td>
        </tr>
        <tr>
          <td class="center val-bold">8</td><td>Rinku Singh</td><td class="num">+12.21</td><td class="num">+34.39</td><td class="num">−0.09</td><td class="num">+46.60</td><td>KKR, Ind</td>
          <td class="center val-bold">8</td><td>Varun Chakravarthy</td><td class="num">+20.23</td><td class="num val-negative">−1.24</td><td class="num">+9.07</td><td class="num">+19.00</td><td>KKR, Ind</td>
        </tr>
        <tr>
          <td class="center val-bold">9</td><td>Shreyas Iyer</td><td class="num">+12.80</td><td class="num">+22.00</td><td class="num">−0.44</td><td class="num">+34.81</td><td>Ind, KKR</td>
          <td class="center val-bold">9</td><td>Nathan Ellis</td><td class="num">+26.19</td><td class="num">+4.84</td><td class="num">+7.52</td><td class="num">+31.03</td><td>PBKS, Aus</td>
        </tr>
        <tr>
          <td class="center val-bold">10</td><td>Tim David</td><td class="num">+43.04</td><td class="num val-negative">−4.90</td><td class="num">+0.29</td><td class="num">+38.14</td><td>MI, Aus</td>
          <td class="center val-bold">10</td><td>Mitchell Santner</td><td class="num">+5.84</td><td class="num">+23.43</td><td class="num">+7.93</td><td class="num">+29.28</td><td>CSK, NZ</td>
        </tr>
      </tbody>
    </table>
    <div class="table-caption">Table 2: Opposition Quality Audit &amp; Mathematical Reconciliation (Raw_B + Raw_D = Adj_HP identically). Vaibhav Sooryavanshi's opposition-adjusted pressure delta is −6.83 runs/100b (alongside unadjusted raw delta: 65.75 − 73.40 = −7.65 runs/100b).</div>

    <!-- Table 3: Transparent Audit of Excluded Pakistan Players -->
    <table class="data-table" style="font-size: 7.4pt; margin-top: 4px;">
      <thead>
        <tr>
          <th style="width: 42px;">Discipline</th>
          <th style="width: 95px;">Player Name</th>
          <th style="width: 32px;" class="center">Unc</th>
          <th style="width: 35px;" class="num">HP B</th>
          <th style="width: 46px;" class="num">Rating</th>
          <th style="width: 44px;" class="num">Base</th>
          <th style="width: 44px;" class="num">Delta</th>
          <th style="width: 65px;">Team</th>
          <th>Reason: author's eligibility choice</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Batter</td><td><strong>Mohammad Rizwan</strong></td><td class="center">15</td><td class="num">400</td><td class="num val-bold">+17.86</td><td class="num">+10.57</td><td class="num">+7.29</td><td>Pakistan</td><td>Author's eligibility choice (Pakistan player; not required by dataset)</td>
        </tr>
        <tr>
          <td>Bowler</td><td><strong>Sufiyan Muqeem</strong></td><td class="center">4</td><td class="num">155</td><td class="num val-bold">+14.13</td><td class="num">+9.07</td><td class="num">+5.06</td><td>Pakistan, Pakistan A</td><td>Author's eligibility choice (Pakistan A player; not required by dataset)</td>
        </tr>
        <tr>
          <td>Bowler</td><td><strong>Mohammad Nawaz</strong></td><td class="center">16</td><td class="num">289</td><td class="num val-bold">+11.27</td><td class="num">+6.13</td><td class="num">+5.14</td><td>Pakistan</td><td>Author's eligibility choice (Pakistan player; not required by dataset)</td>
        </tr>
        <tr>
          <td>Bowler</td><td><strong>Abrar Ahmed</strong></td><td class="center">20</td><td class="num">189</td><td class="num val-bold">+10.77</td><td class="num">+7.47</td><td class="num">+3.30</td><td>Pakistan</td><td>Author's eligibility choice (Pakistan player; not required by dataset)</td>
        </tr>
      </tbody>
    </table>
    <div class="table-caption">Table 3: Transparent audit of excluded Pakistan players who would have ranked in the unconstrained Top 20.</div>
  </div>

  <!-- ===================================================================== -->
  <!-- PAGE 5: SECTION 4 EVIDENCE FOR THE TOP 10 (SHRINKAGE & BATTERS PLOT)  -->
  <!-- ===================================================================== -->
  <div class="content-flow">
    <div class="section-tag">SECTION 4 · QUANTITATIVE EVIDENCE</div>
    <h2 class="section-title">4. Evidence for the Top 10: Hierarchical Shrinkage</h2>
    <p class="lead-text">
      <strong>Hierarchical Empirical Bayes Formulation:</strong> Raw metrics suffer from sample size variance. Performance is decomposed into Ordinary Baseline (<em>B<sub>i</sub></em>) plus Pressure Elevation (<em>Δ<sub>i</sub></em>), with each component shrunk via REML toward eligible cohort population priors: Batters μ<sub>B</sub> = +7.02, μ<sub>Δ</sub> = +3.57 (<em>K<sub>B</sub></em> = 1717.4, <em>K<sub>Δ</sub></em> = 773.0, typical weight = 24.8%); Bowlers μ<sub>B</sub> = +2.53, μ<sub>Δ</sub> = +1.14 (<em>K<sub>B</sub></em> = 1312.9, <em>K<sub>Δ</sub></em> = 1041.4, typical weight = 19.1%). Rating = <em>B</em><sub>shrunk</sub> + <em>Δ</em><sub>shrunk</sub>. Delivery accounting reflects non-wide legal deliveries (Abhishek 494b, Salt 397b, Iyer 448b). Refer to <strong>Appendix A</strong> for full player breakdown.
    </p>

    <h3 class="sub-title" style="margin-top: 6px;">Statistical Rigor: Within-Match Null Test &amp; Reliability</h3>
    <ul class="styled-list" style="font-size: 8.2pt; line-height: 1.35;">
      <li><strong>Within-Match Null Permutation Test (1,000 Draws):</strong> High-pressure indicators were permuted within matches (strictly preserving match phase, context, and venue). Bowlers: observed standard deviation across players is 4.052 vs null mean 3.653 (<em>p</em> = 0.0300 filtered cohort; 4.089 vs 3.601, <em>p</em> = 0.0060 full cohort), confirming <em>statistically distinguishable pressure control</em>. Batters: observed standard deviation is 5.068 vs null mean 4.615 (<em>p</em> = 0.0440 filtered; 5.042 vs 4.590, <em>p</em> = 0.0500 full), indicating <em>borderline pressure-specific signal</em> driven by high single-match batting variance. Refer to <strong>Appendix B</strong> for full side-by-side parameter verification.</li>
      <li><strong>Reliability Reconciliation:</strong> Applying the Spearman-Brown prophecy formula (<em>r</em><sub>SB</sub> = 2<em>r</em> / [1 + <em>r</em>]) to split-half correlations yields <em>r</em><sub>SB</sub> = 0.107 (batters) vs 0.212 (bowlers). The gap to model-implied reliability (24.8% bat, 19.1% bowl) reflects that batting clutch impact across independent halves is subject to substantial single-delivery variance, whereas bowling exhibits higher longitudinal repeatability.</li>
    </ul>

    
    <!-- Figure 3: Stacked Bar Chart -->
    <div class="figure-container">
      <img src="{img_stacked}" alt="Decomposition of Rating into Baseline and Pressure Delta" style="max-height: 90px;">
      <div class="figure-caption">Figure 3: Two-tier hierarchical decomposition showing Shrunk Baseline (B) plus Shrunk Pressure Delta (Δ). Negative pressure deltas (Abhishek Sharma, Jasprit Bumrah) are highlighted in red.</div>
    </div>

    <!-- Ordering Rules & Audits Shaded Box -->
    <div class="info-box" style="margin-top: 4px; margin-bottom: 6px; padding: 8px 12px; font-size: 8.0pt; line-height: 1.35;">
      <p style="margin-bottom: 3px;"><strong>Ordering Rule on Pressure Dips:</strong> Primary ranking is <strong>Rating = Baseline + Pressure Effect with NO dip exclusion</strong> (Abhishek #6, Bumrah #4). Under <strong>Rule B (Clutch-Constrained: Δ<sub>shrunk</sub> ≥ 0)</strong>, Bumrah and Abhishek are excluded due to negative pressure deltas (−5.11 and −2.25), allowing Stoinis (Bat #10) and Kuldeep (Bowl #10) into the Top 10.</p>
      <p style="margin-bottom: 3px;"><strong>Case Audit on Abhishek Sharma &amp; Jasprit Bumrah:</strong> Abhishek Sharma posts an extraordinary baseline (+24.17 shrunk) but a negative pressure delta (−2.25 shrunk; 90% CI [−17.6, +11.4]). Jasprit Bumrah leads all bowlers in baseline runs saved (+18.59 shrunk) but records a negative pressure delta (−5.11 shrunk; 90% CI [−13.7, +4.0]). Under Rule A, their exceptional baselines secure Ranks 6 and 4. Under Rule B, both are excluded. Under a credibly negative test (CI upper &lt; 0), both are retained because their intervals comfortably span zero.</p>
      <p style="margin: 0;"><strong>Diagnostic Finding on Vaibhav Sooryavanshi:</strong> Sooryavanshi's Rank 2 position depends heavily on extraordinary baseline scoring (+73.40 runs/100b) rather than clutch elevation. His Raw Baseline Impact is +73.40, while Raw High-Pressure Impact is +65.75 (+0.82 opp diff), yielding an opposition-adjusted HP impact of +66.57 and a negative raw pressure delta of −6.83 runs/100b. REML shrinks his 168 HP balls toward +3.57, producing a shrunk delta of +1.71. Under Rule B (Δ<sub>shrunk</sub> ≥ 0) he qualifies and maintains Rank 2; on raw delta alone he would be excluded. Under a stricter volume filter of minimum 200 HP balls, his 168 balls render him unranked.</p>
    </div>

    <!-- Figure 4: Batters Forest Plot -->
    <div class="figure-container">
      <img src="{img_forest_bat}" alt="Top 10 Batters Forest Plot" style="max-height: 85px;">
      <div class="figure-caption">Figure 4: Top 10 Batters posterior ratings with 90% match-grouped bootstrap credible intervals and 95% within-match null permutation band. Ratings and P(T10) are reported in the right-hand column.</div>
    </div>
  </div>

  <!-- ===================================================================== -->
  <!-- PAGE 6: BOWLERS FOREST PLOT & SECTION 5 RELIABILITY AND LIMITATIONS   -->
  <!-- ===================================================================== -->
  <div class="content-flow">
    <!-- Figure 5: Bowlers Forest Plot at top of page -->
    <div class="figure-container" style="margin-top: 0;">
      <img src="{img_forest_bowl}" alt="Top 10 Bowlers Forest Plot" style="max-height: 85px;">
      <div class="figure-caption">Figure 5: Top 10 Bowlers posterior ratings with 90% match-grouped bootstrap credible intervals and 95% within-match null permutation band. Ratings and P(T10) are reported in the right-hand column.</div>
    </div>

    <div class="section-tag">SECTION 5 · STABILITY &amp; CAVEATS</div>
    <h2 class="section-title">5. Reliability and Limitations: Sensitivity &amp; Caveats</h2>
    <p class="lead-text">
      The stability of rankings was tested across 14 distinct methodological specifications encompassing wicket valuations, pressure cutoffs, volume filters, competition subsets, and temporal weightings:
    </p>

    <!-- Figure 6: Rank Ranges Chart -->
    <div class="figure-container">
      <img src="{img_ranges}" alt="Rank Sensitivity Ranges Across 14 Specifications" style="max-height: 75px;">
      <div class="figure-caption">Figure 6: Rank sensitivity ranges [Min, Max] across 14 specifications for Top 10 Batters and Bowlers. Solid circles indicate primary base rank. Players failing volume cutoffs are treated as unranked.</div>
    </div>

    <!-- Table 4: Specification Sensitivity Matrix -->
    <table class="data-table" style="font-size: 7.2pt; margin-top: 3px;">
      <thead>
        <tr>
          <th style="width: 32px;" class="center">Spec</th>
          <th style="width: 220px;">Specification Definition</th>
          <th style="width: 75px;" class="center">Batters Overlap</th>
          <th style="width: 75px;" class="center">Bowlers Overlap</th>
          <th>Summary Sensitivity Impact</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td class="center val-bold">S1</td><td>Primary Base: Phase-Specific Wickets (PP 14.36, Mid 8.13, Death 2.92)</td><td class="center">10/10 (1.00)</td><td class="center">10/10 (1.00)</td><td>Primary reference model</td>
        </tr>
        <tr>
          <td class="center val-bold">S2</td><td>Flat Wicket Value = 8.85 runs</td><td class="center">10/10 (1.00)</td><td class="center">7/10 (0.54)</td><td>Spinners gain with flat middle wickets</td>
        </tr>
        <tr>
          <td class="center val-bold">S3</td><td>Wicket Value = 7.0 runs</td><td class="center">10/10 (1.00)</td><td class="center">7/10 (0.54)</td><td>Economy-dominant bowlers gain rank</td>
        </tr>
        <tr>
          <td class="center val-bold">S4</td><td>Wicket Value = 9.0 runs</td><td class="center">10/10 (1.00)</td><td class="center">7/10 (0.54)</td><td>Similar to flat 8.85 benchmark</td>
        </tr>
        <tr>
          <td class="center val-bold">S5</td><td>Wicket Value = 11.0 runs</td><td class="center">10/10 (1.00)</td><td class="center">7/10 (0.54)</td><td>Wicket-taking specialists elevated</td>
        </tr>
        <tr>
          <td class="center val-bold">S6</td><td>Wicket Value = 13.0 runs</td><td class="center">9/10 (0.82)</td><td class="center">7/10 (0.54)</td><td>Wicket penalties impact aggressive hitters</td>
        </tr>
        <tr>
          <td class="center val-bold">S7</td><td>Pressure Threshold: Top 20% Leverage</td><td class="center">9/10 (0.82)</td><td class="center">7/10 (0.54)</td><td>Extreme crisis deliveries isolated</td>
        </tr>
        <tr>
          <td class="center val-bold">S8</td><td>Pressure Threshold: Top 30% Leverage</td><td class="center">8/10 (0.67)</td><td class="center">9/10 (0.82)</td><td>Broader pressure cohort expands sample size</td>
        </tr>
        <tr>
          <td class="center val-bold">S9</td><td>Minimum Sample: 150 Balls</td><td class="center">10/10 (1.00)</td><td class="center">9/10 (0.82)</td><td>All 10 batters qualify; Ellis #11, Kuldeep #8, Duffy #5</td>
        </tr>
        <tr>
          <td class="center val-bold">S10</td><td>Minimum Sample: 200 Balls</td><td class="center">9/10 (0.82)</td><td class="center">9/10 (0.82)</td><td>Sooryavanshi (168b) and Duffy (191b) unranked</td>
        </tr>
        <tr>
          <td class="center val-bold">S11</td><td>Competition: IPL-Only</td><td class="center">8/10 (0.67)</td><td class="center">7/10 (0.54)</td><td>Hendricks, Salt, Duffy, Santner lose T20I volume</td>
        </tr>
        <tr>
          <td class="center val-bold">S12</td><td>Competition: Tier 1 Only (No A-Team/Associate)</td><td class="center">10/10 (1.00)</td><td class="center">9/10 (0.82)</td><td>Removes associate development games</td>
        </tr>
        <tr>
          <td class="center val-bold">S13</td><td>Competition: T20I Excluded</td><td class="center">8/10 (0.67)</td><td class="center">7/10 (0.54)</td><td>Identical to IPL-only constraint</td>
        </tr>
        <tr>
          <td class="center val-bold">S14</td><td>Weighting: Recency Weighting (2022–26)</td><td class="center">10/10 (1.00)</td><td class="center">8/10 (0.67)</td><td>Exponential decay favoring 2024–25 seasons</td>
        </tr>
      </tbody>
    </table>
    <div class="table-caption">Table 4: Jaccard overlap and stability across 14 distinct model specifications.</div>

    <h3 class="sub-title" style="margin-top: 6px;">Honest Limitations, Caveats &amp; Reproduction</h3>
    <ol class="styled-num-list" style="font-size: 8.2pt; line-height: 1.35;">
      <li><strong>Rank Distinguishability:</strong> Pairwise bootstrap win probabilities (49%–64%) indicate top-10 positions form an elite cluster rather than immutable individual ranks.</li>
      <li><strong>Impact Player Rule:</strong> Post-2023 IPL rules artificially increased batting depths, elevating aggression earlier in chases.</li>
      <li><strong>Expected Wicket Noise:</strong> Expected wicket model achieves ROC-AUC 0.595, reflecting that dismissals are high-variance events; rolling Bayesian updates are advised. Refer to <strong>Appendix C</strong> for delivery-level sanity checks on career stars.</li>
      <li><strong>Computational Reproduction:</strong> Run <code>python run_all.py</code> on Windows PowerShell to reproduce every artifact, model, bootstrap draw, and table end-to-end.</li>
    </ol>
  </div>

  <!-- ===================================================================== -->
  <!-- PAGE 7: APPENDICES A, B, AND C                                        -->
  <!-- ===================================================================== -->
  <div class="content-flow">
    <div class="section-tag" style="margin-top: 0; margin-bottom: 2px;">TECHNICAL DOCUMENTATION · REPRODUCIBILITY</div>
    <h2 class="appendix-main-title">Appendix A: Calculation Verification for Primary Selections</h2>
    <p class="table-caption" style="margin-top: 0; margin-bottom: 2px;">Table A1: Complete breakdown of baseline and pressure-side impact, shrinkage weights, and posterior intervals for all 20 players.</p>
    
    <table class="data-table appendix-table">
      <thead>
        <tr>
          <th style="width: 16px;" class="center">Rk</th>
          <th style="width: 105px;">Player Name</th>
          <th style="width: 24px;" class="center">Role</th>
          <th style="width: 28px;" class="num">N_B</th>
          <th style="width: 28px;" class="num">w_B</th>
          <th style="width: 34px;" class="num">Raw_B</th>
          <th style="width: 34px;" class="num">B_shk</th>
          <th style="width: 28px;" class="num">N_D</th>
          <th style="width: 28px;" class="num">w_D</th>
          <th style="width: 34px;" class="num">Raw_D</th>
          <th style="width: 34px;" class="num">D_shk</th>
          <th style="width: 38px;" class="num">Rating</th>
          <th style="width: 65px;" class="center">90% CI</th>
          <th style="width: 30px;" class="num">P(T10)</th>
        </tr>
      </thead>
      <tbody>
        <tr><td class="center val-bold">1</td><td>Suryakumar Yadav</td><td class="center">Bat</td><td class="num">2062</td><td class="num">0.546</td><td class="num">+29.69</td><td class="num">+19.39</td><td class="num">697</td><td class="num">0.474</td><td class="num">+15.01</td><td class="num">+8.99</td><td class="num val-bold">+28.39</td><td class="center">[18.2, 36.2]</td><td class="num">90.3%</td></tr>
        <tr><td class="center val-bold">2</td><td>Vaibhav Sooryavanshi</td><td class="center">Bat</td><td class="num">508</td><td class="num">0.228</td><td class="num">+73.40</td><td class="num">+22.18</td><td class="num">168</td><td class="num">0.179</td><td class="num">−6.83</td><td class="num">+1.71</td><td class="num val-bold">+23.89</td><td class="center">[12.1, 33.3]</td><td class="num">63.2%</td></tr>
        <tr><td class="center val-bold">3</td><td>Jos Buttler</td><td class="center">Bat</td><td class="num">2272</td><td class="num">0.570</td><td class="num">+19.93</td><td class="num">+14.37</td><td class="num">557</td><td class="num">0.419</td><td class="num">+15.78</td><td class="num">+8.68</td><td class="num val-bold">+23.06</td><td class="center">[12.1, 31.3]</td><td class="num">62.5%</td></tr>
        <tr><td class="center val-bold">4</td><td>Heinrich Klaasen</td><td class="center">Bat</td><td class="num">1156</td><td class="num">0.402</td><td class="num">+31.12</td><td class="num">+16.72</td><td class="num">261</td><td class="num">0.252</td><td class="num">+13.25</td><td class="num">+6.01</td><td class="num val-bold">+22.73</td><td class="center">[13.1, 29.4]</td><td class="num">58.3%</td></tr>
        <tr><td class="center val-bold">5</td><td>Reeza Hendricks</td><td class="center">Bat</td><td class="num">611</td><td class="num">0.262</td><td class="num">+11.98</td><td class="num">+8.33</td><td class="num">224</td><td class="num">0.225</td><td class="num">+51.38</td><td class="num">+14.31</td><td class="num val-bold">+22.64</td><td class="center">[13.2, 28.1]</td><td class="num">57.1%</td></tr>
        <tr><td class="center val-bold">6</td><td>Abhishek Sharma</td><td class="center">Bat</td><td class="num">1823</td><td class="num">0.515</td><td class="num">+40.33</td><td class="num">+24.17</td><td class="num">494</td><td class="num">0.390</td><td class="num val-negative">−11.35</td><td class="num val-negative">−2.25</td><td class="num val-bold">+21.93</td><td class="center">[6.3, 35.0]</td><td class="num">53.6%</td></tr>
        <tr><td class="center val-bold">7</td><td>Phil Salt</td><td class="center">Bat</td><td class="num">1246</td><td class="num">0.420</td><td class="num">+28.13</td><td class="num">+15.90</td><td class="num">397</td><td class="num">0.339</td><td class="num">+10.10</td><td class="num">+5.79</td><td class="num val-bold">+21.69</td><td class="center">[9.0, 30.9]</td><td class="num">49.5%</td></tr>
        <tr><td class="center val-bold">8</td><td>Rinku Singh</td><td class="center">Bat</td><td class="num">990</td><td class="num">0.366</td><td class="num">+12.21</td><td class="num">+8.92</td><td class="num">294</td><td class="num">0.276</td><td class="num">+34.39</td><td class="num">+12.06</td><td class="num val-bold">+20.98</td><td class="center">[12.2, 26.7]</td><td class="num">44.9%</td></tr>
        <tr><td class="center val-bold">9</td><td>Shreyas Iyer</td><td class="center">Bat</td><td class="num">1417</td><td class="num">0.452</td><td class="num">+12.80</td><td class="num">+9.64</td><td class="num">448</td><td class="num">0.367</td><td class="num">+22.00</td><td class="num">+10.33</td><td class="num val-bold">+19.97</td><td class="center">[9.9, 26.8]</td><td class="num">36.5%</td></tr>
        <tr><td class="center val-bold">10</td><td>Tim David</td><td class="center">Bat</td><td class="num">850</td><td class="num">0.331</td><td class="num">+43.04</td><td class="num">+18.95</td><td class="num">376</td><td class="num">0.327</td><td class="num val-negative">−4.90</td><td class="num">+0.80</td><td class="num val-bold">+19.75</td><td class="center">[9.5, 27.7]</td><td class="num">35.1%</td></tr>
        <tr><td class="center val-bold">1</td><td>Josh Hazlewood</td><td class="center">Bowl</td><td class="num">1078</td><td class="num">0.451</td><td class="num">+17.17</td><td class="num">+9.13</td><td class="num">399</td><td class="num">0.277</td><td class="num">+28.42</td><td class="num">+8.70</td><td class="num val-bold">+17.83</td><td class="center">[7.4, 27.9]</td><td class="num">73.5%</td></tr>
        <tr><td class="center val-bold">2</td><td>Matheesha Pathirana</td><td class="center">Bowl</td><td class="num">853</td><td class="num">0.394</td><td class="num">+21.03</td><td class="num">+9.82</td><td class="num">282</td><td class="num">0.213</td><td class="num">+31.75</td><td class="num">+7.66</td><td class="num val-bold">+17.48</td><td class="center">[10.1, 24.1]</td><td class="num">82.7%</td></tr>
        <tr><td class="center val-bold">3</td><td>Sunil Narine</td><td class="center">Bowl</td><td class="num">1062</td><td class="num">0.447</td><td class="num">+17.15</td><td class="num">+9.07</td><td class="num">468</td><td class="num">0.310</td><td class="num">+14.62</td><td class="num">+5.32</td><td class="num val-bold">+14.39</td><td class="center">[7.2, 21.5]</td><td class="num">56.8%</td></tr>
        <tr><td class="center val-bold">4</td><td>Jasprit Bumrah</td><td class="center">Bowl</td><td class="num">1270</td><td class="num">0.492</td><td class="num">+35.18</td><td class="num">+18.59</td><td class="num">439</td><td class="num">0.297</td><td class="num val-negative">−19.93</td><td class="num val-negative">−5.11</td><td class="num val-bold">+13.48</td><td class="center">[5.0, 22.5]</td><td class="num">51.3%</td></tr>
        <tr><td class="center val-bold">5</td><td>Jacob Duffy</td><td class="center">Bowl</td><td class="num">686</td><td class="num">0.343</td><td class="num">+20.90</td><td class="num">+8.83</td><td class="num">191</td><td class="num">0.155</td><td class="num">+21.28</td><td class="num">+4.26</td><td class="num val-bold">+13.10</td><td class="center">[2.4, 23.1]</td><td class="num">47.1%</td></tr>
        <tr><td class="center val-bold">6</td><td>Rashid Khan</td><td class="center">Bowl</td><td class="num">2089</td><td class="num">0.614</td><td class="num">+7.69</td><td class="num">+5.70</td><td class="num">658</td><td class="num">0.387</td><td class="num">+16.97</td><td class="num">+7.27</td><td class="num val-bold">+12.97</td><td class="center">[5.5, 20.5]</td><td class="num">44.7%</td></tr>
        <tr><td class="center val-bold">7</td><td>Lockie Ferguson</td><td class="center">Bowl</td><td class="num">814</td><td class="num">0.383</td><td class="num">+7.15</td><td class="num">+4.30</td><td class="num">270</td><td class="num">0.206</td><td class="num">+37.05</td><td class="num">+8.53</td><td class="num val-bold">+12.83</td><td class="center">[2.4, 23.0]</td><td class="num">43.1%</td></tr>
        <tr><td class="center val-bold">8</td><td>Varun Chakravarthy</td><td class="center">Bowl</td><td class="num">1520</td><td class="num">0.537</td><td class="num">+20.23</td><td class="num">+12.03</td><td class="num">608</td><td class="num">0.369</td><td class="num val-negative">−1.24</td><td class="num">+0.26</td><td class="num val-bold">+12.29</td><td class="center">[4.7, 19.6]</td><td class="num">39.1%</td></tr>
        <tr><td class="center val-bold">9</td><td>Nathan Ellis</td><td class="center">Bowl</td><td class="num">649</td><td class="num">0.331</td><td class="num">+26.19</td><td class="num">+10.36</td><td class="num">268</td><td class="num">0.205</td><td class="num">+4.84</td><td class="num">+1.90</td><td class="num val-bold">+12.26</td><td class="center">[5.1, 18.5]</td><td class="num">33.9%</td></tr>
        <tr><td class="center val-bold">10</td><td>Mitchell Santner</td><td class="center">Bowl</td><td class="num">1272</td><td class="num">0.492</td><td class="num">+5.84</td><td class="num">+4.16</td><td class="num">465</td><td class="num">0.309</td><td class="num">+23.43</td><td class="num">+8.02</td><td class="num val-bold">+12.18</td><td class="center">[5.2, 19.3]</td><td class="num">39.7%</td></tr>
      </tbody>
    </table>

    <h3 class="appendix-sub-title">Appendix B: Model Parameter Verification Across Cohorts</h3>
    <p class="table-caption" style="margin-top: 0; margin-bottom: 2px;">Table B1: Side-by-side verification of parameters estimated on full vs filtered (non-Pakistan) cohorts.</p>

    <table class="data-table appendix-table">
      <thead>
        <tr>
          <th style="width: 120px;">Parameter / Metric</th>
          <th style="width: 125px;">Pre-Exclusion (All Cohort)</th>
          <th style="width: 130px;">Post-Exclusion (Filtered Cohort)</th>
          <th>Impact / Reconciliation Notes</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Eligible Batters Count</td><td>139 players (≥ 100 HP balls)</td><td class="val-bold">131 players (8 Pakistan excluded)</td><td>Cohort filtered before estimating population means and bounds</td>
        </tr>
        <tr>
          <td>Eligible Bowlers Count</td><td>148 players (≥ 100 HP balls)</td><td class="val-bold">140 players (8 Pakistan excluded)</td><td>Cohort filtered before estimating population means and bounds</td>
        </tr>
        <tr>
          <td>Batters REML Priors</td><td>K<sub>B</sub> = 1717.4, K<sub>Δ</sub> = 773.0</td><td class="val-bold">K<sub>B</sub> = 1894.4, K<sub>Δ</sub> = 671.6</td><td>Primary model retains global league K (1717.4 / 773.0); sub-cohort re-fit shown</td>
        </tr>
        <tr>
          <td>Bowlers REML Priors</td><td>K<sub>B</sub> = 1312.9, K<sub>Δ</sub> = 1041.4</td><td class="val-bold">K<sub>B</sub> = 1384.0, K<sub>Δ</sub> = 963.5</td><td>Primary model retains global league K (1312.9 / 1041.4); sub-cohort re-fit shown</td>
        </tr>
        <tr>
          <td>Population Means (μ)</td><td>Bat: +7.07 / +3.38 | Bowl: +3.37 / +1.03</td><td class="val-bold">Bat: +7.02 / +3.57 | Bowl: +2.53 / +1.14</td><td>Filtered eligible cohort means used for all primary Bayesian shrinkage</td>
        </tr>
        <tr>
          <td>Null Test p-values</td><td>Bat p = 0.0500 | Bowl p = 0.0060</td><td class="val-bold">Bat p = 0.0440 | Bowl p = 0.0300</td><td>Bowler p shifts as excluding Muqeem narrows observed std from 4.089 to 4.052</td>
        </tr>
        <tr>
          <td>Virat Kohli Verification</td><td>Rating +17.43 (Rank 17 overall)</td><td class="val-bold">Rating +17.52 (Rank 16 overall)</td><td>N_B 1787, Raw_B +14.33, Shk_B +10.75; N_D 669, Raw_D +10.45, Shk_D +6.76</td>
        </tr>
        <tr>
          <td>Rohit Sharma Verification</td><td>Rating +5.30 (Rank 124 overall)</td><td class="val-bold">Rating +5.40 (Rank 117 overall)</td><td>N_B 1181, Raw_B −5.62, Shk_B +1.87; N_D 438, Raw_D +3.45, Shk_D +3.53</td>
        </tr>
      </tbody>
    </table>

    <h3 class="appendix-sub-title">Appendix C: Famous Player Diagnostics (Delivery-Level Numbers)</h3>
    <p class="table-caption" style="margin-top: 0; margin-bottom: 2px;">Table C1: Delivery-level sanity checks against career international stars.</p>

    <table class="data-table appendix-table">
      <thead>
        <tr>
          <th style="width: 90px;">Player</th>
          <th style="width: 35px;">Role</th>
          <th style="width: 32px;" class="num">HP Balls</th>
          <th style="width: 48px;">Actual HP</th>
          <th style="width: 48px;">Expected HP</th>
          <th style="width: 38px;" class="num">Rating</th>
          <th style="width: 20px;" class="center">Rk</th>
          <th>Direct Delivery-Level Verification</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>Suryakumar Yadav</strong></td><td>Batter</td><td class="num">697</td><td>SR 167.9</td><td>Exp SR 136.4</td><td class="num val-bold">+28.39</td><td class="center">1</td><td>Direct ball-by-ball: 697 HP balls faced (723 total incl 26 wides), 1170 runs, 27 outs. HP SR 167.9 (+31.5 SR above exp); 69.4% shrunk succ rate. Shrunk base +19.39, delta +8.99. Rank 1 globally.</td>
        </tr>
        <tr>
          <td><strong>Jos Buttler</strong></td><td>Batter</td><td class="num">557</td><td>SR 164.6</td><td>Exp SR 140.9</td><td class="num val-bold">+23.06</td><td class="center">3</td><td>Direct ball-by-ball: 557 HP balls faced (568 total incl 11 wides), 917 runs, 19 outs. HP SR 164.6 (+23.7 SR above exp); 66.7% shrunk succ rate. Shrunk base +14.37, delta +8.68. Rank 3 overall.</td>
        </tr>
        <tr>
          <td><strong>Virat Kohli</strong></td><td>Batter</td><td class="num">669</td><td>SR 149.8</td><td>Exp SR 141.2</td><td class="num val-bold">+17.52</td><td class="center">16</td><td>Direct ball-by-ball: 669 HP balls (excluding 23 wides), 1002 runs, 20 outs (2.99% out rate vs 4.65% exp). Actual SR 149.8 (+8.6 SR). Hierarchical rating: Shrunk base +10.75, shrunk delta +6.76, Rating +17.52, Rank 16.</td>
        </tr>
        <tr>
          <td><strong>Rohit Sharma</strong></td><td>Batter</td><td class="num">438</td><td>SR 150.7</td><td>Exp SR 141.3</td><td class="num val-bold">+5.40</td><td class="center">117</td><td>Direct ball-by-ball: 438 HP balls (excluding 15 wides), 660 runs, 26 outs (5.94% vs 4.44% exp). Actual SR 150.7 vs Exp 141.3; early outs create wkt deficit. Shrunk base +1.87, shrunk delta +3.53, Rating +5.40, Rank 117.</td>
        </tr>
        <tr>
          <td><strong>Josh Hazlewood</strong></td><td>Bowler</td><td class="num">399</td><td>Econ 7.67</td><td>Exp Econ 8.35</td><td class="num val-bold">+17.83</td><td class="center">1</td><td>Direct ball-by-ball: 399 HP legal balls, 510 runs, 34 wkts; HP SR 11.7. Suppresses 0.68 RPO below exp. Shrunk base +9.13, delta +8.70. Rank 1 bowler globally.</td>
        </tr>
        <tr>
          <td><strong>Matheesha Pathirana</strong></td><td>Bowler</td><td class="num">282</td><td>Econ 7.43</td><td>Exp Econ 8.65</td><td class="num val-bold">+17.48</td><td class="center">2</td><td>Direct ball-by-ball: 282 HP legal balls, 349 runs, 26 wkts; HP SR 10.8. Suppresses 1.22 RPO below exp. Shrunk base +9.82, delta +7.66. Rank 2 overall.</td>
        </tr>
        <tr>
          <td><strong>Jasprit Bumrah</strong></td><td>Bowler</td><td class="num">439</td><td>Econ 7.61</td><td>Exp Econ 8.68</td><td class="num val-bold">+13.48</td><td class="center">4</td><td>Direct ball-by-ball: 439 HP legal balls, 557 runs, 14 wkts. Actual Econ 7.61 vs Exp 8.68 (−1.07 rpo saved); Wkt Rate 3.19% vs Exp 5.07%. Shrunk base +18.59 secures Rank 4 overall.</td>
        </tr>
        <tr>
          <td><strong>Rashid Khan</strong></td><td>Bowler</td><td class="num">658</td><td>Econ 6.72</td><td>Exp Econ 8.35</td><td class="num val-bold">+12.97</td><td class="center">6</td><td>Direct ball-by-ball: 658 HP legal balls, 737 runs, 42 wkts. Actual Econ 6.72 vs Exp 8.35 (−1.63 rpo saved); HP Wkt Rate 6.38% (SR 15.7). Shrunk base +5.70, delta +7.27. Rank 6 overall.</td>
        </tr>
      </tbody>
    </table>

    <div class="signoff-line">
      SupeRR Selector Season 2 – Round 1 Final Submission &nbsp;·&nbsp; Author: <strong>Kishalay Das</strong> &nbsp;·&nbsp; Verified Across 200,999 Deliveries
    </div>
  </div>

</body>
</html>
"""
    return html

def export_pdf():
    """Renders the HTML report to PDF via Playwright and syncs to report/."""
    target_outputs = OUTPUTS_DIR / "methodology_report.pdf"
    target_report = REPORT_DIR / "methodology_report.pdf"

    # Make sure backup of previous PDF exists
    backup_outputs = OUTPUTS_DIR / "methodology_report_old.pdf"
    backup_report = REPORT_DIR / "methodology_report_old.pdf"

    if target_outputs.exists() and not backup_outputs.exists():
        shutil.copyfile(target_outputs, backup_outputs)
        print(f"[+] Preserved backup at: {backup_outputs}")
    if target_report.exists() and not backup_report.exists():
        shutil.copyfile(target_report, backup_report)
        print(f"[+] Preserved backup at: {backup_report}")

    html_content = build_html_content()
    temp_html_path = OUTPUTS_DIR / "report_temp.html"
    with open(temp_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"[+] Saved report HTML to: {temp_html_path}")

    # Footer template matching problem-statement styling
    footer_html = '''
    <div style="font-size: 8pt; font-family: 'Montserrat', Arial, sans-serif; width: 100%; display: flex; justify-content: space-between; padding: 0 22mm; color: #7A889B; border-top: 0.5px solid #E2E6EE; padding-top: 3px; box-sizing: border-box;">
      <span style="font-weight: 500;">SupeRR Selector Season 2 · Round 1 Submission</span>
      <span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span>
    </div>
    '''

    print("[*] Launching Playwright Chromium to print restyled publication PDF...")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html_content, wait_until="networkidle")

        pdf_bytes = page.pdf(
            format="Letter",
            display_header_footer=True,
            header_template="<div></div>",
            footer_template=footer_html,
            margin={"top": "22mm", "bottom": "22mm", "left": "22mm", "right": "22mm"},
            print_background=True
        )
        browser.close()

    with open(target_outputs, "wb") as f:
        f.write(pdf_bytes)
    print(f"[+] Successfully exported restyled publication PDF to: {target_outputs} ({len(pdf_bytes):,} bytes)")

    # Sync to report/
    shutil.copyfile(target_outputs, target_report)
    print(f"[+] Synced methodology report to: {target_report}")

    # Remove temporary HTML
    if temp_html_path.exists():
        temp_html_path.unlink()

if __name__ == "__main__":
    export_pdf()
