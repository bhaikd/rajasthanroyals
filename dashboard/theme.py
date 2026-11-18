"""
dashboard/theme.py - Theme and CSS configuration for the SupeRR Selector Dashboard.
Matches the styling and typography of the methodology report PDF in Light Mode,
and provides a rich, elegant Dark Mode with a single toggle button.
"""
import plotly.graph_objects as go
import streamlit as st

def get_theme_colors():
    """Returns color dictionary based on current dark/light mode state."""
    is_dark = st.session_state.get("dark_mode", False)
    if is_dark:
        return {
            "NAVY": "#F8FAFC",              # Bright slate-white for titles & prominent text
            "PRIMARY_TEXT": "#F8FAFC",      # Main text
            "BODY_TEXT": "#CBD5E1",         # General paragraph text
            "MUTED_TEXT": "#94A3B8",        # Subtext & metadata
            "PINK": "#FF2A9D",              # Electric neon pink for batters & accents
            "BATTER_COLOR": "#FF2A9D",
            "BOWLER_COLOR": "#38BDF8",      # Crisp sky cyan for bowlers
            "PANEL_BG": "#0F172A",          # Dark slate container background
            "WHITE": "#0A0F1D",             # Primary dark page background
            "CARD_BG": "#0F172A",
            "BORDER_COLOR": "#1E293B",      # Subtle dark border
            "GREEN_TINT": "rgba(30, 126, 52, 0.35)", # Highlight for credible players
            "GREEN_TEXT": "#4ADE80",        # Bright green
            "MUTED_RED": "#F87171",         # Soft bright red for negative delta
            "NULL_BAND_BG": "#1E2D4A",
            "NULL_BAND_BORDER": "#334B77",
            "CODE_BG": "#162038",
            "HOVER_BG": "#162038"
        }
    else:
        return {
            "NAVY": "#021D45",              # Deep RR Navy
            "PRIMARY_TEXT": "#0B1F44",
            "BODY_TEXT": "#1F2A44",
            "MUTED_TEXT": "#606F89",
            "PINK": "#E50695",              # RR Pink
            "BATTER_COLOR": "#E50695",
            "BOWLER_COLOR": "#021D45",
            "PANEL_BG": "#F4F6FA",
            "WHITE": "#FFFFFF",
            "CARD_BG": "#FFFFFF",
            "BORDER_COLOR": "#E2E6EE",
            "GREEN_TINT": "#E8F5EC",
            "GREEN_TEXT": "#1E7E34",
            "MUTED_RED": "#C0392B",
            "NULL_BAND_BG": "#F4F6FA",
            "NULL_BAND_BORDER": "#CBD5E0",
            "CODE_BG": "#FAFAFC",
            "HOVER_BG": "#F8F9FC"
        }

# Initial default values for module-level export
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
NULL_BAND_BG = colors["NULL_BAND_BG"]
NULL_BAND_BORDER = colors["NULL_BAND_BORDER"]

def get_css(is_dark=False):
    c = get_theme_colors()
    if is_dark:
        return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400;1,600&display=swap');

/* --- TOP HEADER BAR --- */
header[data-testid="stHeader"] {{
    background-color: #0A0F1D !important;
    border-bottom: 1px solid #1E293B !important;
    z-index: 99999 !important;
}}

header[data-testid="stHeader"] button,
header[data-testid="stHeader"] svg,
header[data-testid="stHeader"] span {{
    color: #F8FAFC !important;
    fill: #F8FAFC !important;
}}

/* --- SIDEBAR STYLING --- */
section[data-testid="stSidebar"] {{
    background-color: #0F172A !important;
    border-right: 1px solid #1E293B !important;
    min-width: 310px !important;
    max-width: 360px !important;
}}

[data-testid="stSidebarContent"] {{
    padding: 1.5rem 1.25rem 2rem 1.25rem !important;
}}

section[data-testid="stSidebar"] .stRadio label {{
    font-family: 'Montserrat', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.90rem !important;
    color: #F1F5F9 !important;
    padding: 6px 10px !important;
    border-radius: 6px !important;
    margin-bottom: 3px !important;
}}

section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div {{
    color: #CBD5E1 !important;
}}

/* --- SCOPED MAIN CONTAINER TYPOGRAPHY --- */
[data-testid="stAppViewContainer"] {{
    background-color: #0A0F1D !important;
    font-family: 'Montserrat', -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
}}

.main .block-container {{
    padding-top: 1.8rem !important;
    padding-bottom: 3rem !important;
    max-width: 1400px !important;
}}

.main p, .main span, .main label, .main li {{
    font-family: 'Montserrat', sans-serif;
    color: #CBD5E1;
}}

/* Headings */
h1, h2, h3, h4, h5, h6 {{
    font-family: 'Montserrat', sans-serif !important;
    color: #F8FAFC !important;
    font-weight: 700 !important;
    letter-spacing: -0.2px;
}}

/* Category Pink Tag */
.pink-tag {{
    font-size: 0.74rem;
    font-weight: 700;
    color: #FF2A9D;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 3px;
    display: inline-block;
}}

/* Main Page Title */
.page-title {{
    font-size: 1.80rem;
    font-weight: 700;
    color: #F8FAFC;
    line-height: 1.2;
    margin-top: 0;
    margin-bottom: 4px;
}}

/* Author Line */
.author-line {{
    font-size: 0.84rem;
    color: #94A3B8;
    font-weight: 500;
    margin-bottom: 12px;
}}

.title-rule {{
    border-bottom: 1px solid #1E293B;
    margin-bottom: 14px;
}}

/* Key Metrics Strip */
.key-strip {{
    background-color: #0F172A;
    border-radius: 6px;
    padding: 10px 14px;
    margin-bottom: 16px;
    border: 1px solid #1E293B;
}}

.metric-box {{
    text-align: center;
    padding: 2px 8px;
}}

.metric-val {{
    font-size: 1.30rem;
    font-weight: 700;
    color: #F8FAFC;
    font-variant-numeric: tabular-nums;
    line-height: 1.2;
}}

.metric-lbl {{
    font-size: 0.68rem;
    font-weight: 700;
    color: #FF2A9D;
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
    background-color: #0F172A;
    color: #FF2A9D;
    text-transform: uppercase;
    font-size: 0.70rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    padding: 7px 10px;
    border-bottom: 2px solid #38BDF8;
}}

.report-table td {{
    padding: 6px 10px;
    border-bottom: 1px solid #1E293B;
    font-size: 0.83rem;
    color: #CBD5E1;
}}

.report-table tr.row-credible {{
    background-color: rgba(30, 126, 52, 0.35) !important;
}}

.report-table tr:hover {{
    background-color: #162038;
}}

.symbol-dot {{
    color: #FF2A9D;
    font-weight: bold;
    margin-right: 5px;
}}

.val-neg {{
    color: #F87171 !important;
    font-weight: 600;
}}

.val-pos {{
    color: #4ADE80 !important;
    font-weight: 600;
}}

/* Table Guide Box */
.guide-box {{
    background-color: #131E38;
    border-left: 3px solid #38BDF8;
    border-radius: 0 4px 4px 0;
    padding: 8px 12px;
    font-size: 0.80rem;
    line-height: 1.45;
    color: #CBD5E1;
    margin-top: 10px;
    margin-bottom: 14px;
}}

/* Card containers */
.stat-card {{
    background-color: #0F172A;
    border: 1px solid #1E293B;
    border-radius: 6px;
    padding: 14px;
    margin-bottom: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.25);
    color: #CBD5E1;
}}

/* Info / Methodology Card */
.info-card {{
    background-color: #131E38;
    border: 1px solid #1E293B;
    border-radius: 6px;
    padding: 12px 16px;
    margin-bottom: 12px;
    color: #CBD5E1;
}}

/* Footer */
.footer-text {{
    font-size: 0.78rem;
    color: #94A3B8;
    text-align: center;
    padding-top: 22px;
    padding-bottom: 14px;
    border-top: 1px solid #1E293B;
    margin-top: 32px;
}}

/* Dark Mode Button Styling */
button[key="theme_toggle_btn"] {{
    background-color: #1E293B !important;
    color: #F8FAFC !important;
    border: 1px solid #334155 !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease-in-out;
}}
button[key="theme_toggle_btn"]:hover {{
    background-color: #334155 !important;
    border-color: #FF2A9D !important;
    color: #FF2A9D !important;
}}
</style>
"""
    else:
        return f"""
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
    color: #0B1F44 !important;
    fill: #0B1F44 !important;
}}

/* --- SIDEBAR STYLING & FIX PADDING/CLIPPING --- */
section[data-testid="stSidebar"] {{
    background-color: #F4F6FA !important;
    border-right: 1px solid #E2E6EE !important;
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
    color: #021D45 !important;
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
    color: #1F2A44;
}}

/* Headings */
h1, h2, h3, h4, h5, h6 {{
    font-family: 'Montserrat', sans-serif !important;
    color: #021D45 !important;
    font-weight: 700 !important;
    letter-spacing: -0.2px;
}}

/* Category Pink Tag */
.pink-tag {{
    font-size: 0.74rem;
    font-weight: 700;
    color: #E50695;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 3px;
    display: inline-block;
}}

/* Main Page Title */
.page-title {{
    font-size: 1.80rem;
    font-weight: 700;
    color: #021D45;
    line-height: 1.2;
    margin-top: 0;
    margin-bottom: 4px;
}}

/* Author Line */
.author-line {{
    font-size: 0.84rem;
    color: #606F89;
    font-weight: 500;
    margin-bottom: 12px;
}}

.title-rule {{
    border-bottom: 1px solid #E2E6EE;
    margin-bottom: 14px;
}}

/* Key Metrics Strip */
.key-strip {{
    background-color: #F4F6FA;
    border-radius: 6px;
    padding: 10px 14px;
    margin-bottom: 16px;
    border: 1px solid #E2E6EE;
}}

.metric-box {{
    text-align: center;
    padding: 2px 8px;
}}

.metric-val {{
    font-size: 1.30rem;
    font-weight: 700;
    color: #021D45;
    font-variant-numeric: tabular-nums;
    line-height: 1.2;
}}

.metric-lbl {{
    font-size: 0.68rem;
    font-weight: 700;
    color: #E50695;
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
    background-color: #F4F6FA;
    color: #E50695;
    text-transform: uppercase;
    font-size: 0.70rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    padding: 7px 10px;
    border-bottom: 2px solid #021D45;
}}

.report-table td {{
    padding: 6px 10px;
    border-bottom: 1px solid #E2E6EE;
    font-size: 0.83rem;
}}

.report-table tr.row-credible {{
    background-color: #E8F5EC !important;
}}

.report-table tr:hover {{
    background-color: #F8F9FC;
}}

.symbol-dot {{
    color: #E50695;
    font-weight: bold;
    margin-right: 5px;
}}

.val-neg {{
    color: #C0392B !important;
    font-weight: 600;
}}

.val-pos {{
    color: #1E7E34 !important;
    font-weight: 600;
}}

/* Table Guide Box */
.guide-box {{
    background-color: #F4F6FA;
    border-left: 3px solid #021D45;
    border-radius: 0 4px 4px 0;
    padding: 8px 12px;
    font-size: 0.80rem;
    line-height: 1.45;
    color: #1F2A44;
    margin-top: 10px;
    margin-bottom: 14px;
}}

/* Card containers */
.stat-card {{
    background-color: #FFFFFF;
    border: 1px solid #E2E6EE;
    border-radius: 6px;
    padding: 14px;
    margin-bottom: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
}}

/* Info / Methodology Card */
.info-card {{
    background-color: #F4F6FA;
    border: 1px solid #E2E6EE;
    border-radius: 6px;
    padding: 12px 16px;
    margin-bottom: 12px;
}}

/* Footer */
.footer-text {{
    font-size: 0.78rem;
    color: #606F89;
    text-align: center;
    padding-top: 22px;
    padding-bottom: 14px;
    border-top: 1px solid #E2E6EE;
    margin-top: 32px;
}}

/* Light Mode Button Styling */
button[key="theme_toggle_btn"] {{
    background-color: #FFFFFF !important;
    color: #021D45 !important;
    border: 1px solid #E2E6EE !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease-in-out;
}}
button[key="theme_toggle_btn"]:hover {{
    background-color: #F4F6FA !important;
    border-color: #E50695 !important;
    color: #E50695 !important;
}}
</style>
"""

def inject_theme():
    """Injects custom CSS matching either the light or dark mode styling."""
    is_dark = st.session_state.get("dark_mode", False)
    st.markdown(get_css(is_dark), unsafe_allow_html=True)

def apply_plotly_theme(fig, height=450, title=None, show_legend=True):
    """Applies standardized font, grid, and color palette to Plotly figures according to active theme."""
    is_dark = st.session_state.get("dark_mode", False)
    c = get_theme_colors()
    
    fig.update_layout(
        template="plotly_dark" if is_dark else "plotly_white",
        height=height,
        title=dict(
            text=title if title else "",
            font=dict(family="Montserrat, Inter, sans-serif", size=14, color=c["NAVY"]),
            x=0.01,
            y=0.96
        ) if title else None,
        font=dict(
            family="Montserrat, Inter, sans-serif",
            size=12,
            color=c["BODY_TEXT"]
        ),
        paper_bgcolor=c["PANEL_BG"] if is_dark else c["WHITE"],
        plot_bgcolor=c["PANEL_BG"] if is_dark else c["WHITE"],
        margin=dict(l=45, r=25, t=45 if title else 25, b=45),
        xaxis=dict(
            showgrid=True,
            gridcolor=c["BORDER_COLOR"],
            gridwidth=1,
            zeroline=True,
            zerolinecolor=c["BOWLER_COLOR"] if is_dark else c["NAVY"],
            zerolinewidth=1,
            tickfont=dict(size=11, color=c["BODY_TEXT"]),
            title=dict(font=dict(size=12, color=c["NAVY"]))
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=c["BORDER_COLOR"],
            gridwidth=1,
            zeroline=True,
            zerolinecolor=c["BOWLER_COLOR"] if is_dark else c["NAVY"],
            zerolinewidth=1,
            tickfont=dict(size=11, color=c["BODY_TEXT"]),
            title=dict(font=dict(size=12, color=c["NAVY"]))
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11, color=c["BODY_TEXT"]),
            bgcolor="rgba(15, 23, 42, 0.85)" if is_dark else "rgba(255,255,255,0.8)"
        ) if show_legend else dict(visible=False),
        hoverlabel=dict(
            bgcolor="#1E293B" if is_dark else c["NAVY"],
            font_size=12,
            font_family="Montserrat, sans-serif",
            font_color="#F8FAFC" if is_dark else c["WHITE"]
        )
    )
    return fig
