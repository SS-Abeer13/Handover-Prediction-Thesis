# -*- coding: utf-8 -*-
"""
Builds the academic conference/defense poster for:
'CONFORMALIZED DISCRETE-TIME HAZARD MODELING FOR MULTI-HORIZON HANDOVER FORECASTING IN CELLULAR NETWORKS'
Department of Electrical and Electronic Engineering, Islamic University of Technology (IUT)
"""

import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml import parse_xml
from pptx.oxml.ns import nsdecls

def create_poster():
    prs = pptx.Presentation('Docs/Thesis_OBE/Poster Template.pptx')
    slide = prs.slides[0]

    # Remove extra slides 2 and 3 if present
    while len(prs.slides) > 1:
        rId = prs.slides._sldIdLst[1].rId
        prs.part.drop_rel(rId)
        del prs.slides._sldIdLst[1]

    # Color definitions
    NAVY = RGBColor(0x00, 0x20, 0x60)
    GOLD = RGBColor(0xFF, 0xC0, 0x00)
    GOLD_BORDER = RGBColor(0xBA, 0x8C, 0x00)
    GREEN = RGBColor(0x00, 0x66, 0x00)
    DARK = RGBColor(0x22, 0x22, 0x22)
    WHITE = RGBColor(0xFF, 0xFF, 0xFF)
    MUTED = RGBColor(0x44, 0x44, 0x44)
    CHECK_BG = RGBColor(0xE8, 0xF5, 0xE9)
    ROW_ALT = RGBColor(0xFA, 0xFA, 0xFA)

    # -------------------------------------------------------------
    # 0. CAPTURE ESSENTIAL SHAPES BEFORE DELETION
    # -------------------------------------------------------------
    s_title = slide.shapes[0]
    s_meta = slide.shapes[23]
    s_iut_logo = slide.shapes[5]
    s_oic_logo = slide.shapes[6]

    b_abs = slide.shapes[1]
    b_bg = slide.shapes[7]
    b_obj = slide.shapes[9]
    b_meth = slide.shapes[24]
    b_exp = slide.shapes[11]

    b_res = slide.shapes[15]
    b_nov = slide.shapes[20]
    b_comm = slide.shapes[17]
    b_obe = slide.shapes[19]
    b_ref = slide.shapes[22]

    table_shape = slide.shapes[28]

    keep_list = [
        s_title, s_meta, s_iut_logo, s_oic_logo,
        b_abs, b_bg, b_obj, b_meth, b_exp,
        b_res, b_nov, b_comm, b_obe, b_ref,
        table_shape
    ]
    keep_ids = {s.shape_id for s in keep_list}

    # Delete all unused dummy shapes
    for s in list(slide.shapes):
        if s.shape_id not in keep_ids:
            sp_elem = s._element
            sp_elem.getparent().remove(sp_elem)

    # -------------------------------------------------------------
    # 1. HEADER TITLE (Shape 0)
    # -------------------------------------------------------------
    s_title.left = Inches(3.8)
    s_title.width = Inches(28.4)
    s_title.top = Inches(0.40)
    s_title.height = Inches(1.90)
    tf_title = s_title.text_frame
    tf_title.word_wrap = True
    tf_title.margin_left = Inches(0.1)
    tf_title.margin_right = Inches(0.1)
    tf_title.margin_top = Inches(0.05)
    tf_title.margin_bottom = Inches(0.05)
    tf_title.clear()
    p_title = tf_title.paragraphs[0]
    p_title.alignment = PP_ALIGN.CENTER
    run_t = p_title.add_run()
    run_t.text = "CONFORMALIZED DISCRETE-TIME HAZARD MODELING FOR MULTI-HORIZON HANDOVER FORECASTING IN CELLULAR NETWORKS"
    run_t.font.name = "Times New Roman"
    run_t.font.size = Pt(50)
    run_t.font.bold = True
    run_t.font.color.rgb = NAVY

    # -------------------------------------------------------------
    # 2. HEADER METADATA (Shape 23)
    # -------------------------------------------------------------
    s_meta.left = Inches(3.8)
    s_meta.width = Inches(28.4)
    s_meta.top = Inches(2.35)
    s_meta.height = Inches(4.5)
    tf_meta = s_meta.text_frame
    tf_meta.word_wrap = True
    tf_meta.clear()
    
    p1 = tf_meta.paragraphs[0]
    p1.alignment = PP_ALIGN.CENTER
    r1 = p1.add_run()
    r1.text = "Students: Saadman Sakib (210021110)   |   Adhnan Kalim (210021308)   |   Evan Ashfaque (210021335)"
    r1.font.name = "Times New Roman"
    r1.font.size = Pt(32)
    r1.font.bold = True
    r1.font.color.rgb = NAVY

    p2 = tf_meta.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    r2 = p2.add_run()
    r2.text = "Supervisor: Dr. Mohmmad Tawhid Kawser, Professor"
    r2.font.name = "Times New Roman"
    r2.font.size = Pt(32)
    r2.font.bold = True
    r2.font.color.rgb = NAVY

    p3 = tf_meta.add_paragraph()
    p3.alignment = PP_ALIGN.CENTER
    r3 = p3.add_run()
    r3.text = "Department of Electrical and Electronic Engineering, Islamic University of Technology (IUT)"
    r3.font.name = "Times New Roman"
    r3.font.size = Pt(34)
    r3.font.bold = True
    r3.font.color.rgb = NAVY

    # Helper function to format banner shape
    def format_banner(shape, title, fill_color, text_color):
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill_color
        shape.line.color.rgb = GOLD_BORDER
        shape.line.width = Pt(1.5)
        tf = shape.text_frame
        tf.word_wrap = False
        tf.margin_left = Inches(0.2)
        tf.margin_top = Inches(0.06)
        tf.margin_bottom = Inches(0.06)
        tf.margin_right = Inches(0.1)
        tf.clear()
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT
        r = p.add_run()
        r.text = "  " + title
        r.font.name = "Calibri"
        r.font.size = Pt(36)
        r.font.bold = True
        r.font.color.rgb = text_color

    # Helper function to create fresh, clean text box
    def create_textbox(left, top, width, height):
        tb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.05)
        tf.margin_right = Inches(0.05)
        tf.margin_top = Inches(0.05)
        tf.margin_bottom = Inches(0.05)
        return tf

    # Helper function to set table cell borders
    def set_cell_border(cell, color="CBD5E1", width_emu=12700):
        tcPr = cell._tc.get_or_add_tcPr()
        for border_name in ['lnL', 'lnR', 'lnT', 'lnB']:
            ln = parse_xml(f'<a:{border_name} {nsdecls("a")} w="{width_emu}" cmpd="s"><a:solidFill><a:srgbClr val="{color}"/></a:solidFill></a:{border_name}>')
            for child in list(tcPr):
                if child.tag.endswith(border_name):
                    tcPr.remove(child)
            tcPr.append(ln)

    # Helper function to add structured bullet points with prominent fonts
    def add_bullet(tf, lead_in, body, font_size=18.0, lead_size=19.0, space_after=3.0, bullet_char="\u2022 "):
        if len(tf.paragraphs) == 1 and len(tf.paragraphs[0].text) == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.space_after = Pt(space_after)
        p.line_spacing = 1.15

        if lead_in:
            r_lead = p.add_run()
            r_lead.text = bullet_char + lead_in + ": "
            r_lead.font.name = "Calibri"
            r_lead.font.size = Pt(lead_size)
            r_lead.font.bold = True
            r_lead.font.color.rgb = NAVY

        r_body = p.add_run()
        r_body.text = body
        r_body.font.name = "Calibri"
        r_body.font.size = Pt(font_size)
        r_body.font.bold = False
        r_body.font.color.rgb = DARK

    # -------------------------------------------------------------
    # LEFT COLUMN - BANNERS & FRESH TEXTBOXES
    # -------------------------------------------------------------
    COL1_L = 1.00
    COL1_W = 15.40

    # 1. ABSTRACT
    b_abs.left = Inches(COL1_L)
    b_abs.top = Inches(7.30)
    b_abs.width = Inches(COL1_W)
    b_abs.height = Inches(0.65)
    format_banner(b_abs, "ABSTRACT", GOLD, NAVY)

    tf_abs = create_textbox(COL1_L, 8.00, COL1_W, 3.55)
    add_bullet(tf_abs, "Problem", "LTE handovers operate reactively via Event A3, initiating target cell preparation only after link degradation has already occurred. This causes radio-link failure (RLF) during rapid channel drops and induces high ping-pong rates.", 18.0, 19.0, 3.0)
    add_bullet(tf_abs, "Logging Artifact Discovery", "Physical alignment audit reveals that standard 1 Hz diagnostic logs write post-handover cell state before the RRC command in 76% of events. Failing to lag features produces a spurious +235% AUPRC inflation (0.179 -> 0.600) prevalent in un-audited literature.", 18.0, 19.0, 3.0)
    add_bullet(tf_abs, "Hazard Formulation", "Framing handover forecasting as discrete-time survival analysis with a single gradient-boosted tree model guarantees coherent multi-horizon ordering without post-hoc heuristics, reaching AUPRC 0.179 at 1 s (2.6x over baseline) and 0.475 at 5 s.", 18.0, 19.0, 3.0)
    add_bullet(tf_abs, "Risk Guarantees", "Conformal Risk Control certifies an early-warning alarm threshold that strictly bounds per-drive miss rate <= 0.20 (realised 0.168 at 47% alarm rate). Over handovers, 36.4% of events are fundamentally bounded by the 2 s post-handover blanking policy limit.", 18.0, 19.0, 3.0)

    # 2. BACKGROUND
    b_bg.left = Inches(COL1_L)
    b_bg.top = Inches(11.60)
    b_bg.width = Inches(COL1_W)
    b_bg.height = Inches(0.65)
    format_banner(b_bg, "BACKGROUND", GOLD, NAVY)

    tf_bg = create_textbox(COL1_L, 12.30, COL1_W, 2.50)
    add_bullet(tf_bg, "3GPP LTE Mobility Mechanism", "Handover decisions are governed by RRC MeasurementReport messages. Event A3 fires when neighbor RSRP exceeds serving by an offset (Mn - Ofn > Ms + Ofs + Off) for a continuous Time-To-Trigger (TTT), creating an unavoidable delay.", 18.0, 19.0, 3.0)
    add_bullet(tf_bg, "Signalling Inefficiencies", "In dense urban topologies, 26.3% to 43.8% of handovers return to the source cell within 15 seconds, expending unnecessary signaling load, radio resource control overhead, and UE battery consumption.", 18.0, 19.0, 3.0)
    add_bullet(tf_bg, "Literature Evaluation Pitfalls", "Audit of 22 published models indicates widespread data leakage: random row-level splitting across continuous drive tests inflates AUPRC by up to 48% and misranks models relative to cluster-safe cross-campaign splits.", 18.0, 19.0, 3.0)

    # 3. OBJECTIVES
    b_obj.left = Inches(COL1_L)
    b_obj.top = Inches(14.90)
    b_obj.width = Inches(COL1_W)
    b_obj.height = Inches(0.65)
    format_banner(b_obj, "OBJECTIVES", GOLD, NAVY)

    tf_obj = create_textbox(COL1_L, 15.60, COL1_W, 3.60)
    add_bullet(tf_obj, "O1 - Alignment Audit", "Identify and correct physical logging/export latency between handset traces and decoded RRC event clock.", 18.0, 19.0, 2.5)
    add_bullet(tf_obj, "O2 - Leakage-Free Benchmarking", "Establish a rigorous Leave-One-Campaign-Out (LOCO) protocol that prevents temporal and spatial information leakage.", 18.0, 19.0, 2.5)
    add_bullet(tf_obj, "O3 - Monotone Multi-Horizon Forecasting", "Develop a discrete-time survival/hazard framework guaranteeing mathematically ordered cumulative incidence (0.5 s to 5 s).", 18.0, 19.0, 2.5)
    add_bullet(tf_obj, "O4 - Distribution-Free Risk Control", "Formulate Conformal Risk Control (CRC) on clustered drive units to certify operational alarm thresholds with statistical bounds.", 18.0, 19.0, 2.5)
    add_bullet(tf_obj, "O5 - Operational Characterization", "Decode live RRC signaling timelines to quantify Event A3 conversion efficiency and ping-pong sensitivity under live deployments.", 18.0, 19.0, 2.5)

    # 4. PROPOSED METHODOLOGY
    b_meth.left = Inches(COL1_L)
    b_meth.top = Inches(19.35)
    b_meth.width = Inches(COL1_W)
    b_meth.height = Inches(0.65)
    format_banner(b_meth, "PROPOSED METHODOLOGY", GOLD, NAVY)

    tf_meth = create_textbox(COL1_L, 20.05, COL1_W, 2.55)
    add_bullet(tf_meth, "Signalling Decoding", "Replay RRC connection reconfiguration timelines under TS 36.331; ground truth extracted from mobilityControlInfo with 100% confirmed completion.", 18.0, 19.0, 2.5)
    add_bullet(tf_meth, "Causal Feature Engineering", "112 strictly causal features: 89 Radio (serving RF + projected neighbor RSRP via zero-order hold), 17 Mobility (GPS speed, acceleration, bearing), 6 History (dwell time, recent handover count). All export features lagged 1 row.", 18.0, 19.0, 2.5)
    add_bullet(tf_meth, "Hazard Formulation", "Single LightGBM model estimates interval hazard lambda_k(x_t). Cumulative incidence derived via product-limit identity F_k(x_t) = 1 - prod_{j=1}^k (1 - lambda_j(x_t)), guaranteeing monotonic ordering without heuristics.", 18.0, 19.0, 2.5)
    add_bullet(tf_meth, "Conformal Risk Control", "Certify threshold lambda* on calibration sessions such that expected per-unit loss satisfies E[L] <= alpha with distribution-free validity.", 18.0, 19.0, 2.5)

    # Add Framework Diagram (Aspect ratio 9.116 -> width 15.40, height 1.69)
    slide.shapes.add_picture('latex/figures/m14_framework.png', Inches(COL1_L), Inches(22.75), width=Inches(COL1_W), height=Inches(1.69))

    # 5. EXPERIMENTAL DESIGN
    b_exp.left = Inches(COL1_L)
    b_exp.top = Inches(24.65)
    b_exp.width = Inches(COL1_W)
    b_exp.height = Inches(0.65)
    format_banner(b_exp, "EXPERIMENTAL DESIGN", GOLD, NAVY)

    tf_exp = create_textbox(COL1_L, 25.35, COL1_W, 2.40)
    add_bullet(tf_exp, "Measurement Testbed", "Commercial live LTE network across Dhaka and Gazipur, Bangladesh, captured using an instrumented vehicle with XCAL diagnostic drive-test hardware.", 18.0, 19.0, 3.0)
    add_bullet(tf_exp, "Four Continuous Campaigns", "Campaign 1 (Urban Arterial, 45 min, 39.1 km/h), Campaign 2 (Urban Loop, 24 min, 25.0 km/h), Campaign 3 (Dense Urban, 60 min, 21.4 km/h), Campaign 4 (Highway, 42 min, 50.9 km/h).", 18.0, 19.0, 3.0)
    add_bullet(tf_exp, "Corpus Scale", "96 km total distance, 10,260 1-Hz measurement rows (8,586 usable modelling rows after 2-second blanking & quality control), 957 confirmed handover commands, and 341 RRC re-establishments.", 18.0, 19.0, 3.0)

    # Add Route Map (Larger, aspect 0.7952 -> width 14.60, height 18.36, centered horizontally, ending at 46.26 in)
    map_w = 14.60
    map_h = 18.36
    map_l = COL1_L + (COL1_W - map_w) / 2.0
    slide.shapes.add_picture('latex/figures/fig03_map_routes.png', Inches(map_l), Inches(27.90), width=Inches(map_w), height=Inches(map_h))

    # -------------------------------------------------------------
    # RIGHT COLUMN - BANNERS, FIGURES, & FRESH TEXTBOXES
    # -------------------------------------------------------------
    COL2_L = 19.60
    COL2_W = 15.40

    # 6. KEY OUTCOMES / RESULTS
    b_res.left = Inches(COL2_L)
    b_res.top = Inches(7.30)
    b_res.width = Inches(COL2_W)
    b_res.height = Inches(0.65)
    format_banner(b_res, "KEY OUTCOMES/RESULTS", GREEN, WHITE)

    tf_res = create_textbox(COL2_L, 8.00, COL2_W, 3.20)
    add_bullet(tf_res, "Predictive Superiority", "Discrete-time LightGBM hazard achieves AUPRC 0.179 at 1 s (2.6x over 6.8% base rate), 0.252 at 2 s, and 0.475 at 5 s, outperforming deployed Event A3 baseline (0.116 at 1 s) and deep sequence models (GRU: 0.158, Transformer: 0.155).", 17.5, 18.5, 2.0)
    add_bullet(tf_res, "100% Horizon Monotonicity", "Hazard formulation yields exactly 0.0% horizon ordering violations, whereas independent binary classifiers produce 40.2% contradictory violations across horizons.", 17.5, 18.5, 2.0)
    add_bullet(tf_res, "Conformal Risk Verification", "At target alpha = 0.20, certified warning threshold achieves realised mean per-unit loss of 0.168 (47% alarm rate) under exchangeable pooling and holds in 83% of cross-campaign holdout rotations.", 17.5, 18.5, 2.0)
    add_bullet(tf_res, "Network Operating Realities", "74.8% of A3 handovers fire under positive offset (+1 dB dominant). Between 63% and 73% of triggered A3 episodes are declined by the eNodeB without a handover command.", 17.5, 18.5, 2.0)

    # Figure 1: Multi-Horizon AUPRC Benchmark (aspect 1.779 -> width 9.60, height 5.40, centered)
    fig1_w = 9.60
    fig1_h = 5.40
    fig1_l = COL2_L + (COL2_W - fig1_w) / 2.0
    slide.shapes.add_picture('latex/figures/fig_c3_main.png', Inches(fig1_l), Inches(11.40), width=Inches(fig1_w), height=Inches(fig1_h))

    # Figure 2: Conformal Risk Control Calibration (aspect 2.191 -> width 9.60, height 4.38, centered)
    fig2_w = 9.60
    fig2_h = 4.38
    fig2_l = COL2_L + (COL2_W - fig2_w) / 2.0
    slide.shapes.add_picture('latex/figures/fig_c10_crc.png', Inches(fig2_l), Inches(17.05), width=Inches(fig2_w), height=Inches(fig2_h))

    # 7. NOVELTY / SIGNIFICANT CONTRIBUTIONS
    b_nov.left = Inches(COL2_L)
    b_nov.top = Inches(21.80)
    b_nov.width = Inches(COL2_W)
    b_nov.height = Inches(0.65)
    format_banner(b_nov, "NOVELTY/SIGNIFICANT CONTRIBUTIONS", GREEN, WHITE)

    tf_nov = create_textbox(COL2_L, 22.50, COL2_W, 3.40)
    add_bullet(tf_nov, "1. Diagnostic Alignment Audit", "First systematic demonstration that commercial diagnostic 1 Hz exports suffer a write-before-read logging artifact, removing spurious results and establishing a reproducibility standard.", 17.0, 18.0, 2.0)
    add_bullet(tf_nov, "2. Coherent Hazard Framework", "First unified discrete-time survival formulation applied to multi-horizon mobility prediction, eliminating horizon incoherence by construction.", 17.0, 18.0, 2.0)
    add_bullet(tf_nov, "3. Clustered Conformal Risk Guarantees", "First deployment of Conformal Risk Control on drive-test sessions, testing exchangeability across routes and revealing the 36.4% evaluation policy limit under post-handover blanking.", 17.0, 18.0, 2.0)
    add_bullet(tf_nov, "4. 22-Model Meta-Audit", "Screened 108 papers and audited 22 models, demonstrating that random-row evaluation inflates scores by up to 48% and corrupts comparative leaderboards.", 17.0, 18.0, 2.0)

    # 8. COMMERCIAL VIABILITY
    b_comm.left = Inches(COL2_L)
    b_comm.top = Inches(26.15)
    b_comm.width = Inches(COL2_W)
    b_comm.height = Inches(0.65)
    format_banner(b_comm, "COMMERCIAL VIABILITY", GREEN, WHITE)

    tf_comm = create_textbox(COL2_L, 26.85, COL2_W, 2.45)
    add_bullet(tf_comm, "Zero Hardware Changes", "Purely software-based inference executable on handset baseband chipsets or integrated as an auxiliary background telemetry daemon.", 17.0, 18.0, 2.0)
    add_bullet(tf_comm, "Open-RAN (O-RAN) xApp Compatibility", "Easily packaged as a near-Real-Time RIC xApp or non-RT rApp, receiving standard E2 measurement reports to guide proactive Traffic Steering (TS) and QoS optimization.", 17.0, 18.0, 2.0)
    add_bullet(tf_comm, "Signalling Overhead & Energy Reduction", "Early target cell preparation mitigates user-plane interruption and eliminates up to 26.3% wasteful ping-pong executions, saving base-station capacity and UE power.", 17.0, 18.0, 2.0)

    # 9. OBE ATTRIBUTES
    b_obe.left = Inches(COL2_L)
    b_obe.top = Inches(29.50)
    b_obe.width = Inches(COL2_W)
    b_obe.height = Inches(0.65)
    format_banner(b_obe, "OBE ATTRIBUTES", GREEN, WHITE)

    # Table (Shape 28) - Significantly enlarged boxes/cells with visible borders
    table_shape.left = Inches(COL2_L)
    table_shape.top = Inches(30.25)
    tbl = table_shape.table

    # Expanded column widths (sum = 6.86 in)
    col_widths = [Inches(1.20), Inches(0.68), Inches(0.98), Inches(0.68), Inches(0.98), Inches(0.68), Inches(0.98), Inches(0.68)]
    for ci, cw in enumerate(col_widths):
        tbl.columns[ci].width = cw
    table_shape.width = sum(col_widths)

    # Expanded row heights (Header = 0.52 in, Data = 0.51 in -> total 6.64 in)
    for idx, r in enumerate(tbl.rows):
        r.height = Inches(0.52) if idx == 0 else Inches(0.51)
    table_shape.height = Inches(6.64)

    obe_data = [
        ['POs', 'Tick', 'Ks', 'Tick', 'Ps', 'Tick', 'As', 'Tick'],
        ['PO1', '\u2713', 'K3', '\u2713', 'P1', '\u2713', 'A1', '\u2713'],
        ['PO2', '\u2713', 'K4', '\u2713', 'P2', '\u2713', 'A2', '\u2713'],
        ['PO3', '\u2713', 'K5', '\u2713', 'P3', '\u2713', 'A3', '\u2713'],
        ['PO4', '\u2713', 'K6', '\u2713', 'P4', '\u2713', 'A4', '\u2713'],
        ['PO5', '\u2713', 'K7', '\u2713', 'P5', '\u2713', 'A5', '\u2713'],
        ['PO6', '\u2713', 'K8', '\u2713', 'P6', '\u2713', '', ''],
        ['PO7', '\u2713', '', '', 'P7', '\u2713', '', ''],
        ['PO8', '\u2713', '', '', '', '', '', ''],
        ['PO9', '', '', '', '', '', '', ''],
        ['PO10', '\u2713', '', '', '', '', '', ''],
        ['PO11', '\u2713', '', '', '', '', '', ''],
        ['PO12', '', '', '', '', '', '', '']
    ]

    for r_idx, row in enumerate(tbl.rows):
        for c_idx, cell in enumerate(row.cells):
            cell.margin_left = Inches(0.02)
            cell.margin_right = Inches(0.02)
            cell.margin_top = Inches(0.01)
            cell.margin_bottom = Inches(0.01)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.text = ""
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            r = p.add_run()
            r.text = obe_data[r_idx][c_idx]
            r.font.name = "Calibri"
            r.font.size = Pt(16.5) if r_idx > 0 else Pt(17.5)
            r.font.bold = True if (r_idx == 0 or c_idx % 2 == 0) else False

            if r_idx == 0:
                cell.fill.solid()
                cell.fill.fore_color.rgb = GREEN
                r.font.color.rgb = WHITE
            elif c_idx % 2 == 1 and r.text == '\u2713':
                cell.fill.solid()
                cell.fill.fore_color.rgb = CHECK_BG
                r.font.color.rgb = GREEN
                r.font.size = Pt(21.0)
                r.font.bold = True
            else:
                cell.fill.solid()
                cell.fill.fore_color.rgb = ROW_ALT if r_idx % 2 == 0 else WHITE
                r.font.color.rgb = NAVY if c_idx % 2 == 0 else DARK

            set_cell_border(cell, "CBD5E1", 12700)

    # OBE Description Card & Text Box (Enlarged and framed)
    tbl_total_w = sum(w.inches for w in col_widths)
    obedesc_l = COL2_L + tbl_total_w + 0.25
    obedesc_w = COL2_W - tbl_total_w - 0.25
    obedesc_h = 6.64

    card_obedesc = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(obedesc_l), Inches(30.25), Inches(obedesc_w), Inches(obedesc_h))
    card_obedesc.fill.solid()
    card_obedesc.fill.fore_color.rgb = RGBColor(250, 252, 253)
    card_obedesc.line.color.rgb = RGBColor(210, 225, 218)
    card_obedesc.line.width = Pt(1.2)

    tb_obedesc = slide.shapes.add_textbox(Inches(obedesc_l), Inches(30.25), Inches(obedesc_w), Inches(obedesc_h))
    tf_obedesc = tb_obedesc.text_frame
    tf_obedesc.word_wrap = True
    tf_obedesc.margin_left = Inches(0.18)
    tf_obedesc.margin_right = Inches(0.18)
    tf_obedesc.margin_top = Inches(0.14)
    tf_obedesc.margin_bottom = Inches(0.14)

    add_bullet(tf_obedesc, "PO3 / PO4 / PO5", "Design of experiments on live operator LTE network; rigorous multi-campaign data analysis; modern machine learning and diagnostic toolchain.", 16.5, 17.5, 3.5)
    add_bullet(tf_obedesc, "PO6 / PO7 / PO8", "Operator anonymity preserved; societal impact through signaling energy waste characterization; professional ethics in reporting negative results.", 16.5, 17.5, 3.5)
    add_bullet(tf_obedesc, "PO10 / PO11", "Exhaustive documentation across 7 chapters; engineering management and resource allocation over two academic terms.", 16.5, 17.5, 3.5)
    add_bullet(tf_obedesc, "K3 / K4 / K5 / K6", "Mathematical survival analysis fundamentals; specialized RRC decoding under 3GPP TS 36.331; causal feature design; live-network instrumentation.", 16.5, 17.5, 3.5)
    add_bullet(tf_obedesc, "K7 / K8", "Societal role of mobile broadband; critical synthesis of 108 papers and 22 audited models.", 16.5, 17.5, 3.5)
    add_bullet(tf_obedesc, "Complex Problems (P1-P7, A1-A5)", "Resolution of conflicting alarm-vs-miss trade-offs; non-standard evaluation procedures; integration across radio propagation, survival theory, and cellular control plane.", 16.5, 17.5, 1.0)

    # 10. REFERENCES
    b_ref.left = Inches(COL2_L)
    b_ref.top = Inches(37.10)
    b_ref.width = Inches(COL2_W)
    b_ref.height = Inches(0.65)
    format_banner(b_ref, "REFERENCES", GREEN, WHITE)

    tf_ref = create_textbox(COL2_L, 37.80, COL2_W, 5.20)
    
    refs = [
        ("[1]", "G. Ke, Q. Meng, T. Finley, T. Wang, W. Chen, W. Ma, Q. Ye, and T.-Y. Liu, \"LightGBM: A highly efficient gradient boosting decision tree,\" in Advances in Neural Information Processing Systems (NeurIPS), vol. 30, pp. 3146–3154, 2017."),
        ("[2]", "A. N. Angelopoulos, S. Bates, C. Cand\u00e8s, M. I. Jordan, and L. Lei, \"Learn then test: Calibrating predictive algorithms to satisfy risk bounds,\" Biometrika, 2024."),
        ("[3]", "3GPP, \"Evolved Universal Terrestrial Radio Access (E-UTRA); Radio Resource Control (RRC); Protocol specification,\" 3rd Generation Partnership Project (3GPP), Technical Specification (TS) 36.331, Rel. 16, 2020."),
        ("[4]", "A. Ghoshal, P. V. Mekala, B. B. B. Dantu, and J. Erman, \"Understanding LTE handover dynamics in the wild,\" in Proc. ACM Internet Measurement Conference (IMC), pp. 696–709, 2020."),
        ("[5]", "S. V. R. Mandapati, \"Meta-continual mobility forecasting for proactive handover prediction,\" arXiv preprint arXiv:2512.11841, 2025."),
        ("[6]", "N. Amirova, T. Taleb, and H. Flinck, \"Data-driven machine learning analysis of handover behavior in operational mobile networks,\" Future Internet, vol. 18, no. 6, p. 290, 2026."),
        ("[7]", "S. Sakib, A. Kalim, E. Ashfaque, and M. T. Kawser, \"Conformalized Discrete-Time Hazard Modeling for Multi-Horizon Handover Forecasting in Cellular Networks,\" B.Sc. Thesis, Dept. of Electrical and Electronic Engineering, Islamic University of Technology (IUT), 2026.")
    ]

    for num, cit in refs:
        if len(tf_ref.paragraphs) == 1 and len(tf_ref.paragraphs[0].text) == 0:
            p = tf_ref.paragraphs[0]
        else:
            p = tf_ref.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.space_after = Pt(6.0)
        p.line_spacing = 1.15

        r_num = p.add_run()
        r_num.text = num + " "
        r_num.font.name = "Calibri"
        r_num.font.size = Pt(18.5)
        r_num.font.bold = True
        r_num.font.color.rgb = GREEN
        
        r_cit = p.add_run()
        r_cit.text = cit
        r_cit.font.name = "Calibri"
        r_cit.font.size = Pt(17.5)
        r_cit.font.color.rgb = DARK

    # 11. RESEARCH ARTIFACTS & REPRODUCIBILITY CARD (Spans 43.15 to 46.55 in, eliminating bottom void)
    card_repro = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(COL2_L), Inches(43.15), Inches(COL2_W), Inches(3.40))
    card_repro.fill.solid()
    card_repro.fill.fore_color.rgb = RGBColor(242, 248, 244)
    card_repro.line.color.rgb = GREEN
    card_repro.line.width = Pt(1.5)

    tb_repro = slide.shapes.add_textbox(Inches(COL2_L), Inches(43.15), Inches(COL2_W), Inches(3.40))
    tf_repro = tb_repro.text_frame
    tf_repro.word_wrap = True
    tf_repro.margin_left = Inches(0.20)
    tf_repro.margin_right = Inches(0.20)
    tf_repro.margin_top = Inches(0.15)
    tf_repro.margin_bottom = Inches(0.15)

    p_rh = tf_repro.paragraphs[0]
    p_rh.alignment = PP_ALIGN.LEFT
    p_rh.space_after = Pt(4.0)
    r_rh = p_rh.add_run()
    r_rh.text = "\u2022 OPEN-SOURCE BENCHMARK & REPRODUCIBILITY ARTIFACTS"
    r_rh.font.name = "Calibri"
    r_rh.font.size = Pt(19.0)
    r_rh.font.bold = True
    r_rh.font.color.rgb = GREEN

    add_bullet(tf_repro, "Causal Signalling & Telemetry Pipeline", "Complete Python framework, millisecond-precision 3GPP TS 36.331 RRC protocol decoders, 112 strictly causal radio and mobility feature builders, and automated verification testbenches.", 16.5, 17.5, 4.0)
    add_bullet(tf_repro, "Conformal Calibration & Model Checkpoints", "Production LightGBM hazard models, Leave-One-Campaign-Out cross-validation harnesses, and distribution-free CRC calibration algorithms open-sourced under Apache-2.0.", 16.5, 17.5, 0.0)

    prs.save('Docs/Thesis_OBE/Thesis_Poster.pptx')
    print("SUCCESS: Thesis_Poster.pptx created successfully!")

if __name__ == '__main__':
    create_poster()
