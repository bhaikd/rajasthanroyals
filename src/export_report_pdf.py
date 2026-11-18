"""
Stage 6: PDF Methodology Report Exporter
- Compact, publication-grade 3-page PDF layout using ReportLab.
- Meets all requirements:
  * Neutral header and footer: "SupeRR Selector Season 2 - Round 1 Submission"
  * Author line strictly the participant's registered name: "Kishalay Das"
  * Executive Summary lists all 6 top-10 players with 90% Delta CI > 0 (Suryakumar, Hendricks, Rinku, Iyer, Pathirana, Santner), uses "indicate"
  * Calibration: explains out-of-fold recentering to zero; notes xW AUC 0.595 noise limitation
  * Deletes every reference to "earlier drafts" across the codebase
  * Documents opposition adjustment diagnostics (with vs without opp; Varun drops #8 to #13, Santner #10 to #12; Hasaranga & Kuldeep enter)
  * Lists sensitivity analysis across all 14 specifications
  * Table 4.1 reports actual full-cohort vs filtered-cohort parameters side by side (REML, K, null test, means, Kohli & Rohit)
  * Sanity diagnostics table includes delivery-level stats for Kohli (+17.52, Rk 16) and Rohit (+5.40, Rk 117)
- Strictly 3 pages, zero unrendered LaTeX.
export_report_pdf.py - Publication-Grade A4 Layout Methodology Report Generator

Produces a 5-page publication-grade PDF adhering to strict layout requirements:
- Exactly 5 pages, no wasted space, intentional visual hierarchy.
- Preserves 100% of all analytical numbers, rankings, player statistics, and text.
- Full text width tables (505 pt), single-line headers, zebra striping, thin borders.
- Full text width calibration charts and high-resolution forest plots.
- Slim top header and bottom footer with dynamic page numbering (Page X of N).
"""
import os
import sys
import shutil
from pathlib import Path
import pandas as pd
import numpy as np

from reportlab.lib.pagesizes import letter
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, Image
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, Image, HRFlowable
)
from reportlab.pdfgen import canvas

sys.path.append(str(Path(__file__).resolve().parent.parent))
from src.config import REPORT_DIR, OUTPUTS_DIR
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = BASE_DIR / "outputs"
REPORT_DIR = BASE_DIR / "report"

class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and print total page numbers."""
PAGE_WIDTH, PAGE_HEIGHT = A4  # 595.27 x 841.89 pt
MARGIN_LEFT = 45.0
MARGIN_RIGHT = 45.0
MARGIN_TOP = 45.0
MARGIN_BOTTOM = 45.0
CONTENT_WIDTH = PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT  # 505.27 pt
PRINTABLE_HEIGHT = PAGE_HEIGHT - MARGIN_TOP - MARGIN_BOTTOM  # 751.89 pt

class A4NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and print total page count
    along with running header and footer furniture.
    """
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        super(A4NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()
            self.draw_page_furniture(num_pages)
            super(A4NumberedCanvas, self).showPage()
        super(A4NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
    def draw_page_furniture(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 7.5)
        # Slim top header
        self.setFont("Helvetica-Bold", 8.0)
        self.setFillColor(colors.HexColor("#004B87"))
        self.drawString(18, 774, "SupeRR Selector Season 2 - Round 1 Submission")
        self.drawString(MARGIN_LEFT, PAGE_HEIGHT - 28, "SupeRR Selector Season 2 – Round 1 Methodology Report")
        
        self.setFont("Helvetica", 7.5)
        self.setFont("Helvetica", 8.0)
        self.setFillColor(colors.HexColor("#555555"))
        self.drawRightString(594, 774, "Hierarchical REML Clutch Impact Engine")
        self.drawRightString(PAGE_WIDTH - MARGIN_RIGHT, PAGE_HEIGHT - 28, "SupeRR Selector Season 2 - Round 1")
        
        self.setStrokeColor(colors.HexColor("#004B87"))
        self.setLineWidth(0.6)
        self.line(18, 770, 594, 770)
        self.line(MARGIN_LEFT, PAGE_HEIGHT - 32, PAGE_WIDTH - MARGIN_RIGHT, PAGE_HEIGHT - 32)
        
        # Slim bottom footer
        self.setStrokeColor(colors.HexColor("#CCCCCC"))
        self.setLineWidth(0.5)
        self.line(18, 22, 594, 22)
        self.line(MARGIN_LEFT, 34, PAGE_WIDTH - MARGIN_RIGHT, 34)
        
        self.setFont("Helvetica-Bold", 7.5)
        self.setFont("Helvetica-Bold", 8.0)
        self.setFillColor(colors.HexColor("#004B87"))
        self.drawString(18, 12, "SupeRR Selector Season 2 - Round 1 Submission")
        self.drawString(MARGIN_LEFT, 22, "SupeRR Selector Season 2 - Round 1 Submission")
        
        self.setFont("Helvetica", 7.5)
        self.setFont("Helvetica", 8.0)
        self.setFillColor(colors.HexColor("#444444"))
        self.drawRightString(594, 12, f"Page {self._pageNumber} of {page_count}")
        self.drawRightString(PAGE_WIDTH - MARGIN_RIGHT, 22, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()

class NumberedCanvasDocTemplate(SimpleDocTemplate):
    def build(self, flowables, canvasmaker=NumberedCanvas):
class A4DocTemplate(SimpleDocTemplate):
    def build(self, flowables, canvasmaker=A4NumberedCanvas):
        super().build(flowables, canvasmaker=canvasmaker)
        self.page_count = len(self.canv._saved_page_states) if hasattr(self, 'canv') and hasattr(self.canv, '_saved_page_states') else 3
        self.page_count = len(self.canv._saved_page_states) if hasattr(self, 'canv') and hasattr(self.canv, '_saved_page_states') else 5
        print(f"[+] Total PDF Pages Generated: {self.page_count}")

def export_pdf():
    print("=" * 80)
    print("STAGE 6: GENERATING METHODOLOGY REPORT PDF (STRICTLY 3 PAGES)")
    print("=" * 80)
def build_pdf(target_path):
    target_path = Path(target_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    pdf_path = REPORT_DIR / "methodology_report.pdf"
    doc = NumberedCanvasDocTemplate(
        str(pdf_path),
        pagesize=letter,
        leftMargin=18,
        rightMargin=18,
        topMargin=24,
        bottomMargin=24
    doc = A4DocTemplate(
        str(target_path),
        pagesize=A4,
        leftMargin=MARGIN_LEFT,
        rightMargin=MARGIN_RIGHT,
        topMargin=MARGIN_TOP,
        bottomMargin=MARGIN_BOTTOM
    )

    styles = getSampleStyleSheet()

    # Typography styles
    title_style = ParagraphStyle(
        'DocTitle',
        fontName='Helvetica-Bold',
        fontSize=12.5,
        leading=13.5,
        fontSize=16.5,
        leading=19.5,
        textColor=colors.HexColor('#004B87'),
        spaceAfter=1
        spaceAfter=1.5
    )
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        fontName='Helvetica-Bold',
        fontSize=7.8,
        leading=8.8,
        fontSize=9.8,
        leading=12.2,
        textColor=colors.HexColor('#E21A5C'),
        spaceAfter=1.5
        spaceAfter=2.0
    )
    meta_style = ParagraphStyle(
        'DocMeta',
        fontName='Helvetica',
        fontSize=6.6,
        leading=7.6,
        textColor=colors.HexColor('#444444'),
        spaceAfter=2
        fontSize=8.2,
        leading=10.5,
        textColor=colors.HexColor('#555555'),
        spaceAfter=2.5
    )
    h1_style = ParagraphStyle(
        'SectionH1',
        fontName='Helvetica-Bold',
        fontSize=8.2,
        leading=9.2,
        fontSize=11.5,
        leading=13.8,
        textColor=colors.HexColor('#004B87'),
        spaceBefore=1.5,
        spaceAfter=1.0,
        spaceBefore=2.5,
        spaceAfter=1.2,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        'SectionH2',
        fontName='Helvetica-Bold',
        fontSize=7.0,
        leading=8.0,
        fontSize=8.8,
        leading=10.8,
        textColor=colors.HexColor('#222222'),
        spaceBefore=1.2,
        spaceAfter=0.8,
        spaceBefore=1.8,
        spaceAfter=1.0,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'BodyDark',
        'BodyTextCustom',
        fontName='Helvetica',
        fontSize=5.9,
        leading=7.1,
        textColor=colors.HexColor('#222222'),
        spaceAfter=1.2
        fontSize=8.2,
        leading=10.3,
        textColor=colors.HexColor('#1A1A1A'),
        spaceAfter=1.8
    )
    bullet_style = ParagraphStyle(
        'BulletCustom',
        fontName='Helvetica',
        fontSize=7.8,
        leading=9.8,
        textColor=colors.HexColor('#1A1A1A'),
        leftIndent=8,
        spaceAfter=1.0
    )
    caption_style = ParagraphStyle(
        'CaptionStyle',
        fontName='Helvetica-Oblique',
        fontSize=7.0,
        leading=8.3,
        textColor=colors.HexColor('#444444'),
        spaceBefore=1.0,
        spaceAfter=2.0,
        keepWithNext=False
    )
    callout_style = ParagraphStyle(
        'CalloutText',
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.4,
        textColor=colors.HexColor('#004B87')
    )

    # Table styles
    table_cell_style = ParagraphStyle(
        'TableCell',
        fontName='Helvetica',
        fontSize=5.5,
        leading=6.5,
        fontSize=6.8,
        leading=8.1,
        textColor=colors.HexColor('#111111')
    )
    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        fontName='Helvetica-Bold',
        fontSize=5.5,
        leading=6.5,
        fontSize=6.8,
        leading=8.1,
        textColor=colors.HexColor('#111111')
    )
    table_cell_header = ParagraphStyle(
        'TableHeader',
        fontName='Helvetica-Bold',
        fontSize=5.6,
        leading=6.6,
        fontSize=6.8,
        leading=8.1,
        textColor=colors.white
    )

    story = []

    # =========================================================================
    # PAGE 1: Title, Executive Summary, Combined Top 10 Table, Section 1
    # PAGE 1: Title, Executive Summary, Key Design Choices, Table 1 (Top 10)
    # =========================================================================
    story.append(Paragraph("SupeRR Selector Season 2 – Round 1 Methodology Report", title_style))
    story.append(Paragraph("Identifying the Most Reliable Players Under Pressure in T20 Cricket (2022 Onwards)", subtitle_style))
    story.append(Paragraph("<b>Author:</b> Kishalay Das &nbsp;|&nbsp; <b>Dataset:</b> 883 Matches, 200,999 Deliveries (IPL & T20I)", meta_style))
    story.append(Paragraph("<b>Author:</b> Kishalay Das &nbsp;|&nbsp; <b>Dataset:</b> 883 Matches, 200,999 Deliveries (IPL & T20I) &nbsp;|&nbsp; <b>Submission:</b> Round 1", meta_style))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#004B87"), spaceBefore=1, spaceAfter=2.5))

    story.append(Paragraph("Executive Summary", h1_style))
    story.append(Paragraph(
        "Evaluating clutch performance in T20 cricket requires disentangling genuine repeatable skill from extreme small-sample noise. "
        "We built an end-to-end sabermetric pipeline across 883 IPL and T20I matches from 2022 onwards (200,999 deliveries). "
        "Players representing Pakistan or Pakistan A are excluded from both rankings as an eligibility choice made by the author; this is not required by the dataset or the problem statement. "
        "<b>Explicit Ordering Rule:</b> Primary selections are strictly ranked in descending order of their total hierarchical posterior mean impact rating (Rating = Shrunk Baseline + Shrunk Pressure Delta). "
        "90% credible intervals indicate that six top-10 players—<b>Suryakumar Yadav, Reeza Hendricks, Rinku Singh, Shreyas Iyer, Matheesha Pathirana, and Mitchell Santner</b>—possess clutch pressure elevation (Delta) strictly above zero at the 90% credibility level, while all other players remain statistically indistinguishable from zero or exhibit pressure dips. "
        "<b>Core Pillars:</b> (1) <i>Outcome Leverage:</i> Formulated strictly as expected absolute win-probability swing across all 7 delivery outcomes, weighted by phase transition probabilities (Top 25% defines High Pressure, 50,241 balls). "
        "(2) <i>Empirical Calibration:</i> Out-of-fold GroupKFold LightGBM models (xR and xW) were recentred by subtracting residual means so league-wide residuals average 0.000 (1.7e-17 runs/ball, -1.3e-18 outs/ball). Expected wicket models achieve ROC-AUC 0.595, reflecting that dismissals carry substantial single-delivery noise. Win-probability models yield Brier scores of 0.2303 (Innings 1) and 0.1555 (Innings 2). Non-Pakistan regulars (>= 100 HP balls) hold positive baseline means (+3.51 runs/100b bat, +1.57 runs saved/100b bowl) because tailenders absorb negative residuals. "
        "(3) <i>Phase-Specific Wickets:</i> Evaluated at 14.36 runs (Powerplay), 8.13 runs (Middle), and 2.92 runs (Death); weighted mean 8.85 runs. High-pressure recomputation yields 14.40 runs (Powerplay), 10.71 runs (Middle), and 5.89 runs (Death). "
        "(4) <i>Hierarchical REML Decomposition:</i> Performance is decomposed into Ordinary Baseline (B_i) plus Pressure Elevation (Delta_i): Rating = B_shrunk + Delta_shrunk. Parameters are shrunk via REML (K_B = 1717.4 bat, 1312.9 bowl; K_Delta = 773.0 bat, 1041.4 bowl; typical HP weight = 24.8% bat, 19.1% bowl). K values were estimated on the full cohort, while population means and ratings use the filtered (non-Pakistan) cohort; the filtered-cohort K values are shown in Table 4.1. "
        "(5) <i>Null Permutation & Single Bootstrap:</i> 1,000 within-match permutations confirm statistically distinguishable bowling control (p = 0.0300 filtered, 0.0060 full) vs borderline batting variance (p = 0.0440 filtered, 0.0500 full). A single 1,000-draw bootstrap (seed 42) ensures identical intervals and P(Top 10) across all exhibits.",
        "90% credible intervals indicate that six top-10 players—<b>Suryakumar Yadav, Reeza Hendricks, Rinku Singh, Shreyas Iyer, Matheesha Pathirana, and Mitchell Santner</b>—possess clutch pressure elevation (Delta) strictly above zero at the 90% credibility level, while all other players remain statistically indistinguishable from zero or exhibit pressure dips.",
        body_style
    ))

    # Combined Executive Summary Table (13 columns, perfectly dimensioned)
    # Core Pillars / Key Design Choices (6 structured bullets)
    story.append(Paragraph("<b>Core Pillars & Methodology Choices:</b>", h2_style))
    story.append(Paragraph("• <b>(1) Outcome Leverage:</b> Formulated strictly as expected absolute win-probability swing across all 7 delivery outcomes, weighted by phase transition probabilities (Top 25% defines High Pressure, 50,241 balls).", bullet_style))
    story.append(Paragraph("• <b>(2) Empirical Calibration:</b> Out-of-fold GroupKFold LightGBM models (xR and xW) were recentred by subtracting residual means so league-wide residuals average 0.000 (1.7e-17 runs/ball, -1.3e-18 outs/ball). Expected wicket models achieve ROC-AUC 0.595, reflecting that dismissals carry substantial single-delivery noise. Win-probability models yield Brier scores of 0.2303 (Innings 1) and 0.1555 (Innings 2). Non-Pakistan regulars (>= 100 HP balls) hold positive baseline means (+3.51 runs/100b bat, +1.57 runs saved/100b bowl) because tailenders absorb negative residuals.", bullet_style))
    story.append(Paragraph("• <b>(3) Phase-Specific Wickets:</b> Evaluated at 14.36 runs (Powerplay), 8.13 runs (Middle), and 2.92 runs (Death); weighted mean 8.85 runs. High-pressure recomputation yields 14.40 runs (Powerplay), 10.71 runs (Middle), and 5.89 runs (Death).", bullet_style))
    story.append(Paragraph("• <b>(4) Hierarchical REML Decomposition:</b> Performance is decomposed into Ordinary Baseline (B_i) plus Pressure Elevation (Delta_i): Rating = B_shrunk + Delta_shrunk. Parameters are shrunk via REML (K_B = 1717.4 bat, 1312.9 bowl; K_Delta = 773.0 bat, 1041.4 bowl; typical HP weight = 24.8% bat, 19.1% bowl). K values were estimated on the full cohort, while population means and ratings use the filtered (non-Pakistan) cohort; the filtered-cohort K values are shown in Table 4.1.", bullet_style))
    story.append(Paragraph("• <b>(5) Null Permutation & Single Bootstrap:</b> 1,000 within-match permutations confirm statistically distinguishable bowling control (p = 0.0300 filtered, 0.0060 full) vs borderline batting variance (p = 0.0440 filtered, 0.0500 full). A single 1,000-draw bootstrap (seed 42) ensures identical intervals and P(Top 10) across all exhibits.", bullet_style))
    story.append(Paragraph("• <b>(6) Eligibility & Exclusions:</b> Minimum filters of 100 HP balls, 6 HP matches, and 10 career matches yield 131 eligible batters and 140 eligible bowlers. Players representing Pakistan or Pakistan A are excluded from both rankings as an eligibility choice made by the author; this is not required by the dataset or the problem statement.", bullet_style))

    # Table 1: Final Primary Top 10 Selections
    story.append(Spacer(1, 1))
    story.append(Paragraph("Final Primary Top 10 Selections (Hierarchical Model: Phase-Specific Wickets, No Dip Exclusion)", h2_style))
    exec_data = [
        [
            Paragraph("Rk", table_cell_header),
            Paragraph("Top 10 Batters Under Pressure", table_cell_header),
            Paragraph("Inn (Pos)", table_cell_header),
            Paragraph("Rating", table_cell_header),
            Paragraph("Delta (90% CI)", table_cell_header),
            Paragraph("Succ%", table_cell_header),
            Paragraph("P(T10)", table_cell_header),
            Paragraph("Top 10 Bowlers Under Pressure", table_cell_header),
            Paragraph("Spl (Pos)", table_cell_header),
            Paragraph("Rating", table_cell_header),
            Paragraph("Delta (90% CI)", table_cell_header),
            Paragraph("Succ%", table_cell_header),
            Paragraph("P(T10)", table_cell_header)
        ],
        [
            Paragraph("1", table_cell_bold), Paragraph("Suryakumar Yadav (MI/Ind)", table_cell_style), Paragraph("40 (29)", table_cell_style), Paragraph("+28.39", table_cell_bold), Paragraph("+8.99 [+0.4, +17.1]", table_cell_style), Paragraph("69.4%", table_cell_style), Paragraph("90.3%", table_cell_style),
            Paragraph("Josh Hazlewood (RCB/Aus)", table_cell_style), Paragraph("26 (14)", table_cell_style), Paragraph("+17.83", table_cell_bold), Paragraph("+8.70 [-0.8, +17.9]", table_cell_style), Paragraph("53.5%", table_cell_style), Paragraph("73.5%", table_cell_style)
        ],
        [
            Paragraph("2", table_cell_bold), Paragraph("Vaibhav Sooryavanshi (RR/Ind)", table_cell_style), Paragraph("14 (10)", table_cell_style), Paragraph("+23.89", table_cell_bold), Paragraph("+1.71 [-8.5, +11.3]", table_cell_style), Paragraph("65.3%", table_cell_style), Paragraph("63.2%", table_cell_style),
            Paragraph("Matheesha Pathirana (CSK/SL)", table_cell_style), Paragraph("20 (14)", table_cell_style), Paragraph("+17.48", table_cell_bold), Paragraph("+7.66 [+0.7, +14.2]", table_cell_style), Paragraph("64.9%", table_cell_style), Paragraph("82.7%", table_cell_style)
        ],
        [
            Paragraph("3", table_cell_bold), Paragraph("Jos Buttler (RR/Eng/GT)", table_cell_style), Paragraph("27 (19)", table_cell_style), Paragraph("+23.06", table_cell_bold), Paragraph("+8.68 [-1.5, +17.0]", table_cell_style), Paragraph("66.7%", table_cell_style), Paragraph("62.5%", table_cell_style),
            Paragraph("Sunil Narine (KKR)", table_cell_style), Paragraph("27 (15)", table_cell_style), Paragraph("+14.39", table_cell_bold), Paragraph("+5.32 [-1.4, +11.9]", table_cell_style), Paragraph("54.8%", table_cell_style), Paragraph("56.8%", table_cell_style)
        ],
        [
            Paragraph("4", table_cell_bold), Paragraph("Heinrich Klaasen (SRH/SA)", table_cell_style), Paragraph("18 (15)", table_cell_style), Paragraph("+22.73", table_cell_bold), Paragraph("+6.01 [-2.9, +13.6]", table_cell_style), Paragraph("74.2%", table_cell_style), Paragraph("58.3%", table_cell_style),
            Paragraph("Jasprit Bumrah (MI/Ind)", table_cell_style), Paragraph("34 (17)", table_cell_style), Paragraph("+13.48", table_cell_bold), Paragraph("-5.11 [-13.7, +4.0]", table_cell_style), Paragraph("50.4%", table_cell_style), Paragraph("51.3%", table_cell_style)
        ],
        [
            Paragraph("5", table_cell_bold), Paragraph("Reeza Hendricks (SA)", table_cell_style), Paragraph("14 (11)", table_cell_style), Paragraph("+22.64", table_cell_bold), Paragraph("+14.31 [+5.5, +22.5]", table_cell_style), Paragraph("69.7%", table_cell_style), Paragraph("57.1%", table_cell_style),
            Paragraph("Jacob Duffy (NZ/RCB)", table_cell_style), Paragraph("16 (8)", table_cell_style), Paragraph("+13.10", table_cell_bold), Paragraph("+4.26 [-5.2, +14.2]", table_cell_style), Paragraph("50.7%", table_cell_style), Paragraph("47.1%", table_cell_style)
        ],
        [
            Paragraph("6", table_cell_bold), Paragraph("Abhishek Sharma (SRH/Ind)", table_cell_style), Paragraph("36 (22)", table_cell_style), Paragraph("+21.93", table_cell_bold), Paragraph("-2.25 [-17.6, +11.4]", table_cell_style), Paragraph("60.0%", table_cell_style), Paragraph("53.6%", table_cell_style),
            Paragraph("Rashid Khan (GT/Afg)", table_cell_style), Paragraph("43 (27)", table_cell_style), Paragraph("+12.97", table_cell_bold), Paragraph("+7.27 [-0.4, +14.9]", table_cell_style), Paragraph("61.1%", table_cell_style), Paragraph("44.7%", table_cell_style)
        ],
        [
            Paragraph("7", table_cell_bold), Paragraph("Phil Salt (Eng/DC/KKR)", table_cell_style), Paragraph("25 (16)", table_cell_style), Paragraph("+21.69", table_cell_bold), Paragraph("+5.79 [-6.1, +16.9]", table_cell_style), Paragraph("61.8%", table_cell_style), Paragraph("49.5%", table_cell_style),
            Paragraph("Lockie Ferguson (GT/NZ/RCB)", table_cell_style), Paragraph("18 (10)", table_cell_style), Paragraph("+12.83", table_cell_bold), Paragraph("+8.53 [-1.1, +18.6]", table_cell_style), Paragraph("54.5%", table_cell_style), Paragraph("43.1%", table_cell_style)
        ],
        [
            Paragraph("8", table_cell_bold), Paragraph("Rinku Singh (KKR/Ind)", table_cell_style), Paragraph("16 (15)", table_cell_style), Paragraph("+20.98", table_cell_bold), Paragraph("+12.06 [+3.7, +18.7]", table_cell_style), Paragraph("80.1%", table_cell_style), Paragraph("44.9%", table_cell_style),
            Paragraph("Varun Chakravarthy (KKR)", table_cell_style), Paragraph("42 (25)", table_cell_style), Paragraph("+12.29", table_cell_bold), Paragraph("+0.26 [-7.9, +8.1]", table_cell_style), Paragraph("58.3%", table_cell_style), Paragraph("39.1%", table_cell_style)
        ],
        [
            Paragraph("9", table_cell_bold), Paragraph("Shreyas Iyer (Ind/KKR)", table_cell_style), Paragraph("25 (19)", table_cell_style), Paragraph("+19.97", table_cell_bold), Paragraph("+10.33 [+0.5, +19.8]", table_cell_style), Paragraph("70.7%", table_cell_style), Paragraph("36.5%", table_cell_style),
            Paragraph("Nathan Ellis (PBKS/Aus)", table_cell_style), Paragraph("15 (10)", table_cell_style), Paragraph("+12.26", table_cell_bold), Paragraph("+1.90 [-7.0, +9.7]", table_cell_style), Paragraph("61.6%", table_cell_style), Paragraph("33.9%", table_cell_style)
        ],
        [
            Paragraph("10", table_cell_bold), Paragraph("Tim David (MI/Aus/RCB)", table_cell_style), Paragraph("29 (20)", table_cell_style), Paragraph("+19.75", table_cell_bold), Paragraph("+0.80 [-8.6, +9.8]", table_cell_style), Paragraph("65.8%", table_cell_style), Paragraph("35.1%", table_cell_style),
            Paragraph("Mitchell Santner (CSK/NZ)", table_cell_style), Paragraph("36 (22)", table_cell_style), Paragraph("+12.18", table_cell_bold), Paragraph("+8.02 [+0.3, +15.8]", table_cell_style), Paragraph("59.5%", table_cell_style), Paragraph("39.7%", table_cell_style)
        ],
    ]

    t_exec = Table(exec_data, colWidths=[14, 82, 22, 28, 64, 22, 22, 82, 22, 28, 64, 22, 22])
    t_exec = Table(exec_data, colWidths=[14, 84, 27, 29, 60, 21, 23, 84, 27, 29, 60, 21, 23])
    t_exec.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (6, 0), colors.HexColor('#E21A5C')),
        ('BACKGROUND', (7, 0), (-1, 0), colors.HexColor('#004B87')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0.7),
        ('TOPPADDING', (0, 0), (-1, -1), 0.7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.6),
        ('TOPPADDING', (0, 0), (-1, -1), 1.6),
        ('LEFTPADDING', (0, 0), (-1, -1), 1.5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 1.5),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#DDDDDD')),
        ('GRID', (0, 0), (-1, -1), 0.35, colors.HexColor('#DDDDDD')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')])
    ]))
    story.append(t_exec)
    story.append(Spacer(1, 1.2))
    story.append(Paragraph("Table 1: Final top 10 batters (pink) and bowlers (navy) ranked by posterior mean impact rating (net runs added/saved per 100 balls above context).", caption_style))

    # Section 1: Pressure Definition & Non-Circular Validation
    # Interpretive Callout Box
    t_callout = Table([[
        Paragraph("<b>Rating Interpretation:</b> Ratings denote net context-adjusted runs added (batters) or saved (bowlers) per 100 balls under high pressure relative to league average. Delta represents clutch elevation above ordinary baseline. P(T10) denotes empirical probability of finishing in true top-10 across 1,000 match-grouped bootstrap draws.", callout_style)
    ]], colWidths=[CONTENT_WIDTH])
    t_callout.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F0F4F8')),
        ('BOX', (0,0), (-1,-1), 0.6, colors.HexColor('#004B87')),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t_callout)

    # =========================================================================
    # PAGE 2: Pressure Definition, Calibration & Fair Comparisons
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("1. Pressure Definition, Consistency Metrics & Non-Circular Domain Validation", h1_style))
    story.append(Paragraph(
        "<b>Outcome Leverage Formulation:</b> Leverage = Sum P(outcome | phase) * |WP_sim - WP_now| across 7 delivery outcomes. "
        "GroupKFold LightGBM models yield Brier scores of 0.2303 (Innings 1) and 0.1555 (Innings 2). Top quartile (>= 75th percentile, 50,241 balls) defines High Pressure. "
        "<b>Consistency Metrics & Innings Counts:</b> Success % is defined as Beta-Binomial shrunk positive-impact match rate (alpha=4.97, beta=3.95 bat; alpha=4.22, beta=3.86 bowl). Requiring >= 5 HP balls ensures per-match statistical validity (Suryakumar has 40 qualifying innings with 29 positive, 72.5% raw, 69.4% shrunk; Jos Buttler has 27 qualifying innings with 19 positive, 70.4% raw, 66.7% shrunk; all appearances >= 1 ball are 86 and 82). "
        "<b>Consistency Metrics & Innings Counts:</b> Success % is defined as Beta-Binomial shrunk positive-impact match rate (alpha=4.97, beta=3.95 bat; alpha=4.22, beta=3.86 bowl). "
        "Requiring >= 5 HP balls ensures per-match statistical validity (Suryakumar has 40 qualifying innings with 29 positive, 72.5% raw, 69.4% shrunk; Jos Buttler has 27 qualifying innings with 19 positive, 70.4% raw, 66.7% shrunk; all appearances >= 1 ball are 86 and 82). "
        "<b>Non-Circular Validation:</b> (1) <i>Strike Rotation:</i> Batters significantly increase singles and twos running from 41.85% to 43.24% (+1.39 pp, d = 0.028, p &lt; 1e-10). "
        "(2) <i>Dot Ball Reduction:</i> Dot % drops from 35.59% to 34.42% (-1.17 pp, d = -0.024, p &lt; 1e-10). "
        "(3) <i>Runs Per Ball Variance:</i> Variance narrows from 3.037 to 2.974 (-0.064 var, Levene p = 0.0038). "
        "(4) <i>Run-outs & Stumpings:</i> Desperation dismissals rise from 7.22% to 8.22% (+1.00 pp, d = 0.038), but p = 0.0951 (labeled <b>Not Statistically Significant</b>). "
        "(4) <i>Run-outs &amp; Stumpings:</i> Desperation dismissals rise from 7.22% to 8.22% (+1.00 pp, d = 0.038), but p = 0.0951 (labeled <b>Not Statistically Significant</b>). "
        "(5) <i>Scoring Rates:</i> Run rate is 8.52 vs 8.53 (p = 0.799); boundary % is 18.01% vs 17.81% (p = 0.325). "
        "(6) <i>WP Volatility (Definitional):</i> Average swing per ball surges +126% from 1.59% to 3.60% (+2.00 pp/ball, d = 0.528, p &lt; 1e-10).",
        body_style
    ))
    cal_img_path = OUTPUTS_DIR / "expected_value_calibration_deciles_phases.png"
    if cal_img_path.exists():
        story.append(Image(str(cal_img_path), width=540, height=92))

    # =========================================================================
    # PAGE 2: Fair Comparisons, Wicket Values, REML Table 3.1 & Sooryavanshi
    # =========================================================================
    story.append(PageBreak())
    # Figure 1: Calibration Deciles & Match Phases (3 panels in 1 row)
    story.append(Paragraph("Figure 1: Out-of-fold Expected Value Calibration Deciles & Match Phases", h2_style))
    img_xr = Image(str(OUTPUTS_DIR / "cal_xr_deciles.png"), width=165, height=84)
    img_xw = Image(str(OUTPUTS_DIR / "cal_xw_deciles.png"), width=165, height=84)
    img_ph = Image(str(OUTPUTS_DIR / "cal_runs_phase.png"), width=165, height=84)
    
    t_cal = Table([
        [img_xr, img_xw, img_ph],
        [
            Paragraph("Panel A: Expected Runs (xR) Deciles", caption_style),
            Paragraph("Panel B: Expected Wickets (xW) Deciles", caption_style),
            Paragraph("Panel C: Runs by Match Phase", caption_style)
        ]
    ], colWidths=[168, 168, 168])
    t_cal.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0.5),
    ]))
    story.append(t_cal)

    # Section 2: Fair Comparisons & Opposition Adjustment
    story.append(Paragraph("2. Fair Comparisons, Eligibility, Opposition Quality Audit & Dip Rules", h1_style))
    story.append(Paragraph(
        "<b>Eligibility Rules & Cohort Counts:</b> Players must meet three filters: (1) >= 100 High-Pressure balls faced / legal balls bowled; "
        "(2) >= 6 High-Pressure matches/innings; (3) >= 10 career matches in 2022-26 data. "
        "<b>Pakistan Player Exclusion:</b> Players representing Pakistan or Pakistan A are excluded from both rankings as an eligibility choice made by the author; this is not required by the dataset or the problem statement. "
        "This leaves exactly <b>131 eligible batters</b> and <b>140 eligible bowlers</b> (8 batters and 8 bowlers excluded). "
        "<b>Eligibility Rules & Cohort Counts:</b> Players must meet three filters: (1) >= 100 High-Pressure balls faced / legal balls bowled; (2) >= 6 High-Pressure matches/innings; (3) >= 10 career matches in 2022-26 data. "
        "<b>Pakistan Player Exclusion:</b> Players representing Pakistan or Pakistan A are excluded from both rankings as an eligibility choice made by the author; this is not required by the dataset or the problem statement. This leaves exactly 131 eligible batters and 140 eligible bowlers (8 batters and 8 bowlers excluded). "
        "<b>Opposition Quality Diagnostics:</b> Batters HP opp strength has mean = +0.46 runs/100b (SD = 1.89); Bowlers HP opp strength has mean = +6.07 runs/100b (SD = 3.79) as high-pressure deliveries face established top/middle-order batters (+6.07 runs/100b above league avg). Baseline impact (Raw_B) is unadjusted; bowler ordinary-opposition mean is +5.82 runs/100b (and batter ordinary opp is -0.16 runs/100b), so bowler pressure effects are shifted up by a similar amount for everyone, and rankings are largely unaffected (demonstrated by the 8/10 bowler overlap without opp adjustment and 9/10 overlap under symmetric recentering). Evaluating without opposition adjustment leaves batter rankings 100% identical (10/10 overlap); in bowlers, 8 of 10 players are retained (Pathirana #1 11.43 vs Hazlewood #2 11.40; Varun drops #8 to #13 and Santner drops #10 to #12, with Hasaranga entering at #9 and Kuldeep at #10). Under symmetric recentered adjustment, 9 of 10 bowlers are retained (Hazlewood #1 12.10, Pathirana #2 11.40; Ellis drops to #12 and Archer enters at #10). "
        "<b>Ordering Rule on Pressure Dips:</b> Primary ranking is <b>Rating = Baseline + Pressure Effect with NO dip exclusion</b> (Abhishek #6, Bumrah #4). "
        "Under <b>Rule B (Clutch-Constrained: Delta_shrunk >= 0)</b>, Bumrah and Abhishek are excluded due to negative pressure deltas (-5.11 and -2.25), allowing Stoinis (Bat #10) and Kuldeep (Bowl #10) into the Top 10.",
        "<b>Ordering Rule on Pressure Dips:</b> Primary ranking is Rating = Baseline + Pressure Effect with NO dip exclusion (Abhishek #6, Bumrah #4). Under Rule B (Clutch-Constrained: Delta_shrunk >= 0), Bumrah and Abhishek are excluded due to negative pressure deltas (-5.11 and -2.25), allowing Stoinis (Bat #10) and Kuldeep (Bowl #10) into the Top 10.",
        body_style
    ))

    # Reconciled Opposition Quality Audit Table (All 20 Players: Raw_B, Raw_D, Opp, Adj_HP, Team)
    # Table 2.1: Opposition Quality Audit
    story.append(Paragraph("Table 2.1: Opposition Quality Audit & Mathematical Reconciliation (Raw_B + Raw_D = Adj_HP identically)", h2_style))
    opp_audit_data = [
    audit_data = [
        [
            Paragraph("Rk", table_cell_header), Paragraph("Batter (Top 10)", table_cell_header), Paragraph("Raw_B", table_cell_header), Paragraph("Raw_D", table_cell_header), Paragraph("Opp", table_cell_header), Paragraph("Adj HP", table_cell_header), Paragraph("Team", table_cell_header),
            Paragraph("Rk", table_cell_header), Paragraph("Bowler (Top 10)", table_cell_header), Paragraph("Raw_B", table_cell_header), Paragraph("Raw_D", table_cell_header), Paragraph("Opp", table_cell_header), Paragraph("Adj HP", table_cell_header), Paragraph("Team", table_cell_header)
        ],
        [
            Paragraph("1", table_cell_bold), Paragraph("Suryakumar Yadav", table_cell_style), Paragraph("+29.69", table_cell_style), Paragraph("+15.01", table_cell_style), Paragraph("-0.43", table_cell_style), Paragraph("+44.70", table_cell_style), Paragraph("MI, India", table_cell_style),
            Paragraph("1", table_cell_bold), Paragraph("Josh Hazlewood", table_cell_style), Paragraph("+17.17", table_cell_style), Paragraph("+28.42", table_cell_style), Paragraph("+7.37", table_cell_style), Paragraph("+45.59", table_cell_style), Paragraph("Aus, RCB", table_cell_style)
        ],
        [
            Paragraph("2", table_cell_bold), Paragraph("Vaibhav Sooryavanshi", table_cell_style), Paragraph("+73.40", table_cell_style), Paragraph("-6.83", table_cell_style), Paragraph("+0.82", table_cell_style), Paragraph("+66.57", table_cell_style), Paragraph("RR, India", table_cell_style),
            Paragraph("2", table_cell_bold), Paragraph("Matheesha Pathirana", table_cell_style), Paragraph("+21.03", table_cell_style), Paragraph("+31.75", table_cell_style), Paragraph("+5.99", table_cell_style), Paragraph("+52.78", table_cell_style), Paragraph("CSK, SL", table_cell_style)
        ],
        [
            Paragraph("3", table_cell_bold), Paragraph("Jos Buttler", table_cell_style), Paragraph("+19.93", table_cell_style), Paragraph("+15.78", table_cell_style), Paragraph("+0.07", table_cell_style), Paragraph("+35.71", table_cell_style), Paragraph("RR, Eng", table_cell_style),
            Paragraph("3", table_cell_bold), Paragraph("Sunil Narine", table_cell_style), Paragraph("+17.15", table_cell_style), Paragraph("+14.62", table_cell_style), Paragraph("+9.37", table_cell_style), Paragraph("+31.78", table_cell_style), Paragraph("KKR", table_cell_style)
        ],
        [
            Paragraph("4", table_cell_bold), Paragraph("Heinrich Klaasen", table_cell_style), Paragraph("+31.12", table_cell_style), Paragraph("+13.25", table_cell_style), Paragraph("+0.60", table_cell_style), Paragraph("+44.37", table_cell_style), Paragraph("SRH, SA", table_cell_style),
            Paragraph("4", table_cell_bold), Paragraph("Jasprit Bumrah", table_cell_style), Paragraph("+35.18", table_cell_style), Paragraph("-19.93", table_cell_style), Paragraph("+9.20", table_cell_style), Paragraph("+15.25", table_cell_style), Paragraph("MI, India", table_cell_style)
        ],
        [
            Paragraph("5", table_cell_bold), Paragraph("Reeza Hendricks", table_cell_style), Paragraph("+11.98", table_cell_style), Paragraph("+51.38", table_cell_style), Paragraph("-0.44", table_cell_style), Paragraph("+63.36", table_cell_style), Paragraph("SA", table_cell_style),
            Paragraph("5", table_cell_bold), Paragraph("Jacob Duffy", table_cell_style), Paragraph("+20.90", table_cell_style), Paragraph("+21.28", table_cell_style), Paragraph("+9.01", table_cell_style), Paragraph("+42.17", table_cell_style), Paragraph("NZ, RCB", table_cell_style)
        ],
        [
            Paragraph("6", table_cell_bold), Paragraph("Abhishek Sharma", table_cell_style), Paragraph("+40.33", table_cell_style), Paragraph("-11.35", table_cell_style), Paragraph("-0.60", table_cell_style), Paragraph("+28.98", table_cell_style), Paragraph("SRH, Ind", table_cell_style),
            Paragraph("6", table_cell_bold), Paragraph("Rashid Khan", table_cell_style), Paragraph("+7.69", table_cell_style), Paragraph("+16.97", table_cell_style), Paragraph("+3.45", table_cell_style), Paragraph("+24.66", table_cell_style), Paragraph("GT, Afg", table_cell_style)
        ],
        [
            Paragraph("7", table_cell_bold), Paragraph("Phil Salt", table_cell_style), Paragraph("+28.13", table_cell_style), Paragraph("+10.10", table_cell_style), Paragraph("-0.11", table_cell_style), Paragraph("+38.23", table_cell_style), Paragraph("Eng, KKR", table_cell_style),
            Paragraph("7", table_cell_bold), Paragraph("Lockie Ferguson", table_cell_style), Paragraph("+7.15", table_cell_style), Paragraph("+37.05", table_cell_style), Paragraph("+6.44", table_cell_style), Paragraph("+44.20", table_cell_style), Paragraph("GT, NZ", table_cell_style)
        ],
        [
            Paragraph("8", table_cell_bold), Paragraph("Rinku Singh", table_cell_style), Paragraph("+12.21", table_cell_style), Paragraph("+34.39", table_cell_style), Paragraph("-0.09", table_cell_style), Paragraph("+46.60", table_cell_style), Paragraph("KKR, Ind", table_cell_style),
            Paragraph("8", table_cell_bold), Paragraph("Varun Chakravarthy", table_cell_style), Paragraph("+20.23", table_cell_style), Paragraph("-1.24", table_cell_style), Paragraph("+9.07", table_cell_style), Paragraph("+19.00", table_cell_style), Paragraph("KKR, Ind", table_cell_style)
        ],
        [
            Paragraph("9", table_cell_bold), Paragraph("Shreyas Iyer", table_cell_style), Paragraph("+12.80", table_cell_style), Paragraph("+22.00", table_cell_style), Paragraph("-0.44", table_cell_style), Paragraph("+34.81", table_cell_style), Paragraph("Ind, KKR", table_cell_style),
            Paragraph("9", table_cell_bold), Paragraph("Nathan Ellis", table_cell_style), Paragraph("+26.19", table_cell_style), Paragraph("+4.84", table_cell_style), Paragraph("+7.52", table_cell_style), Paragraph("+31.03", table_cell_style), Paragraph("PBKS, Aus", table_cell_style)
        ],
        [
            Paragraph("10", table_cell_bold), Paragraph("Tim David", table_cell_style), Paragraph("+43.04", table_cell_style), Paragraph("-4.90", table_cell_style), Paragraph("+0.29", table_cell_style), Paragraph("+38.14", table_cell_style), Paragraph("MI, Aus", table_cell_style),
            Paragraph("10", table_cell_bold), Paragraph("Mitchell Santner", table_cell_style), Paragraph("+5.84", table_cell_style), Paragraph("+23.43", table_cell_style), Paragraph("+7.93", table_cell_style), Paragraph("+29.28", table_cell_style), Paragraph("CSK, NZ", table_cell_style)
        ],
        [Paragraph("1", table_cell_bold), Paragraph("Suryakumar Yadav", table_cell_style), Paragraph("+29.69", table_cell_style), Paragraph("+15.01", table_cell_style), Paragraph("-0.43", table_cell_style), Paragraph("+44.70", table_cell_style), Paragraph("MI, India", table_cell_style), Paragraph("1", table_cell_bold), Paragraph("Josh Hazlewood", table_cell_style), Paragraph("+17.17", table_cell_style), Paragraph("+28.42", table_cell_style), Paragraph("+7.37", table_cell_style), Paragraph("+45.59", table_cell_style), Paragraph("Aus, RCB", table_cell_style)],
        [Paragraph("2", table_cell_bold), Paragraph("Vaibhav Sooryavanshi", table_cell_style), Paragraph("+73.40", table_cell_style), Paragraph("-6.83", table_cell_style), Paragraph("+0.82", table_cell_style), Paragraph("+66.57", table_cell_style), Paragraph("RR, India", table_cell_style), Paragraph("2", table_cell_bold), Paragraph("Matheesha Pathirana", table_cell_style), Paragraph("+21.03", table_cell_style), Paragraph("+31.75", table_cell_style), Paragraph("+5.99", table_cell_style), Paragraph("+52.78", table_cell_style), Paragraph("CSK, SL", table_cell_style)],
        [Paragraph("3", table_cell_bold), Paragraph("Jos Buttler", table_cell_style), Paragraph("+19.93", table_cell_style), Paragraph("+15.78", table_cell_style), Paragraph("+0.07", table_cell_style), Paragraph("+35.71", table_cell_style), Paragraph("RR, Eng", table_cell_style), Paragraph("3", table_cell_bold), Paragraph("Sunil Narine", table_cell_style), Paragraph("+17.15", table_cell_style), Paragraph("+14.62", table_cell_style), Paragraph("+9.37", table_cell_style), Paragraph("+31.78", table_cell_style), Paragraph("KKR", table_cell_style)],
        [Paragraph("4", table_cell_bold), Paragraph("Heinrich Klaasen", table_cell_style), Paragraph("+31.12", table_cell_style), Paragraph("+13.25", table_cell_style), Paragraph("+0.60", table_cell_style), Paragraph("+44.37", table_cell_style), Paragraph("SRH, SA", table_cell_style), Paragraph("4", table_cell_bold), Paragraph("Jasprit Bumrah", table_cell_style), Paragraph("+35.18", table_cell_style), Paragraph("-19.93", table_cell_style), Paragraph("+9.20", table_cell_style), Paragraph("+15.25", table_cell_style), Paragraph("MI, India", table_cell_style)],
        [Paragraph("5", table_cell_bold), Paragraph("Reeza Hendricks", table_cell_style), Paragraph("+11.98", table_cell_style), Paragraph("+51.38", table_cell_style), Paragraph("-0.44", table_cell_style), Paragraph("+63.36", table_cell_style), Paragraph("SA", table_cell_style), Paragraph("5", table_cell_bold), Paragraph("Jacob Duffy", table_cell_style), Paragraph("+20.90", table_cell_style), Paragraph("+21.28", table_cell_style), Paragraph("+9.01", table_cell_style), Paragraph("+42.17", table_cell_style), Paragraph("NZ, RCB", table_cell_style)],
        [Paragraph("6", table_cell_bold), Paragraph("Abhishek Sharma", table_cell_style), Paragraph("+40.33", table_cell_style), Paragraph("-11.35", table_cell_style), Paragraph("-0.60", table_cell_style), Paragraph("+28.98", table_cell_style), Paragraph("SRH, Ind", table_cell_style), Paragraph("6", table_cell_bold), Paragraph("Rashid Khan", table_cell_style), Paragraph("+7.69", table_cell_style), Paragraph("+16.97", table_cell_style), Paragraph("+3.45", table_cell_style), Paragraph("+24.66", table_cell_style), Paragraph("GT, Afg", table_cell_style)],
        [Paragraph("7", table_cell_bold), Paragraph("Phil Salt", table_cell_style), Paragraph("+28.13", table_cell_style), Paragraph("+10.10", table_cell_style), Paragraph("-0.11", table_cell_style), Paragraph("+38.23", table_cell_style), Paragraph("Eng, KKR", table_cell_style), Paragraph("7", table_cell_bold), Paragraph("Lockie Ferguson", table_cell_style), Paragraph("+7.15", table_cell_style), Paragraph("+37.05", table_cell_style), Paragraph("+6.44", table_cell_style), Paragraph("+44.20", table_cell_style), Paragraph("GT, NZ", table_cell_style)],
        [Paragraph("8", table_cell_bold), Paragraph("Rinku Singh", table_cell_style), Paragraph("+12.21", table_cell_style), Paragraph("+34.39", table_cell_style), Paragraph("-0.09", table_cell_style), Paragraph("+46.60", table_cell_style), Paragraph("KKR, Ind", table_cell_style), Paragraph("8", table_cell_bold), Paragraph("Varun Chakravarthy", table_cell_style), Paragraph("+20.23", table_cell_style), Paragraph("-1.24", table_cell_style), Paragraph("+9.07", table_cell_style), Paragraph("+19.00", table_cell_style), Paragraph("KKR, Ind", table_cell_style)],
        [Paragraph("9", table_cell_bold), Paragraph("Shreyas Iyer", table_cell_style), Paragraph("+12.80", table_cell_style), Paragraph("+22.00", table_cell_style), Paragraph("-0.44", table_cell_style), Paragraph("+34.81", table_cell_style), Paragraph("Ind, KKR", table_cell_style), Paragraph("9", table_cell_bold), Paragraph("Nathan Ellis", table_cell_style), Paragraph("+26.19", table_cell_style), Paragraph("+4.84", table_cell_style), Paragraph("+7.52", table_cell_style), Paragraph("+31.03", table_cell_style), Paragraph("PBKS, Aus", table_cell_style)],
        [Paragraph("10", table_cell_bold), Paragraph("Tim David", table_cell_style), Paragraph("+43.04", table_cell_style), Paragraph("-4.90", table_cell_style), Paragraph("+0.29", table_cell_style), Paragraph("+38.14", table_cell_style), Paragraph("MI, Aus", table_cell_style), Paragraph("10", table_cell_bold), Paragraph("Mitchell Santner", table_cell_style), Paragraph("+5.84", table_cell_style), Paragraph("+23.43", table_cell_style), Paragraph("+7.93", table_cell_style), Paragraph("+29.28", table_cell_style), Paragraph("CSK, NZ", table_cell_style)],
    ]
    t_opp = Table(opp_audit_data, colWidths=[12, 68, 22, 22, 18, 24, 44, 12, 68, 22, 22, 18, 24, 44])
    t_opp.setStyle(TableStyle([
    t_audit = Table(audit_data, colWidths=[12, 78, 25, 25, 21, 27, 45, 12, 78, 25, 25, 21, 27, 45])
    t_audit.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (6, 0), colors.HexColor('#E21A5C')),
        ('BACKGROUND', (7, 0), (-1, 0), colors.HexColor('#004B87')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0.5),
        ('TOPPADDING', (0, 0), (-1, -1), 0.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 1.0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 1.0),
        ('GRID', (0, 0), (-1, -1), 0.35, colors.HexColor('#DDDDDD')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')])
    ]))
    story.append(t_opp)
    story.append(Paragraph(
        "<i>Note on Raw Delta:</i> For all players, Raw_B + Raw_D = Adj_HP identically. Vaibhav Sooryavanshi's opposition-adjusted pressure delta is -6.83 runs/100b (alongside unadjusted raw delta: 65.75 - 73.40 = -7.65 runs/100b).",
        body_style
    ))
    story.append(Spacer(1, 0.8))
    story.append(t_audit)
    story.append(Paragraph("Note on Raw Delta: For all players, Raw_B + Raw_D = Adj_HP identically. Vaibhav Sooryavanshi's opposition-adjusted pressure delta is -6.83 runs/100b (alongside unadjusted raw delta: 65.75 - 73.40 = -7.65 runs/100b).", caption_style))

    # Excluded Pakistan Players Table
    # Table 2.2: Transparent Audit of Excluded Pakistan Players
    story.append(Paragraph("Table 2.2: Transparent Audit of Excluded Pakistan Players in Unconstrained Top 20", h2_style))
    excl_data = [
        [Paragraph("Discipline", table_cell_header), Paragraph("Player Name", table_cell_header), Paragraph("Unc. Rk", table_cell_header), Paragraph("HP Balls", table_cell_header), Paragraph("Shrunk Rating", table_cell_header), Paragraph("Shrunk Base", table_cell_header), Paragraph("Shrunk Delta", table_cell_header), Paragraph("Primary Team", table_cell_header), Paragraph("Reason: author's eligibility choice", table_cell_header)],
        [Paragraph("Batter", table_cell_style), Paragraph("Mohammad Rizwan", table_cell_bold), Paragraph("15", table_cell_style), Paragraph("400", table_cell_style), Paragraph("+17.86", table_cell_style), Paragraph("+10.57", table_cell_style), Paragraph("+7.29", table_cell_style), Paragraph("Pakistan", table_cell_style), Paragraph("Author's eligibility choice (Pakistan player; not required by dataset)", table_cell_style)],
        [Paragraph("Bowler", table_cell_style), Paragraph("Sufiyan Muqeem", table_cell_bold), Paragraph("4", table_cell_style), Paragraph("155", table_cell_style), Paragraph("+14.13", table_cell_style), Paragraph("+9.07", table_cell_style), Paragraph("+5.06", table_cell_style), Paragraph("Pakistan, Pakistan A", table_cell_style), Paragraph("Author's eligibility choice (Pakistan A player; not required by dataset)", table_cell_style)],
        [Paragraph("Bowler", table_cell_style), Paragraph("Mohammad Nawaz", table_cell_bold), Paragraph("16", table_cell_style), Paragraph("289", table_cell_style), Paragraph("+11.27", table_cell_style), Paragraph("+6.13", table_cell_style), Paragraph("+5.14", table_cell_style), Paragraph("Pakistan", table_cell_style), Paragraph("Author's eligibility choice (Pakistan player; not required by dataset)", table_cell_style)],
        [Paragraph("Bowler", table_cell_style), Paragraph("Abrar Ahmed", table_cell_bold), Paragraph("20", table_cell_style), Paragraph("189", table_cell_style), Paragraph("+10.77", table_cell_style), Paragraph("+7.47", table_cell_style), Paragraph("+3.30", table_cell_style), Paragraph("Pakistan", table_cell_style), Paragraph("Author's eligibility choice (Pakistan player; not required by dataset)", table_cell_style)],
        [
            Paragraph("Discipline", table_cell_header), Paragraph("Player Name", table_cell_header), Paragraph("Unc. Rk", table_cell_header), Paragraph("HP Balls", table_cell_header), Paragraph("Shrunk Rating", table_cell_header), Paragraph("Shrunk Base", table_cell_header), Paragraph("Shrunk Delta", table_cell_header), Paragraph("Primary Team", table_cell_header), Paragraph("Reason: author's eligibility choice", table_cell_header)
        ],
        [Paragraph("Batter", table_cell_style), Paragraph("Mohammad Rizwan", table_cell_bold), Paragraph("15", table_cell_style), Paragraph("400", table_cell_style), Paragraph("+17.86", table_cell_bold), Paragraph("+10.57", table_cell_style), Paragraph("+7.29", table_cell_style), Paragraph("Pakistan", table_cell_style), Paragraph("Author's eligibility choice (Pakistan player; not required by dataset)", table_cell_style)],
        [Paragraph("Bowler", table_cell_style), Paragraph("Sufiyan Muqeem", table_cell_bold), Paragraph("4", table_cell_style), Paragraph("155", table_cell_style), Paragraph("+14.13", table_cell_bold), Paragraph("+9.07", table_cell_style), Paragraph("+5.06", table_cell_style), Paragraph("Pakistan, Pakistan A", table_cell_style), Paragraph("Author's eligibility choice (Pakistan A player; not required by dataset)", table_cell_style)],
        [Paragraph("Bowler", table_cell_style), Paragraph("Mohammad Nawaz", table_cell_bold), Paragraph("16", table_cell_style), Paragraph("289", table_cell_style), Paragraph("+11.27", table_cell_bold), Paragraph("+6.13", table_cell_style), Paragraph("+5.14", table_cell_style), Paragraph("Pakistan", table_cell_style), Paragraph("Author's eligibility choice (Pakistan player; not required by dataset)", table_cell_style)],
        [Paragraph("Bowler", table_cell_style), Paragraph("Abrar Ahmed", table_cell_bold), Paragraph("20", table_cell_style), Paragraph("189", table_cell_style), Paragraph("+10.77", table_cell_bold), Paragraph("+7.47", table_cell_style), Paragraph("+3.30", table_cell_style), Paragraph("Pakistan", table_cell_style), Paragraph("Author's eligibility choice (Pakistan player; not required by dataset)", table_cell_style)],
    ]
    t_excl = Table(excl_data, colWidths=[36, 75, 24, 26, 36, 34, 34, 60, 195])
    t_excl = Table(excl_data, colWidths=[38, 75, 32, 30, 35, 35, 35, 55, 170])
    t_excl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#555555')),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#004B87')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0.5),
        ('TOPPADDING', (0, 0), (-1, -1), 0.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 1.0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 1.0),
        ('GRID', (0, 0), (-1, -1), 0.35, colors.HexColor('#DDDDDD')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')])
    ]))
    story.append(t_excl)
    story.append(Spacer(1, 0.8))
    story.append(Paragraph("Table 2.2: Transparent audit of excluded Pakistan players who would have ranked in unconstrained Top 20.", caption_style))

    # Vaibhav Sooryavanshi Plain Statement
    story.append(Paragraph("Diagnostic Finding on Vaibhav Sooryavanshi's Baseline Dependence", h2_style))
    story.append(Paragraph(
        "<b>Plain Finding on Vaibhav Sooryavanshi:</b> Sooryavanshi's Rank 2 position depends heavily on extraordinary baseline scoring rather than clutch elevation. "
        "His Raw Baseline Impact is +73.40 runs/100b, while his Raw High-Pressure Impact is +65.75 runs/100b (+0.82 opp diff), yielding an <b>opposition-adjusted HP impact of +66.57 runs/100b</b> and a <b>negative raw pressure delta of -6.83 runs/100b</b>. "
        "REML shrinks his modest sample (168 HP balls) toward the positive population mean (+3.57), producing a shrunk delta of +1.71. "
        "Under <b>Rule B (Clutch-Constrained: Delta_shrunk >= 0)</b>, he qualifies and maintains Rank 2; however, on raw delta alone he would be excluded. "
        "Under a stricter volume filter of <b>minimum 200 HP balls</b>, his 168 balls render him unranked.",
        body_style
    ))
    story.append(Spacer(1, 0.8))

    # Section 3: Wicket Run-Values & Table 3.1
    # =========================================================================
    # PAGE 3: Wicket Values, Shrinkage Reconciliation (Table 3.1) & REML Priors
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("3. Wicket Run-Values & Mathematical Shrinkage Reconciliation", h1_style))
    story.append(Paragraph(
        "<b>Wicket Values:</b> Powerplay = 14.36 runs, Middle = 8.13 runs, Death = 2.92 runs (weighted mean 8.85 runs; HP-specific: PP 14.40, Mid 10.71, Death 5.89). "
        "<b>Reconciliation & Ball Counts:</b> Population priors are Batters mu_B = +7.02, mu_Delta = +3.57 (K_B = 1717.4, K_Delta = 773.0, w = 24.8%); Bowlers mu_B = +2.53, mu_Delta = +1.14 (K_B = 1312.9, K_Delta = 1041.4, w = 19.1%). Rating = B_shrunk + Delta_shrunk. "
        "HP ball counts in Table 3.1 reflect all non-wide legal deliveries in the master database (Abhishek 494b, Salt 397b, Iyer 448b), ensuring full accounting of all delivery-level events.",
        body_style
    ))

    # Table 3.1 Breakdown Table (ALL 20 PLAYERS: 10 Batters + 10 Bowlers with 90% CI, Exact Matches)
    # Table 3.1: Complete Calculation Verification
    story.append(Paragraph("Table 3.1: Complete Calculation Verification for All 20 Primary Selections (10 Batters & 10 Bowlers)", h2_style))
    verif_all_data = [
        [
            Paragraph("Rk", table_cell_header), Paragraph("Player Name", table_cell_header), Paragraph("Role", table_cell_header), Paragraph("N_B", table_cell_header), Paragraph("w_B", table_cell_header), Paragraph("Raw_B", table_cell_header), Paragraph("B_shk", table_cell_header), Paragraph("N_D", table_cell_header), Paragraph("w_D", table_cell_header), Paragraph("Raw_D", table_cell_header), Paragraph("D_shk", table_cell_header), Paragraph("Rating", table_cell_header), Paragraph("90% CI", table_cell_header), Paragraph("P(T10)", table_cell_header)
        ],
        [Paragraph("1", table_cell_bold), Paragraph("Suryakumar Yadav", table_cell_style), Paragraph("Bat", table_cell_style), Paragraph("2062", table_cell_style), Paragraph("0.546", table_cell_style), Paragraph("+29.69", table_cell_style), Paragraph("+19.39", table_cell_style), Paragraph("697", table_cell_style), Paragraph("0.474", table_cell_style), Paragraph("+15.01", table_cell_style), Paragraph("+8.99", table_cell_style), Paragraph("+28.39", table_cell_bold), Paragraph("[18.2, 36.2]", table_cell_style), Paragraph("90.3%", table_cell_style)],
        [Paragraph("2", table_cell_bold), Paragraph("Vaibhav Sooryavanshi", table_cell_style), Paragraph("Bat", table_cell_style), Paragraph("508", table_cell_style), Paragraph("0.228", table_cell_style), Paragraph("+73.40", table_cell_style), Paragraph("+22.18", table_cell_style), Paragraph("168", table_cell_style), Paragraph("0.179", table_cell_style), Paragraph("-6.83", table_cell_style), Paragraph("+1.71", table_cell_style), Paragraph("+23.89", table_cell_bold), Paragraph("[12.1, 33.3]", table_cell_style), Paragraph("63.2%", table_cell_style)],
        [Paragraph("3", table_cell_bold), Paragraph("Jos Buttler", table_cell_style), Paragraph("Bat", table_cell_style), Paragraph("2272", table_cell_style), Paragraph("0.570", table_cell_style), Paragraph("+19.93", table_cell_style), Paragraph("+14.37", table_cell_style), Paragraph("557", table_cell_style), Paragraph("0.419", table_cell_style), Paragraph("+15.78", table_cell_style), Paragraph("+8.68", table_cell_style), Paragraph("+23.06", table_cell_bold), Paragraph("[12.1, 31.3]", table_cell_style), Paragraph("62.5%", table_cell_style)],
        [Paragraph("4", table_cell_bold), Paragraph("Heinrich Klaasen", table_cell_style), Paragraph("Bat", table_cell_style), Paragraph("1156", table_cell_style), Paragraph("0.402", table_cell_style), Paragraph("+31.12", table_cell_style), Paragraph("+16.72", table_cell_style), Paragraph("261", table_cell_style), Paragraph("0.252", table_cell_style), Paragraph("+13.25", table_cell_style), Paragraph("+6.01", table_cell_style), Paragraph("+22.73", table_cell_bold), Paragraph("[13.1, 29.4]", table_cell_style), Paragraph("58.3%", table_cell_style)],
        [Paragraph("5", table_cell_bold), Paragraph("Reeza Hendricks", table_cell_style), Paragraph("Bat", table_cell_style), Paragraph("611", table_cell_style), Paragraph("0.262", table_cell_style), Paragraph("+11.98", table_cell_style), Paragraph("+8.33", table_cell_style), Paragraph("224", table_cell_style), Paragraph("0.225", table_cell_style), Paragraph("+51.38", table_cell_style), Paragraph("+14.31", table_cell_style), Paragraph("+22.64", table_cell_bold), Paragraph("[13.2, 28.1]", table_cell_style), Paragraph("57.1%", table_cell_style)],
        [Paragraph("6", table_cell_bold), Paragraph("Abhishek Sharma", table_cell_style), Paragraph("Bat", table_cell_style), Paragraph("1823", table_cell_style), Paragraph("0.515", table_cell_style), Paragraph("+40.33", table_cell_style), Paragraph("+24.17", table_cell_style), Paragraph("494", table_cell_style), Paragraph("0.390", table_cell_style), Paragraph("-11.35", table_cell_style), Paragraph("-2.25", table_cell_style), Paragraph("+21.93", table_cell_bold), Paragraph("[6.3, 35.0]", table_cell_style), Paragraph("53.6%", table_cell_style)],
        [Paragraph("7", table_cell_bold), Paragraph("Phil Salt", table_cell_style), Paragraph("Bat", table_cell_style), Paragraph("1246", table_cell_style), Paragraph("0.420", table_cell_style), Paragraph("+28.13", table_cell_style), Paragraph("+15.90", table_cell_style), Paragraph("397", table_cell_style), Paragraph("0.339", table_cell_style), Paragraph("+10.10", table_cell_style), Paragraph("+5.79", table_cell_style), Paragraph("+21.69", table_cell_bold), Paragraph("[9.0, 30.9]", table_cell_style), Paragraph("49.5%", table_cell_style)],
        [Paragraph("8", table_cell_bold), Paragraph("Rinku Singh", table_cell_style), Paragraph("Bat", table_cell_style), Paragraph("990", table_cell_style), Paragraph("0.366", table_cell_style), Paragraph("+12.21", table_cell_style), Paragraph("+8.92", table_cell_style), Paragraph("294", table_cell_style), Paragraph("0.276", table_cell_style), Paragraph("+34.39", table_cell_style), Paragraph("+12.06", table_cell_style), Paragraph("+20.98", table_cell_bold), Paragraph("[12.2, 26.7]", table_cell_style), Paragraph("44.9%", table_cell_style)],
        [Paragraph("9", table_cell_bold), Paragraph("Shreyas Iyer", table_cell_style), Paragraph("Bat", table_cell_style), Paragraph("1417", table_cell_style), Paragraph("0.452", table_cell_style), Paragraph("+12.80", table_cell_style), Paragraph("+9.64", table_cell_style), Paragraph("448", table_cell_style), Paragraph("0.367", table_cell_style), Paragraph("+22.00", table_cell_style), Paragraph("+10.33", table_cell_style), Paragraph("+19.97", table_cell_bold), Paragraph("[9.9, 26.8]", table_cell_style), Paragraph("36.5%", table_cell_style)],
        [Paragraph("10", table_cell_bold), Paragraph("Tim David", table_cell_style), Paragraph("Bat", table_cell_style), Paragraph("850", table_cell_style), Paragraph("0.331", table_cell_style), Paragraph("+43.04", table_cell_style), Paragraph("+18.95", table_cell_style), Paragraph("376", table_cell_style), Paragraph("0.327", table_cell_style), Paragraph("-4.90", table_cell_style), Paragraph("+0.80", table_cell_style), Paragraph("+19.75", table_cell_bold), Paragraph("[9.5, 27.7]", table_cell_style), Paragraph("35.1%", table_cell_style)],
        [Paragraph("1", table_cell_bold), Paragraph("Josh Hazlewood", table_cell_style), Paragraph("Bowl", table_cell_style), Paragraph("1078", table_cell_style), Paragraph("0.451", table_cell_style), Paragraph("+17.17", table_cell_style), Paragraph("+9.13", table_cell_style), Paragraph("399", table_cell_style), Paragraph("0.277", table_cell_style), Paragraph("+28.42", table_cell_style), Paragraph("+8.70", table_cell_style), Paragraph("+17.83", table_cell_bold), Paragraph("[7.4, 27.9]", table_cell_style), Paragraph("73.5%", table_cell_style)],
        [Paragraph("2", table_cell_bold), Paragraph("Matheesha Pathirana", table_cell_style), Paragraph("Bowl", table_cell_style), Paragraph("853", table_cell_style), Paragraph("0.394", table_cell_style), Paragraph("+21.03", table_cell_style), Paragraph("+9.82", table_cell_style), Paragraph("282", table_cell_style), Paragraph("0.213", table_cell_style), Paragraph("+31.75", table_cell_style), Paragraph("+7.66", table_cell_style), Paragraph("+17.48", table_cell_bold), Paragraph("[10.1, 24.1]", table_cell_style), Paragraph("82.7%", table_cell_style)],
        [Paragraph("3", table_cell_bold), Paragraph("Sunil Narine", table_cell_style), Paragraph("Bowl", table_cell_style), Paragraph("1062", table_cell_style), Paragraph("0.447", table_cell_style), Paragraph("+17.15", table_cell_style), Paragraph("+9.07", table_cell_style), Paragraph("468", table_cell_style), Paragraph("0.310", table_cell_style), Paragraph("+14.62", table_cell_style), Paragraph("+5.32", table_cell_style), Paragraph("+14.39", table_cell_bold), Paragraph("[7.2, 21.5]", table_cell_style), Paragraph("56.8%", table_cell_style)],
        [Paragraph("4", table_cell_bold), Paragraph("Jasprit Bumrah", table_cell_style), Paragraph("Bowl", table_cell_style), Paragraph("1270", table_cell_style), Paragraph("0.492", table_cell_style), Paragraph("+35.18", table_cell_style), Paragraph("+18.59", table_cell_style), Paragraph("439", table_cell_style), Paragraph("0.297", table_cell_style), Paragraph("-19.93", table_cell_style), Paragraph("-5.11", table_cell_style), Paragraph("+13.48", table_cell_bold), Paragraph("[5.0, 22.5]", table_cell_style), Paragraph("51.3%", table_cell_style)],
        [Paragraph("5", table_cell_bold), Paragraph("Jacob Duffy", table_cell_style), Paragraph("Bowl", table_cell_style), Paragraph("686", table_cell_style), Paragraph("0.343", table_cell_style), Paragraph("+20.90", table_cell_style), Paragraph("+8.83", table_cell_style), Paragraph("191", table_cell_style), Paragraph("0.155", table_cell_style), Paragraph("+21.28", table_cell_style), Paragraph("+4.26", table_cell_style), Paragraph("+13.10", table_cell_bold), Paragraph("[2.4, 23.1]", table_cell_style), Paragraph("47.1%", table_cell_style)],
        [Paragraph("6", table_cell_bold), Paragraph("Rashid Khan", table_cell_style), Paragraph("Bowl", table_cell_style), Paragraph("2089", table_cell_style), Paragraph("0.614", table_cell_style), Paragraph("+7.69", table_cell_style), Paragraph("+5.70", table_cell_style), Paragraph("658", table_cell_style), Paragraph("0.387", table_cell_style), Paragraph("+16.97", table_cell_style), Paragraph("+7.27", table_cell_style), Paragraph("+12.97", table_cell_bold), Paragraph("[5.5, 20.5]", table_cell_style), Paragraph("44.7%", table_cell_style)],
        [Paragraph("7", table_cell_bold), Paragraph("Lockie Ferguson", table_cell_style), Paragraph("Bowl", table_cell_style), Paragraph("814", table_cell_style), Paragraph("0.383", table_cell_style), Paragraph("+7.15", table_cell_style), Paragraph("+4.30", table_cell_style), Paragraph("270", table_cell_style), Paragraph("0.206", table_cell_style), Paragraph("+37.05", table_cell_style), Paragraph("+8.53", table_cell_style), Paragraph("+12.83", table_cell_bold), Paragraph("[2.4, 23.0]", table_cell_style), Paragraph("43.1%", table_cell_style)],
        [Paragraph("8", table_cell_bold), Paragraph("Varun Chakravarthy", table_cell_style), Paragraph("Bowl", table_cell_style), Paragraph("1520", table_cell_style), Paragraph("0.537", table_cell_style), Paragraph("+20.23", table_cell_style), Paragraph("+12.03", table_cell_style), Paragraph("608", table_cell_style), Paragraph("0.369", table_cell_style), Paragraph("-1.24", table_cell_style), Paragraph("+0.26", table_cell_style), Paragraph("+12.29", table_cell_bold), Paragraph("[4.7, 19.6]", table_cell_style), Paragraph("39.1%", table_cell_style)],
        [Paragraph("9", table_cell_bold), Paragraph("Nathan Ellis", table_cell_style), Paragraph("Bowl", table_cell_style), Paragraph("649", table_cell_style), Paragraph("0.331", table_cell_style), Paragraph("+26.19", table_cell_style), Paragraph("+10.36", table_cell_style), Paragraph("268", table_cell_style), Paragraph("0.205", table_cell_style), Paragraph("+4.84", table_cell_style), Paragraph("+1.90", table_cell_style), Paragraph("+12.26", table_cell_bold), Paragraph("[5.1, 18.5]", table_cell_style), Paragraph("33.9%", table_cell_style)],
        [Paragraph("10", table_cell_bold), Paragraph("Mitchell Santner", table_cell_style), Paragraph("Bowl", table_cell_style), Paragraph("1272", table_cell_style), Paragraph("0.492", table_cell_style), Paragraph("+5.84", table_cell_style), Paragraph("+4.16", table_cell_style), Paragraph("465", table_cell_style), Paragraph("0.309", table_cell_style), Paragraph("+23.43", table_cell_style), Paragraph("+8.02", table_cell_style), Paragraph("+12.18", table_cell_bold), Paragraph("[5.2, 19.3]", table_cell_style), Paragraph("39.7%", table_cell_style)],
    ]
    t_verif = Table(verif_all_data, colWidths=[12, 85, 20, 24, 25, 28, 30, 24, 25, 28, 30, 32, 42, 25])
    t_verif = Table(verif_all_data, colWidths=[14, 98, 22, 28, 28, 33, 33, 26, 28, 33, 33, 37, 56, 28], repeatRows=1)
    t_verif.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#004B87')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0.4),
        ('TOPPADDING', (0, 0), (-1, -1), 0.4),
        ('LEFTPADDING', (0, 0), (-1, -1), 1.0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 1.0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0.7),
        ('TOPPADDING', (0, 0), (-1, -1), 0.7),
        ('LEFTPADDING', (0, 0), (-1, -1), 1.5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 1.5),
        ('GRID', (0, 0), (-1, -1), 0.35, colors.HexColor('#DDDDDD')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')])
    ]))
    story.append(t_verif)
    story.append(Paragraph("Table 3.1: Breakdown of baseline and pressure-side impact, shrinkage weights, and posterior intervals for all 20 players.", caption_style))

    # =========================================================================
    # PAGE 3: Null Permutation, Sensitivity, Bowler Wickets & Diagnostics
    # =========================================================================
    story.append(PageBreak())
    page3_elements = []
    # Vaibhav Sooryavanshi Plain Statement
    story.append(Paragraph("Diagnostic Finding on Vaibhav Sooryavanshi's Baseline Dependence", h2_style))
    story.append(Paragraph(
        "<b>Plain Finding on Vaibhav Sooryavanshi:</b> Sooryavanshi's Rank 2 position depends heavily on extraordinary baseline scoring rather than clutch elevation. "
        "His Raw Baseline Impact is +73.40 runs/100b, while his Raw High-Pressure Impact is +65.75 runs/100b (+0.82 opp diff), yielding an opposition-adjusted HP impact of +66.57 runs/100b and a negative raw pressure delta of -6.83 runs/100b. "
        "REML shrinks his modest sample (168 HP balls) toward the positive population mean (+3.57), producing a shrunk delta of +1.71. "
        "Under <b>Rule B (Clutch-Constrained: Delta_shrunk >= 0)</b>, he qualifies and maintains Rank 2; however, on raw delta alone he would be excluded. "
        "Under a stricter volume filter of <b>minimum 200 HP balls</b>, his 168 balls render him unranked.",
        body_style
    ))

    page3_elements.append(Paragraph("4. Within-Match Null Test & Filtered Cohort Parameter Verification", h1_style))
    page3_elements.append(Paragraph(
    # Section 4: Within-Match Null Test & Table 4.1
    story.append(Paragraph("4. Within-Match Null Test & Filtered Cohort Parameter Verification", h1_style))
    story.append(Paragraph(
        "<b>Within-Match Null Test (1,000 Draws):</b> High-pressure indicators permuted within matches (preserving phase, context, and venue). "
        "Bowlers: observed std is 4.052 vs null mean 3.653 (p = 0.0300 filtered cohort; 4.089 vs 3.601, p = 0.0060 full cohort), confirming <i>statistically distinguishable pressure control</i>. "
        "Batters: observed std is 5.068 vs null mean 4.615 (p = 0.0440 filtered; 5.042 vs 4.590, p = 0.0500 full), indicating <i>borderline pressure-specific signal</i> due to high single-match batting variance. "
        "Bowlers: observed std is 4.052 vs null mean 3.653 (p = 0.0300 filtered cohort; 4.089 vs 3.601, p = 0.0060 full cohort), confirming statistically distinguishable pressure control. "
        "Batters: observed std is 5.068 vs null mean 4.615 (p = 0.0440 filtered; 5.042 vs 4.590, p = 0.0500 full), indicating borderline pressure-specific signal due to high single-match batting variance. "
        "<b>Reliability Reconciliation:</b> Applying Spearman-Brown (r_SB = 2r / [1 + r]) to split-half correlations yields r_SB = 0.107 (batters) vs 0.212 (bowlers). "
        "The gap to implied reliability (24.8% bat, 19.1% bowl) reflects that batting clutch impact across independent halves is subject to substantial single-delivery variance, whereas bowling exhibits higher longitudinal repeatability.",
        body_style
    ))
    page3_elements.append(Spacer(1, 0.8))

    # Side-by-side pre vs post exclusion parameter table
    page3_elements.append(Paragraph("Table 4.1: Side-by-Side Model Parameter Verification (Pre-Exclusion vs Filtered Cohort from Actual Runs)", h2_style))
    # Table 4.1 Parameter Verification
    story.append(Paragraph("Table 4.1: Side-by-Side Model Parameter Verification (Pre-Exclusion vs Filtered Cohort from Actual Runs)", h2_style))
    param_comp_data = [
        [Paragraph("Parameter / Metric", table_cell_header), Paragraph("Pre-Exclusion (All Cohort)", table_cell_header), Paragraph("Post-Exclusion (Filtered Cohort)", table_cell_header), Paragraph("Impact / Reconciliation Notes", table_cell_header)],
        [Paragraph("Eligible Batters Count", table_cell_style), Paragraph("139 players (>= 100 HP balls)", table_cell_style), Paragraph("131 players (8 Pakistan excluded)", table_cell_bold), Paragraph("Cohort filtered before estimating population means and bounds", table_cell_style)],
        [Paragraph("Eligible Bowlers Count", table_cell_style), Paragraph("148 players (>= 100 HP balls)", table_cell_style), Paragraph("140 players (8 Pakistan excluded)", table_cell_bold), Paragraph("Cohort filtered before estimating population means and bounds", table_cell_style)],
        [Paragraph("Batters REML Priors", table_cell_style), Paragraph("K_B = 1717.4, K_Delta = 773.0", table_cell_style), Paragraph("K_B = 1894.4, K_Delta = 671.6", table_cell_bold), Paragraph("Primary model retains global league K (1717.4 / 773.0); sub-cohort re-fit shown", table_cell_style)],
        [Paragraph("Bowlers REML Priors", table_cell_style), Paragraph("K_B = 1312.9, K_Delta = 1041.4", table_cell_style), Paragraph("K_B = 1384.0, K_Delta = 963.5", table_cell_bold), Paragraph("Primary model retains global league K (1312.9 / 1041.4); sub-cohort re-fit shown", table_cell_style)],
        [Paragraph("Population Means (mu)", table_cell_style), Paragraph("Bat: +7.07 / +3.38 | Bowl: +3.37 / +1.03", table_cell_style), Paragraph("Bat: +7.02 / +3.57 | Bowl: +2.53 / +1.14", table_cell_bold), Paragraph("Filtered eligible cohort means used for all primary Bayesian shrinkage", table_cell_style)],
        [Paragraph("Null Test p-values", table_cell_style), Paragraph("Bat p = 0.0500 | Bowl p = 0.0060", table_cell_style), Paragraph("Bat p = 0.0440 | Bowl p = 0.0300", table_cell_bold), Paragraph("Bowler p shifts as excluding Muqeem narrows observed std from 4.089 to 4.052", table_cell_style)],
        [Paragraph("Virat Kohli Verification", table_cell_style), Paragraph("Rating +17.43 (Rank 17 overall)", table_cell_style), Paragraph("Rating +17.52 (Rank 16 overall)", table_cell_bold), Paragraph("N_B 1787, Raw_B +14.33, Shk_B +10.75; N_D 669, Raw_D +10.45, Shk_D +6.76", table_cell_style)],
        [Paragraph("Rohit Sharma Verification", table_cell_style), Paragraph("Rating +5.30 (Rank 124 overall)", table_cell_style), Paragraph("Rating +5.40 (Rank 117 overall)", table_cell_bold), Paragraph("N_B 1181, Raw_B -5.62, Shk_B +1.87; N_D 438, Raw_D +3.45, Shk_D +3.53", table_cell_style)],
    ]
    t_param = Table(param_comp_data, colWidths=[90, 110, 115, 235])
    t_param = Table(param_comp_data, colWidths=[105, 115, 120, 165])
    t_param.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#004B87')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0.4),
        ('TOPPADDING', (0, 0), (-1, -1), 0.4),
        ('LEFTPADDING', (0, 0), (-1, -1), 1.0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 1.0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0.8),
        ('TOPPADDING', (0, 0), (-1, -1), 0.8),
        ('LEFTPADDING', (0, 0), (-1, -1), 1.5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 1.5),
        ('GRID', (0, 0), (-1, -1), 0.35, colors.HexColor('#DDDDDD')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')])
    ]))
    page3_elements.append(t_param)
    page3_elements.append(Spacer(1, 0.8))
    story.append(t_param)
    story.append(Paragraph("Table 4.1: Model parameters estimated across cohorts, confirming primary model retains global league K.", caption_style))

    # Top-10 Forest Plots with Null Band
    forest_bat_path = OUTPUTS_DIR / "top10_batters_intervals.png"
    forest_bowl_path = OUTPUTS_DIR / "top10_bowlers_intervals.png"
    if forest_bat_path.exists() and forest_bowl_path.exists():
        forest_bat = Image(str(forest_bat_path), width=268, height=105)
        forest_bowl = Image(str(forest_bowl_path), width=268, height=105)
        forest_tbl = Table([[forest_bat, forest_bowl]], colWidths=[273, 273])
        forest_tbl.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ]))
        page3_elements.append(forest_tbl)
        page3_elements.append(Spacer(1, 0.8))
    # =========================================================================
    # PAGE 4: High-Resolution Forest Plots & Dip Ordering Rules
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("Figure 2: Top 10 Batters Under Pressure Forest Plot (90% CI vs 95% Null Band)", h2_style))
    img_forest_bat = Image(str(OUTPUTS_DIR / "top10_batters_intervals.png"), width=505, height=192)
    story.append(img_forest_bat)
    story.append(Paragraph("Figure 2: Top 10 Batters posterior ratings with 90% match-grouped bootstrap credible intervals and 95% within-match null permutation band.", caption_style))

    page3_elements.append(Paragraph("5. Sensitivity Analysis Across 14 Specifications & Bowler Wicket Benchmark", h1_style))
    page3_elements.append(Paragraph(
    story.append(Spacer(1, 1))
    story.append(Paragraph("Figure 3: Top 10 Bowlers Under Pressure Forest Plot (90% CI vs 95% Null Band)", h2_style))
    img_forest_bowl = Image(str(OUTPUTS_DIR / "top10_bowlers_intervals.png"), width=505, height=192)
    story.append(img_forest_bowl)
    story.append(Paragraph("Figure 3: Top 10 Bowlers posterior ratings with 90% match-grouped bootstrap credible intervals and 95% within-match null permutation band.", caption_style))

    story.append(Paragraph("5. Ordering Rules for Pressure Dips & Decision Framework", h1_style))
    story.append(Paragraph(
        "<b>Ordering Rule on Pressure Dips:</b> Primary ranking is <b>Rating = Baseline + Pressure Effect with NO dip exclusion</b> (Abhishek #6, Bumrah #4). "
        "Under <b>Rule B (Clutch-Constrained: Delta_shrunk >= 0)</b>, Bumrah and Abhishek are excluded due to negative pressure deltas (-5.11 and -2.25), allowing Stoinis (Bat #10) and Kuldeep (Bowl #10) into the Top 10.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Top-10 Players with 90% Interval Strictly Above Zero:</b> Six players—<b>Suryakumar Yadav</b> [+0.4, +17.1], <b>Reeza Hendricks</b> [+5.5, +22.5], <b>Rinku Singh</b> [+3.7, +18.7], <b>Shreyas Iyer</b> [+0.5, +19.8], <b>Matheesha Pathirana</b> [+0.7, +14.2], and <b>Mitchell Santner</b> [+0.3, +15.8]—indicate statistically verifiable clutch elevation above ordinary baseline at the 90% credibility level.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Plain Audit on Abhishek Sharma & Jasprit Bumrah:</b> Abhishek Sharma posts an extraordinary baseline (+24.17 shrunk) but a negative pressure delta (-2.25 shrunk; 90% CI [-17.6, +11.4]). Jasprit Bumrah leads all bowlers in baseline runs saved (+18.59 shrunk) but records a negative pressure delta (-5.11 shrunk; 90% CI [-13.7, +4.0]). Under Rule A, their high baselines secure Ranks 6 and 4. Under Rule B, both are excluded. Under a credibly negative test (CI upper &lt; 0), both are retained because their intervals span zero.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Bowler Wicket Value Benchmark:</b> Top 20 bowler evaluation confirms moderate sensitivity to wicket valuation (8/10 overlap vs HP-specific, 7/10 vs Flat). Middle-overs spinners gain when middle-overs wickets are credited at 8.85 or 10.71 runs rather than the phase-calibrated 8.13 runs; Phase-Specific valuation (PP 14.36, Mid 8.13, Death 2.92) is adopted because it empirically reflects the actual subsequent innings run-penalty.",
        body_style
    ))

    # =========================================================================
    # PAGE 5: Sensitivity Analysis (Table 6.1), Famous Players (Table 6.2), Limitations
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("6. Sensitivity Analysis Across 14 Specifications & Famous Player Diagnostics", h1_style))
    story.append(Paragraph(
        "<b>Rank Ranges [Min, Max] across 14 Specifications (Volume Cutoff Policy):</b> Players failing a volume cutoff (e.g. min 200 HP balls in Spec 10) are treated as Unranked (excluded from that spec) rather than assigned an artificial penalty rank. "
        "Ranges strictly bound primary rank: <i>Batters:</i> Suryakumar [1, 2]; Sooryavanshi [2, 7]; Buttler [3, 7]; Klaasen [3, 20]; Hendricks [2, 9]; Abhishek [2, 21]; Salt [4, 8]; Rinku [1, 12]; Iyer [6, 12]; David [7, 10]. "
        "<i>Bowlers:</i> Hazlewood [1, 6]; Pathirana [1, 2]; Narine [1, 4]; Bumrah [4, 25]; Duffy [4, 11]; Rashid [3, 12]; Ferguson [5, 21]; Varun [4, 10]; Ellis [3, 20]; Santner [7, 16]. "
        "<b>Top-10 Overlap across Specifications:</b> S1 (Primary Phase-Wkts) 10/10 bat, 10/10 bowl; S2 (Flat 8.85) 10/10 bat, 7/10 bowl; S3 (Wkt 7.0) 10/10 bat, 7/10 bowl; S4 (Wkt 9.0) 10/10 bat, 7/10 bowl; S5 (Wkt 11.0) 10/10 bat, 7/10 bowl; S6 (Wkt 13.0) 9/10 bat, 7/10 bowl; S7 (Top 20% Lev) 9/10 bat, 7/10 bowl; S8 (Top 30% Lev) 8/10 bat, 9/10 bowl; S9 (Min 150b) 10/10 bat, 9/10 bowl (Ellis #11; Duffy #5); S10 (Min 200b) 9/10 bat (Sooryavanshi unranked), 9/10 bowl (Duffy unranked); S11 (IPL-only) 8/10 bat, 7/10 bowl; S12 (Tier 1 only) 10/10 bat, 9/10 bowl; S13 (T20I excluded) 8/10 bat, 7/10 bowl; S14 (Recency) 10/10 bat, 8/10 bowl. "
        "<b>Bowler Wicket Value Benchmark:</b> Top 20 bowler evaluation confirms moderate sensitivity to wicket valuation (8/10 overlap vs HP-specific, 7/10 vs Flat). Middle-overs spinners gain when middle-overs wickets are credited at 8.85 or 10.71 runs rather than the phase-calibrated 8.13 runs; Phase-Specific valuation (PP 14.36, Mid 8.13, Death 2.92) is adopted because it empirically reflects the actual subsequent innings run-penalty.",
        "<b>Top-10 Overlap across Specifications:</b> S1 (Primary Phase-Wkts) 10/10 bat, 10/10 bowl; S2 (Flat 8.85) 10/10 bat, 7/10 bowl; S3 (Wkt 7.0) 10/10 bat, 7/10 bowl; S4 (Wkt 9.0) 10/10 bat, 7/10 bowl; S5 (Wkt 11.0) 10/10 bat, 7/10 bowl; S6 (Wkt 13.0) 9/10 bat, 7/10 bowl; S7 (Top 20% Lev) 9/10 bat, 7/10 bowl; S8 (Top 30% Lev) 8/10 bat, 9/10 bowl; S9 (Min 150b) 10/10 bat, 9/10 bowl (Ellis #11; Duffy #5); S10 (Min 200b) 9/10 bat (Sooryavanshi unranked), 9/10 bowl (Duffy unranked); S11 (IPL-only) 8/10 bat, 7/10 bowl; S12 (Tier 1 only) 10/10 bat, 9/10 bowl; S13 (T20I excluded) 8/10 bat, 7/10 bowl; S14 (Recency) 10/10 bat, 8/10 bowl.",
        body_style
    ))
    page3_elements.append(Spacer(1, 0.8))

    # Famous Players Sanity Diagnostics Table (Direct Delivery-Level Numbers)
    page3_elements.append(Paragraph("6. Famous Player Sanity Diagnostics (Direct Delivery-Level Verification)", h1_style))
    # Table 6.1: Complete Specification Sensitivity Matrix
    story.append(Paragraph("Table 6.1: Complete Specification Sensitivity Matrix (14 Distinct Formulations)", h2_style))
    sens_specs_data = [
        [Paragraph("Spec", table_cell_header), Paragraph("Specification Definition", table_cell_header), Paragraph("Batters Overlap", table_cell_header), Paragraph("Bowlers Overlap", table_cell_header), Paragraph("Summary Sensitivity Impact", table_cell_header)],
        [Paragraph("S1", table_cell_bold), Paragraph("Primary Base: Phase-Specific Wickets (PP 14.36, Mid 8.13, Death 2.92)", table_cell_style), Paragraph("10/10 (1.00)", table_cell_style), Paragraph("10/10 (1.00)", table_cell_style), Paragraph("Primary model baseline reference specification", table_cell_style)],
        [Paragraph("S2", table_cell_bold), Paragraph("Flat Wicket Value = 8.85 runs", table_cell_style), Paragraph("10/10 (1.00)", table_cell_style), Paragraph("7/10 (0.54)", table_cell_style), Paragraph("Spinners gain with flat middle wickets", table_cell_style)],
        [Paragraph("S3", table_cell_bold), Paragraph("Wicket Value = 7.0 runs", table_cell_style), Paragraph("10/10 (1.00)", table_cell_style), Paragraph("7/10 (0.54)", table_cell_style), Paragraph("Economy-dominant bowlers gain rank", table_cell_style)],
        [Paragraph("S4", table_cell_bold), Paragraph("Wicket Value = 9.0 runs", table_cell_style), Paragraph("10/10 (1.00)", table_cell_style), Paragraph("7/10 (0.54)", table_cell_style), Paragraph("Similar to flat 8.85 benchmark", table_cell_style)],
        [Paragraph("S5", table_cell_bold), Paragraph("Wicket Value = 11.0 runs", table_cell_style), Paragraph("10/10 (1.00)", table_cell_style), Paragraph("7/10 (0.54)", table_cell_style), Paragraph("Wicket-taking specialists elevated", table_cell_style)],
        [Paragraph("S6", table_cell_bold), Paragraph("Wicket Value = 13.0 runs", table_cell_style), Paragraph("9/10 (0.82)", table_cell_style), Paragraph("7/10 (0.54)", table_cell_style), Paragraph("Wicket penalties impact aggressive hitters", table_cell_style)],
        [Paragraph("S7", table_cell_bold), Paragraph("Pressure Threshold: Top 20% Leverage", table_cell_style), Paragraph("9/10 (0.82)", table_cell_style), Paragraph("7/10 (0.54)", table_cell_style), Paragraph("Extreme crisis deliveries isolated", table_cell_style)],
        [Paragraph("S8", table_cell_bold), Paragraph("Pressure Threshold: Top 30% Leverage", table_cell_style), Paragraph("8/10 (0.67)", table_cell_style), Paragraph("9/10 (0.82)", table_cell_style), Paragraph("Broader pressure cohort expands sample size", table_cell_style)],
        [Paragraph("S9", table_cell_bold), Paragraph("Minimum Sample: 150 Balls", table_cell_style), Paragraph("10/10 (1.00)", table_cell_style), Paragraph("9/10 (0.82)", table_cell_style), Paragraph("All 10 batters qualify (Sooryavanshi #2 with 168b); 9/10 bowlers qualify (Duffy #5 with 191b; Ellis slips to #11 as Kuldeep enters at #8)", table_cell_style)],
        [Paragraph("S10", table_cell_bold), Paragraph("Minimum Sample: 200 Balls", table_cell_style), Paragraph("9/10 (0.82)", table_cell_style), Paragraph("9/10 (0.82)", table_cell_style), Paragraph("Sooryavanshi (168b) and Duffy (191b) unranked", table_cell_style)],
        [Paragraph("S11", table_cell_bold), Paragraph("Competition: IPL-Only", table_cell_style), Paragraph("8/10 (0.67)", table_cell_style), Paragraph("7/10 (0.54)", table_cell_style), Paragraph("Hendricks, Salt, Duffy, Santner lose T20I volume", table_cell_style)],
        [Paragraph("S12", table_cell_bold), Paragraph("Competition: Tier 1 Only (No A-Team/Associate)", table_cell_style), Paragraph("10/10 (1.00)", table_cell_style), Paragraph("9/10 (0.82)", table_cell_style), Paragraph("Highly robust; removes associate development games", table_cell_style)],
        [Paragraph("S13", table_cell_bold), Paragraph("Competition: T20I Excluded", table_cell_style), Paragraph("8/10 (0.67)", table_cell_style), Paragraph("7/10 (0.54)", table_cell_style), Paragraph("Identical to IPL-only constraint", table_cell_style)],
        [Paragraph("S14", table_cell_bold), Paragraph("Weighting: Recency Weighting (2022-26)", table_cell_style), Paragraph("10/10 (1.00)", table_cell_style), Paragraph("8/10 (0.67)", table_cell_style), Paragraph("Exponential decay favoring 2024–25 seasons", table_cell_style)],
    ]
    t_sens = Table(sens_specs_data, colWidths=[28, 175, 62, 62, 178])
    t_sens.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#004B87')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0.6),
        ('TOPPADDING', (0, 0), (-1, -1), 0.6),
        ('LEFTPADDING', (0, 0), (-1, -1), 1.5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 1.5),
        ('GRID', (0, 0), (-1, -1), 0.35, colors.HexColor('#DDDDDD')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')])
    ]))
    story.append(t_sens)
    story.append(Paragraph("Table 6.1: Jaccard overlap and stability across 14 distinct model specifications.", caption_style))

    # Table 6.2: Famous Player Sanity Diagnostics Table
    story.append(Paragraph("Table 6.2: Famous Player Sanity Diagnostics (Direct Delivery-Level Numbers)", h2_style))
    famous_data = [
        [Paragraph("Player", table_cell_header), Paragraph("Role", table_cell_header), Paragraph("HP Balls", table_cell_header), Paragraph("Actual HP", table_cell_header), Paragraph("Expected HP", table_cell_header), Paragraph("Rating", table_cell_header), Paragraph("Rk", table_cell_header), Paragraph("Direct Delivery-Level Verification", table_cell_header)],
        [Paragraph("Suryakumar Yadav", table_cell_bold), Paragraph("Batter", table_cell_style), Paragraph("697", table_cell_style), Paragraph("SR 167.9", table_cell_style), Paragraph("Exp SR 136.4", table_cell_style), Paragraph("+28.39", table_cell_bold), Paragraph("1", table_cell_style), Paragraph("Direct ball-by-ball: 697 HP balls faced (723 total incl 26 wides), 1170 runs, 27 outs. HP SR 167.9 (+31.5 SR above exp); 69.4% shrunk succ rate. Shrunk base +19.39, delta +8.99. Rank 1 globally.", table_cell_style)],
        [Paragraph("Jos Buttler", table_cell_bold), Paragraph("Batter", table_cell_style), Paragraph("557", table_cell_style), Paragraph("SR 164.6", table_cell_style), Paragraph("Exp SR 140.9", table_cell_style), Paragraph("+23.06", table_cell_bold), Paragraph("3", table_cell_style), Paragraph("Direct ball-by-ball: 557 HP balls faced (568 total incl 11 wides), 917 runs, 19 outs. HP SR 164.6 (+23.7 SR above exp); 66.7% shrunk succ rate. Shrunk base +14.37, delta +8.68. Rank 3 overall.", table_cell_style)],
        [Paragraph("Virat Kohli", table_cell_bold), Paragraph("Batter", table_cell_style), Paragraph("669", table_cell_style), Paragraph("SR 149.8", table_cell_style), Paragraph("Exp SR 141.2", table_cell_style), Paragraph("+17.52", table_cell_bold), Paragraph("16", table_cell_style), Paragraph("Direct ball-by-ball: 669 HP balls (excluding 23 wides), 1002 runs, 20 outs (2.99% out rate vs 4.65% exp). Actual SR 149.8 (+8.6 SR). Hierarchical rating: Shrunk base +10.75, shrunk delta +6.76, Rating +17.52, Rank 16.", table_cell_style)],
        [Paragraph("Rohit Sharma", table_cell_bold), Paragraph("Batter", table_cell_style), Paragraph("438", table_cell_style), Paragraph("SR 150.7", table_cell_style), Paragraph("Exp SR 141.3", table_cell_style), Paragraph("+5.40", table_cell_style), Paragraph("117", table_cell_style), Paragraph("Direct ball-by-ball: 438 HP balls (excluding 15 wides), 660 runs, 26 outs (5.94% vs 4.44% exp). Actual SR 150.7 vs Exp 141.3; early outs create wkt deficit. Shrunk base +1.87, shrunk delta +3.53, Rating +5.40, Rank 117.", table_cell_style)],
        [Paragraph("Josh Hazlewood", table_cell_bold), Paragraph("Bowler", table_cell_style), Paragraph("399", table_cell_style), Paragraph("Econ 7.67", table_cell_style), Paragraph("Exp Econ 8.35", table_cell_style), Paragraph("+17.83", table_cell_bold), Paragraph("1", table_cell_style), Paragraph("Direct ball-by-ball: 399 HP legal balls, 510 runs, 34 wkts; HP SR 11.7. Suppresses 0.68 RPO below exp. Shrunk base +9.13, delta +8.70. Rank 1 bowler globally.", table_cell_style)],
        [Paragraph("Matheesha Pathirana", table_cell_bold), Paragraph("Bowler", table_cell_style), Paragraph("282", table_cell_style), Paragraph("Econ 7.43", table_cell_style), Paragraph("Exp Econ 8.65", table_cell_style), Paragraph("+17.48", table_cell_bold), Paragraph("2", table_cell_style), Paragraph("Direct ball-by-ball: 282 HP legal balls, 349 runs, 26 wkts; HP SR 10.8. Suppresses 1.22 RPO below exp. Shrunk base +9.82, delta +7.66. Rank 2 overall.", table_cell_style)],
        [Paragraph("Jasprit Bumrah", table_cell_bold), Paragraph("Bowler", table_cell_style), Paragraph("439", table_cell_style), Paragraph("Econ 7.61", table_cell_style), Paragraph("Exp Econ 8.68", table_cell_style), Paragraph("+13.48", table_cell_bold), Paragraph("4", table_cell_style), Paragraph("Direct ball-by-ball: 439 HP legal balls, 557 runs, 14 wkts. Actual Econ 7.61 vs Exp 8.68 (-1.07 rpo saved); Wkt Rate 3.19% vs Exp 5.07%. Shrunk base +18.59 secures Rank 4 overall.", table_cell_style)],
        [Paragraph("Rashid Khan", table_cell_bold), Paragraph("Bowler", table_cell_style), Paragraph("658", table_cell_style), Paragraph("Econ 6.72", table_cell_style), Paragraph("Exp Econ 8.35", table_cell_style), Paragraph("+12.97", table_cell_bold), Paragraph("6", table_cell_style), Paragraph("Direct ball-by-ball: 658 HP legal balls, 737 runs, 42 wkts. Actual Econ 6.72 vs Exp 8.35 (-1.63 rpo saved); HP Wkt Rate 6.38% (SR 15.7). Shrunk base +5.70, delta +7.27. Rank 6 overall.", table_cell_style)],
    ]
    t_famous = Table(famous_data, colWidths=[65, 24, 28, 36, 38, 28, 14, 317])
    t_famous = Table(famous_data, colWidths=[78, 28, 32, 42, 42, 34, 16, 233])
    t_famous.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#004B87')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0.4),
        ('TOPPADDING', (0, 0), (-1, -1), 0.4),
        ('LEFTPADDING', (0, 0), (-1, -1), 1.0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 1.0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0.7),
        ('TOPPADDING', (0, 0), (-1, -1), 0.7),
        ('LEFTPADDING', (0, 0), (-1, -1), 1.5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 1.5),
        ('GRID', (0, 0), (-1, -1), 0.35, colors.HexColor('#DDDDDD')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')])
    ]))
    page3_elements.append(t_famous)
    page3_elements.append(Spacer(1, 0.8))
    story.append(t_famous)
    story.append(Paragraph("Table 6.2: Sanity checks against career international stars with delivery-level data accounting.", caption_style))

    # Real-World Limitations & Reproduction
    story.append(KeepTogether(page3_elements))

    # Limitations & Reproduction
    limitations_p = Paragraph(
        "<b>7. Honest Limitations, Caveats & Reproduction:</b> (1) <i>Rank Distinguishability:</i> Pairwise bootstrap win probabilities (49%-64%) indicate top-10 positions form an elite cluster rather than immutable individual ranks. "
        "(2) <i>Impact Player Rule:</i> Post-2023 IPL rules artificially increased batting depths, elevating aggression earlier in chases. "
        "(3) <i>Expected Wicket Noise:</i> Expected wicket model achieves ROC-AUC 0.595, reflecting that dismissals are high-variance events; rolling Bayesian updates are advised. "
    # Section 7: Limitations & Reproduction
    story.append(Paragraph("7. Honest Limitations, Caveats & Reproduction", h1_style))
    story.append(Paragraph(
        "<b>(1) Rank Distinguishability:</b> Pairwise bootstrap win probabilities (49%-64%) indicate top-10 positions form an elite cluster rather than immutable individual ranks. "
        "<b>(2) Impact Player Rule:</b> Post-2023 IPL rules artificially increased batting depths, elevating aggression earlier in chases. "
        "<b>(3) Expected Wicket Noise:</b> Expected wicket model achieves ROC-AUC 0.595, reflecting that dismissals are high-variance events; rolling Bayesian updates are advised. "
        "<b>Reproduction:</b> Run <code>python run_all.py</code> on Windows PowerShell to reproduce every artifact, model, bootstrap draw, and table end-to-end.",
        body_style
    )
    story.append(limitations_p)
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[+] Successfully exported methodology report PDF to: {pdf_path}")
    # Concluding Sign-Off Bar
    t_signoff = Table([[
        Paragraph("<b>SupeRR Selector Season 2 – Round 1 Final Submission</b> | Author: <b>Kishalay Das</b> | Methodological Pipeline Verified Across 200,999 Deliveries", ParagraphStyle('Sign', fontName='Helvetica', fontSize=7.4, leading=9.2, textColor=colors.HexColor('#004B87'), alignment=1))
    ]], colWidths=[CONTENT_WIDTH])
    t_signoff.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F0F4F8')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#004B87')),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(Spacer(1, 2))
    story.append(t_signoff)

    doc.build(story, canvasmaker=A4NumberedCanvas)
    print(f"[+] Successfully exported A4 methodology report PDF to: {target_path}")

def main():
    target_outputs = OUTPUTS_DIR / "methodology_report.pdf"
    target_report = REPORT_DIR / "methodology_report.pdf"

    print("[*] Generating new 5-page publication-grade methodology report...")
    build_pdf(target_outputs)

    # Sync to report/
    shutil.copyfile(target_outputs, target_report)
    print(f"[+] Synced methodology report to: {target_report}")

if __name__ == "__main__":
    export_pdf()
    main()
