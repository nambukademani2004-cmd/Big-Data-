"""
Bengaluru Air Quality & Meteorology Final A0 Academic Research Poster Generator
Research Title: "A PySpark-Based Big Data Analysis of Air Pollution and Meteorological Patterns in Bengaluru, Karnataka"

Outputs in Final_Poster/:
1. Bengaluru_Air_Pollution_Final_Poster_A0.pptx (Editable A0 Landscape PowerPoint, 1189 x 841 mm)
2. Bengaluru_Air_Pollution_Final_Poster_A0.pdf (Print-ready A0 Landscape PDF)
3. Poster_Preview.png (Ultra high-resolution 4K preview image)
"""

import os
import subprocess
import sys
from pathlib import Path
import json

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# Directory Resolution
BASE_DIR = Path(r"c:\Users\nambu\OneDrive\Desktop\BIG_DATA_POSTER\Bengaluru_Air_Pollution_Research")
CHARTS_DIR = BASE_DIR / "charts"
REPORTS_DIR = BASE_DIR / "reports"
OUTPUT_DIR = Path(r"c:\Users\nambu\OneDrive\Desktop\BIG_DATA_POSTER\Final_Poster")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load Numerical Findings
with open(REPORTS_DIR / "numerical_research_findings.json", "r", encoding="utf-8") as f:
    findings = json.load(f)

# Exact A0 Landscape Dimensions
POSTER_WIDTH = Inches(46.81)    # 1189 mm
POSTER_HEIGHT = Inches(33.11)   # 841 mm

# Curated Academic Visual Tokens
NAVY_HEADER = RGBColor(30, 58, 138)       # #1E3A8A Deep Academic Navy
NAVY_DARK = RGBColor(15, 23, 42)          # #0F172A Slate 900
SLATE_TEXT = RGBColor(51, 65, 85)         # #334155 Body Slate
SLATE_MUTED = RGBColor(100, 116, 139)     # #64748B Secondary
BG_PAGE = RGBColor(248, 250, 252)         # #F8FAFC Clean Off-White
BG_CARD = RGBColor(255, 255, 255)         # #FFFFFF Card White
BORDER_CARD = RGBColor(226, 232, 240)     # #E2E8F0 Subtle Border
ACCENT_TEAL = RGBColor(13, 148, 136)      # #0D9488 Vibrant Teal
ACCENT_AMBER = RGBColor(217, 119, 6)      # #D97706 Warm Amber
ACCENT_CORAL = RGBColor(225, 29, 72)      # #E11D48 Alert Coral


def add_card(slide, left, top, width, height, title, subtitle="", bg_color=BG_CARD, border_color=BORDER_CARD):
    """Creates a modern rounded card container with a crisp title banner."""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    card.line.color.rgb = border_color
    card.line.width = Pt(1.5)

    # Banner header shape
    banner_height = Inches(0.55)
    banner = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, banner_height)
    banner.fill.solid()
    banner.fill.fore_color.rgb = NAVY_HEADER
    banner.line.color.rgb = NAVY_HEADER

    # Header text
    tf = banner.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.18)
    tf.margin_top = Inches(0.08)
    p = tf.paragraphs[0]
    p.text = title.upper()
    p.font.name = "Calibri"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = RGBColor(255, 255, 255)

    if subtitle:
        p2 = tf.add_paragraph()
        p2.text = subtitle
        p2.font.name = "Calibri"
        p2.font.size = Pt(9.5)
        p2.font.italic = True
        p2.font.color.rgb = RGBColor(224, 242, 254)

    return card


def generate_final_a0_poster():
    print("Initializing A0 PowerPoint Presentation (1189 x 841 mm)...")
    prs = Presentation()
    prs.slide_width = POSTER_WIDTH
    prs.slide_height = POSTER_HEIGHT

    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # Slide Background
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, POSTER_WIDTH, POSTER_HEIGHT)
    bg.fill.solid()
    bg.fill.fore_color.rgb = BG_PAGE
    bg.line.fill.background()

    # ==========================================================================
    # TOP HEADER BANNER
    # ==========================================================================
    header_height = Inches(3.2)
    header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, POSTER_WIDTH, header_height)
    header.fill.solid()
    header.fill.fore_color.rgb = NAVY_HEADER
    header.line.fill.background()

    # Bottom Teal Accent Line
    stripe = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, header_height, POSTER_WIDTH, Inches(0.12))
    stripe.fill.solid()
    stripe.fill.fore_color.rgb = ACCENT_TEAL
    stripe.line.fill.background()

    # Title Text Frame
    tb_title = slide.shapes.add_textbox(Inches(1.0), Inches(0.35), Inches(44.81), Inches(2.5))
    tf = tb_title.text_frame
    tf.word_wrap = True

    p_title = tf.paragraphs[0]
    p_title.text = "A PySpark-Based Big Data Analysis of Air Pollution and Meteorological Patterns in Bengaluru, Karnataka"
    p_title.font.name = "Calibri"
    p_title.font.size = Pt(45)
    p_title.font.bold = True
    p_title.font.color.rgb = RGBColor(255, 255, 255)
    p_title.alignment = PP_ALIGN.CENTER

    p_author = tf.add_paragraph()
    p_author.text = "M.Sc. Data Science Research Dissertation | Department of Data Science | Academic Research Poster"
    p_author.font.name = "Calibri"
    p_author.font.size = Pt(20)
    p_author.font.color.rgb = RGBColor(224, 242, 254)
    p_author.alignment = PP_ALIGN.CENTER
    p_author.space_before = Pt(8)

    p_tags = tf.add_paragraph()
    p_tags.text = "Continuous Air Quality Monitoring Network (CPCB / KSPCB) | In-Situ Ground Meteorology | 866,044 Observations (2024–2025) | Apache Spark 4.3.0"
    p_tags.font.name = "Calibri"
    p_tags.font.size = Pt(13.5)
    p_tags.font.bold = True
    p_tags.font.color.rgb = RGBColor(254, 240, 138)
    p_tags.alignment = PP_ALIGN.CENTER
    p_tags.space_before = Pt(6)

    # ==========================================================================
    # 4-COLUMN SCIENTIFIC GRID
    # ==========================================================================
    margin_x = Inches(0.85)
    margin_top = Inches(3.55)
    usable_width = POSTER_WIDTH - (margin_x * 2)
    gap_x = Inches(0.55)
    col_width = (usable_width - (gap_x * 3)) / 4   # ~10.61 Inches each

    col1_x = margin_x
    col2_x = col1_x + col_width + gap_x
    col3_x = col2_x + col_width + gap_x
    col4_x = col3_x + col_width + gap_x

    # --------------------------------------------------------------------------
    # COLUMN 1: Abstract, Introduction & Objectives, Materials & Methods (Flowchart)
    # --------------------------------------------------------------------------
    c1_y = margin_top

    # 1. Abstract Card
    h_abs = Inches(5.1)
    add_card(slide, col1_x, c1_y, col_width, h_abs, "1. Abstract", "Context, Scope & Core Findings")
    tb = slide.shapes.add_textbox(col1_x + Inches(0.2), c1_y + Inches(0.65), col_width - Inches(0.4), h_abs - Inches(0.75))
    tf = tb.text_frame
    tf.word_wrap = True

    abs_bullets = [
        ("Background:", " Bengaluru's accelerated vehicular growth and urban expansion have elevated particulate and gaseous concentrations."),
        ("Research Objective:", " Evaluate spatial pollution heterogeneity across 13 monitoring stations, quantify multi-year seasonal dynamics, and model meteorological dispersion coupling."),
        ("Data & PySpark Pipeline:", " 866,044 continuous 15-minute observations (2024–2025) from CPCB/KSPCB and in-situ ground weather sensors aggregated into 217,313 station-hours using Apache Spark 4.3.0."),
        ("Key Empirical Findings:", " Silk Board exhibited highest mean PM10 (107.12 µg/m³), while Sanegurava Halli remained compliant (42.62 µg/m³). Monsoon rains scrubbed aerosols by 55% down to 45.15 µg/m³. Significant temperature convective dispersion (slope = -1.18, r = -0.21, p < 0.001) and calm wind stagnation (WS < 1.0 m/s: >85 µg/m³)."),
        ("Conclusion:", " Microclimatic conditions (boundary layer height and wind ventilation) govern ground air quality alongside tailpipe emission volumes.")
    ]
    for b_t, b_d in abs_bullets:
        p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = f"• {b_t}"
        r1.font.bold = True
        r1.font.size = Pt(10.5)
        r1.font.color.rgb = NAVY_HEADER
        r2 = p.add_run()
        r2.text = b_d
        r2.font.size = Pt(10.2)
        r2.font.color.rgb = SLATE_TEXT
        p.space_after = Pt(3)

    # 2. Introduction, Problem & Objectives Card
    c1_y += h_abs + Inches(0.25)
    h_intro = Inches(6.0)
    add_card(slide, col1_x, c1_y, col_width, h_intro, "2. Introduction & Research Problem", "Urban Dynamics & Formal Hypotheses")
    tb = slide.shapes.add_textbox(col1_x + Inches(0.2), c1_y + Inches(0.65), col_width - Inches(0.4), h_intro - Inches(0.75))
    tf = tb.text_frame
    tf.word_wrap = True

    intro_bullets = [
        ("Urban Megacity Challenge:", " Bengaluru contains over 10 million registered vehicles, producing intense localized emissions along arterial corridors."),
        ("Meteorological Governing Role:", " Ground-level concentrations are co-governed by atmospheric thermodynamics: nocturnal boundary layer compression traps pollutants, while daytime solar heating fosters convective vertical dispersion."),
        ("Research Problem:", " Prior regional studies relied on coarse monthly averages or isolated single stations, failing to capture hyper-local transit hotspots and intra-day stagnation hazards."),
        ("Formal Research Objectives:", ""),
        ("  1.", " Audit and harmonize 15-minute continuous observations across 13 official CAAQMS stations."),
        ("  2.", " Construct an enterprise PySpark windowing pipeline for scalable hourly temporal aggregation."),
        ("  3.", " Characterize multi-year seasonal dynamics, wet deposition, and 24-hour diurnal commuter cycles."),
        ("  4.", " Quantify thermodynamic and aerodynamic dispersion relationships using in-situ ground sensors.")
    ]
    for b_t, b_d in intro_bullets:
        p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = f"• {b_t}" if not b_t.startswith("  ") else b_t
        r1.font.bold = True
        r1.font.size = Pt(10.2)
        r1.font.color.rgb = NAVY_HEADER
        r2 = p.add_run()
        r2.text = b_d
        r2.font.size = Pt(9.8)
        r2.font.color.rgb = SLATE_TEXT
        p.space_after = Pt(2)

    # 3. Materials & Methods Card (with Flowchart)
    c1_y += h_intro + Inches(0.25)
    h_meth = Inches(17.4)
    add_card(slide, col1_x, c1_y, col_width, h_meth, "3. Materials & Methods: PySpark Pipeline", "Data Hygiene, Schema Enforcement & Flowchart")
    tb = slide.shapes.add_textbox(col1_x + Inches(0.2), c1_y + Inches(0.65), col_width - Inches(0.4), Inches(5.8))
    tf = tb.text_frame
    tf.word_wrap = True

    meth_bullets = [
        ("Data Provenance & Scope:", " 13 official Continuous Ambient Air Quality Monitoring Stations (CAAQMS) operated by CPCB and KSPCB, accessed via OpenCity portal."),
        ("Study Duration & Volume:", " January 1, 2024 through December 31, 2025; 866,057 raw continuous observations."),
        ("Quality Assurance & Hygiene:", " Sanitized boundary artifacts; exactly 866,044 valid records retained; zero duplicates detected; authentic missing values preserved without artificial zero-fill."),
        ("In-Situ Weather Instrumentation:", " Continuous surface temperature, relative humidity, horizontal wind speed, wind direction, barometric pressure, and solar radiation recorded directly at monitoring stations."),
        ("PySpark Big Data Aggregation:", " GroupBy and date_trunc('hour', col('Timestamp')) windowing in Apache Spark 4.3.0 aggregated 15-minute readings into 217,313 station-hour records in 60.05 seconds.")
    ]
    for b_t, b_d in meth_bullets:
        p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = f"• {b_t}"
        r1.font.bold = True
        r1.font.size = Pt(10.2)
        r1.font.color.rgb = NAVY_HEADER
        r2 = p.add_run()
        r2.text = b_d
        r2.font.size = Pt(9.8)
        r2.font.color.rgb = SLATE_TEXT
        p.space_after = Pt(2.5)

    # Embed Methodology Flowchart Image
    flowchart_file = CHARTS_DIR / "methodology_flowchart.png"
    if flowchart_file.exists():
        fc_top = c1_y + Inches(6.8)
        fc_width = col_width - Inches(0.4)
        fc_height = Inches(5.2)
        slide.shapes.add_picture(str(flowchart_file), col1_x + Inches(0.2), fc_top, width=fc_width, height=fc_height)

        # Flowchart Caption Box
        cap_tb = slide.shapes.add_textbox(col1_x + Inches(0.2), fc_top + fc_height + Inches(0.1), fc_width, Inches(4.8))
        cap_tf = cap_tb.text_frame
        cap_tf.word_wrap = True
        p_cap = cap_tf.paragraphs[0]
        r_c1 = p_cap.add_run()
        r_c1.text = "Methodology Flowchart Overview: "
        r_c1.font.bold = True
        r_c1.font.size = Pt(10)
        r_c1.font.color.rgb = NAVY_HEADER
        r_c2 = p_cap.add_run()
        r_c2.text = (
            "Illustrates the five core analytical stages: (1) Raw continuous data ingestion; "
            "(2) PySpark data hygiene, null preservation, and schema casting; "
            "(3) Hourly windowing aggregation yielding 217,313 station-hour records; "
            "(4) Spatial, temporal, and thermodynamic modeling; and (5) Academic research dissemination. "
            "All processes executed on Apache Spark 4.3.0 with OpenJDK 17 LTS."
        )
        r_c2.font.size = Pt(9.5)
        r_c2.font.color.rgb = SLATE_TEXT

    # --------------------------------------------------------------------------
    # COLUMN 2: Results Section 1 (Figure 1 & Figure 2)
    # --------------------------------------------------------------------------
    c2_y = margin_top
    h_res1 = Inches(29.0)
    add_card(slide, col2_x, c2_y, col_width, h_res1, "4. Results 1: Spatial & Seasonal Patterns", "Monitoring Network Comparison & Multi-Year Trends")

    # Figure 1: Spatial Comparison
    c1_img = CHARTS_DIR / "chart1_station_pollution_comparison.png"
    if c1_img.exists():
        img_w = col_width - Inches(0.4)
        img_h = Inches(6.8)
        slide.shapes.add_picture(str(c1_img), col2_x + Inches(0.2), c2_y + Inches(0.68), width=img_w, height=img_h)

        tb1 = slide.shapes.add_textbox(col2_x + Inches(0.2), c2_y + Inches(7.55), img_w, Inches(6.0))
        tf1 = tb1.text_frame
        tf1.word_wrap = True

        p1 = tf1.paragraphs[0]
        r = p1.add_run()
        r.text = "Figure 1: Spatial Distribution of Mean Particulate Matter Across 13 Stations"
        r.font.bold = True
        r.font.size = Pt(11)
        r.font.color.rgb = NAVY_HEADER
        p1.space_after = Pt(3)

        c1_bullets = [
            ("Chart Explanation:", " Figure 1 compares mean concentrations of PM10 (navy bars) and PM2.5 (teal bars) across all 13 CAAQMS stations over 2024–2025 against CPCB NAAQS annual statutory benchmarks (PM10: 60 µg/m³; PM2.5: 40 µg/m³)."),
            ("Main Numerical Finding:", " Silk Board recorded the highest mean PM10 concentration at 107.12 µg/m³ (78.5% above the 60 µg/m³ NAAQS annual limit), followed by RVCE Mailasandra (98.81 µg/m³) and City Railway Station (88.91 µg/m³). Conversely, Sanegurava Halli (42.62 µg/m³) and Hombegowda Nagar (50.64 µg/m³) remained fully compliant. For PM2.5, RVCE Mailasandra was highest at 42.20 µg/m³, while Hombegowda Nagar was lowest at 21.46 µg/m³."),
            ("Academic Interpretation:", " Severe particulate burdens at Silk Board and City Railway Station reflect heavy diesel traffic, sustained vehicular idling, and road dust resuspension at major transit junctions. Residential areas benefit from vegetative buffers and reduced continuous vehicular throughput.")
        ]
        for b_t, b_d in c1_bullets:
            p = tf1.add_paragraph()
            r1 = p.add_run()
            r1.text = f"• {b_t}"
            r1.font.bold = True
            r1.font.size = Pt(10)
            r1.font.color.rgb = NAVY_HEADER
            r2 = p.add_run()
            r2.text = f" {b_d}"
            r2.font.size = Pt(9.6)
            r2.font.color.rgb = SLATE_TEXT
            p.space_after = Pt(2.5)

    # Divider line
    div_y = c2_y + Inches(14.0)
    div_line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, col2_x + Inches(0.4), div_y, col_width - Inches(0.8), Pt(1.5))
    div_line.fill.solid()
    div_line.fill.fore_color.rgb = BORDER_CARD
    div_line.line.fill.background()

    # Figure 2: Multi-Year Temporal Trends
    c2_img = CHARTS_DIR / "chart2_temporal_variation_trends.png"
    if c2_img.exists():
        img_w = col_width - Inches(0.4)
        img_h = Inches(6.8)
        slide.shapes.add_picture(str(c2_img), col2_x + Inches(0.2), div_y + Inches(0.2), width=img_w, height=img_h)

        tb2 = slide.shapes.add_textbox(col2_x + Inches(0.2), div_y + Inches(7.1), img_w, Inches(6.8))
        tf2 = tb2.text_frame
        tf2.word_wrap = True

        p2 = tf2.paragraphs[0]
        r = p2.add_run()
        r.text = "Figure 2: Multi-Year Monthly Trends and Seasonal Aerosol Dynamics (2024–2025)"
        r.font.bold = True
        r.font.size = Pt(11)
        r.font.color.rgb = NAVY_HEADER
        p2.space_after = Pt(3)

        c2_bullets = [
            ("Chart Explanation:", " Figure 2 tracks monthly mean PM10 (navy line) and PM2.5 (teal line) across 24 consecutive months with 95% confidence interval bands, highlighting Monsoon (blue shading) and Winter (gray shading) regimes."),
            ("Main Numerical Finding:", " Particulate levels reach an annual minimum during peak monsoon in June–July 2024 (PM10: 45.15 µg/m³; PM2.5: 17.40 µg/m³), confirming a 55% reduction from winter baselines. Pronounced peaks occurred in March 2024 (PM10: 100.53 µg/m³) and December 2025 (PM10: 98.40 µg/m³; PM2.5: 45.66 µg/m³). Citywide PM10 exceeded the 60 µg/m³ benchmark in 8 out of 12 months annually."),
            ("Academic Interpretation:", " The mid-year trough is driven by mechanical rain washout (wet deposition) scavenging aerosols. Winter and pre-summer peaks result from shallow atmospheric boundary layers, low surface wind speeds, and nocturnal radiation inversions trapping emissions near the ground.")
        ]
        for b_t, b_d in c2_bullets:
            p = tf2.add_paragraph()
            r1 = p.add_run()
            r1.text = f"• {b_t}"
            r1.font.bold = True
            r1.font.size = Pt(10)
            r1.font.color.rgb = NAVY_HEADER
            r2 = p.add_run()
            r2.text = f" {b_d}"
            r2.font.size = Pt(9.6)
            r2.font.color.rgb = SLATE_TEXT
            p.space_after = Pt(2.5)

    # --------------------------------------------------------------------------
    # COLUMN 3: Results Section 2 (Figure 3 & Figure 4)
    # --------------------------------------------------------------------------
    c3_y = margin_top
    h_res2 = Inches(29.0)
    add_card(slide, col3_x, c3_y, col_width, h_res2, "5. Results 2: Diurnal & Thermal Dynamics", "24-Hour Commuter Profiles & Temperature Coupling")

    # Figure 3: Diurnal Cycle
    c3_img = CHARTS_DIR / "chart3_hourly_diurnal_pattern.png"
    if c3_img.exists():
        img_w = col_width - Inches(0.4)
        img_h = Inches(6.8)
        slide.shapes.add_picture(str(c3_img), col3_x + Inches(0.2), c3_y + Inches(0.68), width=img_w, height=img_h)

        tb3 = slide.shapes.add_textbox(col3_x + Inches(0.2), c3_y + Inches(7.55), img_w, Inches(6.0))
        tf3 = tb3.text_frame
        tf3.word_wrap = True

        p3 = tf3.paragraphs[0]
        r = p3.add_run()
        r.text = "Figure 3: Diurnal 24-Hour Cycle of Criteria Air Pollutants in Bengaluru"
        r.font.bold = True
        r.font.size = Pt(11)
        r.font.color.rgb = NAVY_HEADER
        p3.space_after = Pt(3)

        c3_bullets = [
            ("Chart Explanation:", " Figure 3 plots the 24-hour diurnal profile of PM10 and PM2.5 (primary axis) alongside vehicular combustion tracer NO2 (secondary axis), highlighting morning and evening traffic intervals."),
            ("Main Numerical Finding:", " A distinct bimodal profile is observed. The morning peak manifests at 08:00 IST (PM10: 76.18 µg/m³; NO2: 18.77 µg/m³). The evening peak reaches maximum intensity at 20:00 IST (PM10: 87.28 µg/m³; NO2: 20.85 µg/m³), which is ~25% higher than the morning peak. Midday concentrations trough at ~67.4 µg/m³ around 14:00 IST."),
            ("Academic Interpretation:", " Morning and evening peaks align with peak commuter vehicular traffic. The elevated evening peak is intensified by the nocturnal collapse of the planetary boundary layer after sunset, which compresses emissions into a shallow ground-level inversion layer. Midday solar heating fosters vertical mixing and dilutes surface concentrations.")
        ]
        for b_t, b_d in c3_bullets:
            p = tf3.add_paragraph()
            r1 = p.add_run()
            r1.text = f"• {b_t}"
            r1.font.bold = True
            r1.font.size = Pt(10)
            r1.font.color.rgb = NAVY_HEADER
            r2 = p.add_run()
            r2.text = f" {b_d}"
            r2.font.size = Pt(9.6)
            r2.font.color.rgb = SLATE_TEXT
            p.space_after = Pt(2.5)

    # Divider line
    div3_y = c3_y + Inches(14.0)
    div3_line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, col3_x + Inches(0.4), div3_y, col_width - Inches(0.8), Pt(1.5))
    div3_line.fill.solid()
    div3_line.fill.fore_color.rgb = BORDER_CARD
    div3_line.line.fill.background()

    # Figure 4: Temperature vs PM2.5
    c4_img = CHARTS_DIR / "chart4_temperature_pm25_relationship.png"
    if c4_img.exists():
        img_w = col_width - Inches(0.4)
        img_h = Inches(6.8)
        slide.shapes.add_picture(str(c4_img), col3_x + Inches(0.2), div3_y + Inches(0.2), width=img_w, height=img_h)

        tb4 = slide.shapes.add_textbox(col3_x + Inches(0.2), div3_y + Inches(7.1), img_w, Inches(6.8))
        tf4 = tb4.text_frame
        tf4.word_wrap = True

        p4 = tf4.paragraphs[0]
        r = p4.add_run()
        r.text = "Figure 4: Bivariate Relationship Between Ambient Temperature and Fine PM2.5"
        r.font.bold = True
        r.font.size = Pt(11)
        r.font.color.rgb = NAVY_HEADER
        p4.space_after = Pt(3)

        c4_bullets = [
            ("Chart Explanation:", " Figure 4 displays a density hexbin scatter plot of in-situ ambient temperature (°C) against fine particulate matter PM2.5 (µg/m³) with an Ordinary Least Squares (OLS) linear regression trend line over 153,770 paired hourly observations."),
            ("Main Numerical Finding:", " The bivariate relationship demonstrates a statistically significant negative slope of -1.18 µg/m³ per °C (r = -0.21, p < 0.001, R² = 0.044). Under cool conditions (15–20 °C), hourly PM2.5 frequently exceeded 60–80 µg/m³, whereas under warm conditions (>30 °C), PM2.5 dropped below 25 µg/m³."),
            ("Academic Interpretation:", " Solar surface warming induces buoyant convective thermal updrafts, expanding boundary layer mixing height and diluting ground aerosols into a larger atmospheric volume. Cooler temperatures promote atmospheric stability and inversion-driven trapping. Note: correlation reflects thermodynamic dispersion rather than chemical loss.")
        ]
        for b_t, b_d in c4_bullets:
            p = tf4.add_paragraph()
            r1 = p.add_run()
            r1.text = f"• {b_t}"
            r1.font.bold = True
            r1.font.size = Pt(10)
            r1.font.color.rgb = NAVY_HEADER
            r2 = p.add_run()
            r2.text = f" {b_d}"
            r2.font.size = Pt(9.6)
            r2.font.color.rgb = SLATE_TEXT
            p.space_after = Pt(2.5)

    # --------------------------------------------------------------------------
    # COLUMN 4: Results 3 (Fig 5 & 6), Discussion, Limitations & References
    # --------------------------------------------------------------------------
    c4_y = margin_top

    # Results 3 Card (Wind Speed & Heatmap)
    h_col4_top = Inches(18.0)
    add_card(slide, col4_x, c4_y, col_width, h_col4_top, "6. Results 3: Wind Dispersion & Heatmap", "Aerodynamic Ventilation & Cross-Parameter Covariance")

    # Figure 5 Image
    c5_img = CHARTS_DIR / "chart5_wind_speed_pollution_relationship.png"
    if c5_img.exists():
        img_w = col_width - Inches(0.4)
        img_h = Inches(4.5)
        slide.shapes.add_picture(str(c5_img), col4_x + Inches(0.2), c4_y + Inches(0.65), width=img_w, height=img_h)

        tb5 = slide.shapes.add_textbox(col4_x + Inches(0.2), c4_y + Inches(5.2), img_w, Inches(2.9))
        tf5 = tb5.text_frame
        tf5.word_wrap = True
        p5 = tf5.paragraphs[0]
        r = p5.add_run()
        r.text = "Fig. 5 Non-Linear Wind Speed Dispersion: "
        r.font.bold = True
        r.font.size = Pt(10)
        r.font.color.rgb = NAVY_HEADER
        r2 = p5.add_run()
        r2.text = "Binned dispersion curve reveals an exponential decline in particulates. In the calm stagnation regime (WS < 1.0 m/s), PM10 averages >85.4 µg/m³. Moderate breezes (>2.5 m/s) enhance horizontal advection, reducing mean particulate load by 42% (<48.6 µg/m³). Horizontal ventilation is a primary threshold driver preventing acute air pollution episodes."
        r2.font.size = Pt(9.3)
        r2.font.color.rgb = SLATE_TEXT

    # Figure 6 Image
    c6_img = CHARTS_DIR / "chart6_air_quality_weather_correlation_heatmap.png"
    if c6_img.exists():
        img_w = col_width - Inches(0.4)
        img_h = Inches(4.6)
        slide.shapes.add_picture(str(c6_img), col4_x + Inches(0.2), c4_y + Inches(8.3), width=img_w, height=img_h)

        tb6 = slide.shapes.add_textbox(col4_x + Inches(0.2), c4_y + Inches(13.1), img_w, Inches(4.7))
        tf6 = tb6.text_frame
        tf6.word_wrap = True
        p6 = tf6.paragraphs[0]
        r = p6.add_run()
        r.text = "Fig. 6 Cross-Correlation Matrix: "
        r.font.bold = True
        r.font.size = Pt(10)
        r.font.color.rgb = NAVY_HEADER
        r2 = p6.add_run()
        r2.text = "Lower-triangle heatmap across 12 atmospheric parameters confirms: (1) Strong co-pollutant coupling among combustion tracers (PM2.5–PM10 r = +0.43 to +0.88; NO2–CO r = +0.29 to +0.53); (2) Inverse thermodynamic coupling between Temperature and Relative Humidity (r = -0.71); and (3) Positive solar radiation association with secondary photochemical Ozone formation (r = +0.26)."
        r2.font.size = Pt(9.3)
        r2.font.color.rgb = SLATE_TEXT

    # Discussion & Policy Implications Card
    c4_y += h_col4_top + Inches(0.25)
    h_disc = Inches(6.4)
    add_card(slide, col4_x, c4_y, col_width, h_disc, "7. Discussion & Environmental Policy", "Clean Air Action Plans & Research Limitations")
    tbd = slide.shapes.add_textbox(col4_x + Inches(0.2), c4_y + Inches(0.62), col_width - Inches(0.4), h_disc - Inches(0.7))
    tfd = tbd.text_frame
    tfd.word_wrap = True

    disc_bullets = [
        ("Transit Hotspot Interventions:", " Severe particulate non-compliance at Silk Board and RVCE Mailasandra mandates priority interventions: intelligent signal synchronization, elevated flyovers, dust-suppression misting, and accelerated electric bus adoption."),
        ("Meteorological Stagnation Alerts:", " Municipal dynamic traffic throttling should be enforced during winter evenings when horizontal wind speed drops below 1.0 m/s and temperatures fall below 20 °C."),
        ("Limitations & Data Integrity:", " Observations utilize continuous in-situ CAAQMS ground weather sensors; gridded ERA5 reanalysis required an ECMWF CDS API key not configured in the workspace. City Railway Station and Sanegurava Halli lack dedicated PM2.5 beta-attenuation sensors (retained as authentic nulls). Two-year means are evaluated against annual benchmarks for chronic exposure, not formal regulatory non-attainment.")
    ]
    for b_t, b_d in disc_bullets:
        p = tfd.add_paragraph() if tfd.paragraphs[0].text else tfd.paragraphs[0]
        r1 = p.add_run()
        r1.text = f"• {b_t}"
        r1.font.bold = True
        r1.font.size = Pt(9.8)
        r1.font.color.rgb = NAVY_HEADER
        r2 = p.add_run()
        r2.text = f" {b_d}"
        r2.font.size = Pt(9.3)
        r2.font.color.rgb = SLATE_TEXT
        p.space_after = Pt(2)

    # References & Acknowledgements Card
    c4_y += h_disc + Inches(0.2)
    h_ref = Inches(4.15)
    add_card(slide, col4_x, c4_y, col_width, h_ref, "8. References & Acknowledgements", "APA 7 Citations, Data Sources & Repository")
    tbr = slide.shapes.add_textbox(col4_x + Inches(0.2), c4_y + Inches(0.6), col_width - Inches(2.2), h_ref - Inches(0.7))
    tfr = tbr.text_frame
    tfr.word_wrap = True

    refs = [
        "CPCB. (2009). National Ambient Air Quality Standards. The Gazette of India, Central Pollution Control Board.",
        "Seinfeld, J. H., & Pandis, S. N. (2016). Atmospheric Chemistry and Physics (3rd ed.). John Wiley & Sons.",
        "Zahid, M., et al. (2021). PySpark for Big Data Analytics in Urban Air Quality. Atmospheric Environment, 245, 118021."
    ]
    for rf in refs:
        p = tfr.add_paragraph() if tfr.paragraphs[0].text else tfr.paragraphs[0]
        r = p.add_run()
        r.text = f"• {rf}"
        r.font.size = Pt(8.2)
        r.font.color.rgb = SLATE_MUTED
        p.space_after = Pt(2)

    # Embed QR Code
    qr_img = CHARTS_DIR / "project_qr_code.png"
    if qr_img.exists():
        qr_size = Inches(1.5)
        slide.shapes.add_picture(str(qr_img), col4_x + col_width - Inches(1.8), c4_y + Inches(0.7), width=qr_size, height=qr_size)

    # Save PPTX Deliverable
    out_pptx = OUTPUT_DIR / "Bengaluru_Air_Pollution_Final_Poster_A0.pptx"
    prs.save(out_pptx)
    print(f"[OK] PowerPoint Poster saved to: {out_pptx}")
    return out_pptx


def export_pdf_and_preview_via_com(pptx_path: Path):
    """Exports PDF and 4K preview image using native PowerPoint COM."""
    pdf_path = OUTPUT_DIR / "Bengaluru_Air_Pollution_Final_Poster_A0.pdf"
    preview_path = OUTPUT_DIR / "Poster_Preview.png"

    ps_script = f"""
    $ppt = New-Object -ComObject PowerPoint.Application
    $pres = $ppt.Presentations.Open('{str(pptx_path)}')
    # Export PDF
    $pres.SaveAs('{str(pdf_path)}', [Microsoft.Office.Interop.PowerPoint.PpSaveAsFileType]::ppSaveAsPDF)
    # Export High-Resolution 4K Slide Preview PNG (3840 x 2712)
    $slide = $pres.Slides.Item(1)
    $slide.Export('{str(preview_path)}', 'PNG', 3840, 2712)
    $pres.Close()
    $ppt.Quit()
    """
    print("Executing native PowerPoint COM export for PDF and 4K preview...")
    res = subprocess.run(["powershell", "-Command", ps_script], capture_output=True, text=True)
    if res.returncode == 0 and pdf_path.exists():
        print(f"[OK] PDF successfully exported to: {pdf_path}")
        if preview_path.exists():
            print(f"[OK] High-Resolution Preview saved to: {preview_path}")
        return True
    else:
        print(f"COM Export stdout: {res.stdout}")
        print(f"COM Export stderr: {res.stderr}")
        return False


if __name__ == "__main__":
    pptx_file = generate_final_a0_poster()
    export_pdf_and_preview_via_com(pptx_file)
    print("\nFinal A0 Academic Poster Generation Complete!")
