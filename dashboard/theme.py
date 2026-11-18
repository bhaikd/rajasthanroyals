"""
dashboard/theme.py - Theme and CSS configuration for the SupeRR Selector Dashboard.
Matches the styling and typography of the methodology report PDF.
"""
import plotly.graph_objects as go
import streamlit as st

# Color Palette matching the methodology report PDF
NAVY = "#021D45"
PRIMARY_TEXT = "#0B1F44"
BODY_TEXT = "#1F2A44"
MUTED_TEXT = "#606F89"
PINK = "#E50695"
BATTER_COLOR = "#E50695"
BOWLER_COLOR = "#021D45"
PANEL_BG = "#F4F6FA"
WHITE = "#FFFFFF"
BORDER_COLOR = "#E2E6EE"
GREEN_TINT = "#E8F5EC"
GREEN_TEXT = "#1E7E34"
MUTED_RED = "#C0392B"

CUSTOM_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400;1,600&display=swap');

/* --- TOP HEADER BAR FIX --- */
header[data-testid="stHeader"] {{
    background-color: #FFFFFF !important;
    border-bottom: 1px solid #E6E9F0 !important;
    z-index: 99999 !important;
}}

header[data-testid="stHeader"] button,
header[data-testid="stHeader"] svg,
header[data-testid="stHeader"] span {{
    color: {PRIMARY_TEXT} !important;
    fill: {PRIMARY_TEXT} !important;
}}

/* --- SIDEBAR STYLING & FIX PADDING/CLIPPING --- */
section[data-testid="stSidebar"] {{
    background-color: {PANEL_BG} !important;
    border-right: 1px solid {BORDER_COLOR} !important;
    min-width: 310px !important;
    max-width: 360px !important;
}}

[data-testid="stSidebarContent"] {{
    padding: 1.5rem 1.25rem 2rem 1.25rem !important;
}}

/* Sidebar radio labels */
section[data-testid="stSidebar"] .stRadio label {{
    font-family: 'Montserrat', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.90rem !important;
    color: {NAVY} !important;
    padding: 6px 10px !important;
    border-radius: 6px !important;
    margin-bottom: 3px !important;
}}

/* --- SCOPED MAIN CONTAINER TYPOGRAPHY --- */
[data-testid="stAppViewContainer"] {{
    background-color: #FFFFFF;
    font-family: 'Montserrat', -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
}}

.main .block-container {{
    padding-top: 1.8rem !important;
    padding-bottom: 3rem !important;
    max-width: 1400px !important;
}}

.main p, .main span, .main label, .main li {{
    font-family: 'Montserrat', sans-serif;
    color: {BODY_TEXT};
}}

/* Headings */
h1, h2, h3, h4, h5, h6 {{
    font-family: 'Montserrat', sans-serif !important;
    color: {NAVY} !important;
    font-weight: 700 !important;
    letter-spacing: -0.2px;
}}

/* Category Pink Tag */
.pink-tag {{
    font-size: 0.74rem;
    font-weight: 700;
    color: {PINK};
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 3px;
    display: inline-block;
}}

/* Main Page Title */
.page-title {{
    font-size: 1.80rem;
    font-weight: 700;
    color: {NAVY};
    line-height: 1.2;
    margin-top: 0;
    margin-bottom: 4px;
}}

/* Author Line */
.author-line {{
    font-size: 0.84rem;
    color: {MUTED_TEXT};
    font-weight: 500;
    margin-bottom: 12px;
}}

.title-rule {{
    border-bottom: 1px solid {BORDER_COLOR};
    margin-bottom: 14px;
}}

/* Key Metrics Strip */
.key-strip {{
    background-color: {PANEL_BG};
    border-radius: 6px;
    padding: 10px 14px;
    margin-bottom: 16px;
    border: 1px solid {BORDER_COLOR};
}}

.metric-box {{
    text-align: center;
    padding: 2px 8px;
}}

.metric-val {{
    font-size: 1.30rem;
    font-weight: 700;
    color: {NAVY};
    font-variant-numeric: tabular-nums;
    line-height: 1.2;
}}

.metric-lbl {{
    font-size: 0.68rem;
    font-weight: 700;
    color: {PINK};
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: 2px;
}}

/* Styled Data Tables (Top 10 Batters & Bowlers) */
.report-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 0.84rem;
    margin-bottom: 8px;
}}

.report-table th {{
    background-color: {PANEL_BG};
    color: {PINK};
    text-transform: uppercase;
    font-size: 0.70rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    padding: 7px 10px;
    border-bottom: 2px solid {NAVY};
}}

.report-table td {{
    padding: 6px 10px;
    border-bottom: 1px solid {BORDER_COLOR};
    font-size: 0.83rem;
}}

.report-table tr.row-credible {{
    background-color: {GREEN_TINT} !important;
}}

.report-table tr:hover {{
    background-color: #F8F9FC;
}}

.symbol-dot {{
    color: {PINK};
    font-weight: bold;
    margin-right: 5px;
}}

.val-neg {{
    color: {MUTED_RED} !important;
    font-weight: 600;
}}

.val-pos {{
    color: {GREEN_TEXT} !important;
    font-weight: 600;
}}

/* Table Guide Box */
.guide-box {{
    background-color: {PANEL_BG};
    border-left: 3px solid {NAVY};
    border-radius: 0 4px 4px 0;
    padding: 8px 12px;
    font-size: 0.80rem;
    line-height: 1.45;
    color: {BODY_TEXT};
    margin-top: 10px;
    margin-bottom: 14px;
}}

/* Card containers */
.stat-card {{
    background-color: #FFFFFF;
    border: 1px solid {BORDER_COLOR};
    border-radius: 6px;
    padding: 14px;
    margin-bottom: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
}}

/* Info / Methodology Card */
.info-card {{
    background-color: {PANEL_BG};
    border: 1px solid {BORDER_COLOR};
    border-radius: 6px;
    padding: 12px 16px;
    margin-bottom: 12px;
}}

/* Footer */
.footer-text {{
    font-size: 0.78rem;
    color: {MUTED_TEXT};
    text-align: center;
    padding-top: 22px;
    padding-bottom: 14px;
    border-top: 1px solid {BORDER_COLOR};
    margin-top: 32px;
}}
</style>
"""

def inject_theme():
    """Injects custom CSS matching the report styling."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

def apply_plotly_theme(fig, height=450, title=None, show_legend=True):
    """Applies standardized font, grid, and color palette to Plotly figures without deprecated properties."""
    fig.update_layout(
        template="plotly_white",
        height=height,
        title=dict(
            text=title if title else "",
            font=dict(family="Montserrat, Inter, sans-serif", size=14, color=NAVY),
            x=0.01,
            y=0.96
        ) if title else None,
        font=dict(
            family="Montserrat, Inter, sans-serif",
            size=12,
            color=BODY_TEXT
        ),
        paper_bgcolor=WHITE,
        plot_bgcolor=WHITE,
        margin=dict(l=45, r=25, t=45 if title else 25, b=45),
        xaxis=dict(
            showgrid=True,
            gridcolor=BORDER_COLOR,
            gridwidth=1,
            zeroline=True,
            zerolinecolor=NAVY,
            zerolinewidth=1,
            tickfont=dict(size=11, color=BODY_TEXT),
            title=dict(font=dict(size=12, color=NAVY))
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=BORDER_COLOR,
            gridwidth=1,
            zeroline=True,
            zerolinecolor=NAVY,
            zerolinewidth=1,
            tickfont=dict(size=11, color=BODY_TEXT),
            title=dict(font=dict(size=12, color=NAVY))
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11, color=BODY_TEXT),
            bgcolor="rgba(255,255,255,0.8)"
        ) if show_legend else dict(visible=False),
        hoverlabel=dict(
            bgcolor=NAVY,
            font_size=12,
            font_family="Montserrat, sans-serif",
            font_color=WHITE
        )
    )
    return fig
