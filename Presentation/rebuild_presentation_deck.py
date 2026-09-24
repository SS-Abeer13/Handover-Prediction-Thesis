import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

PPTX_PATH = r"D:\Handover Thesis\Presentation\Handover-Thesis-Defence.pptx"
BG_IMAGE_PATH = r"D:\Handover Thesis\Presentation\template_bg.png"
NARRATIVE_PNG = r"D:\Handover Thesis\Presentation\figures\m08_narrative.png"
FIG27_PNG = r"D:\Handover Thesis\Presentation\figures\fig27_feature_ablation.png"

prs = Presentation(PPTX_PATH)
blank_layout = prs.slide_layouts[6] # completely blank layout

# Color Palette matching IUT template
MAROON = RGBColor(0x89, 0x13, 0x13)
NAVY = RGBColor(0x1F, 0x4E, 0x79)
INK = RGBColor(0x26, 0x26, 0x26)
MUTED = RGBColor(0x77, 0x77, 0x77)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
HIGHLIGHT_BG = RGBColor(0xFD, 0xED, 0xEC)
CARD_BG = RGBColor(0xF8, 0xF9, 0xFA)
BORDER_GRAY = RGBColor(0xCC, 0xCC, 0xCC)
FONT = "Arial"
L = 0.92

# ==============================================================================
# Helper to create Slide 2: Abstract / Executive Summary
# ==============================================================================
def create_abstract_slide():
    slide = prs.slides.add_slide(blank_layout)
    # Background picture
    slide.shapes.add_picture(BG_IMAGE_PATH, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    
    # Breadcrumb
    tb_bc = slide.shapes.add_textbox(Inches(L), Inches(0.85), Inches(7.0), Inches(0.32))
    tf_bc = tb_bc.text_frame
    tf_bc.word_wrap = True
    p_bc = tf_bc.paragraphs[0]
    p_bc.text = "ABSTRACT & RESEARCH SUMMARY"
    p_bc.font.size = Pt(11)
    p_bc.font.bold = True
    p_bc.font.name = FONT
    p_bc.font.color.rgb = MUTED
    
    # Action Title
    tb_title = slide.shapes.add_textbox(Inches(L), Inches(1.18), Inches(9.5), Inches(0.95))
    tf_title = tb_title.text_frame
    tf_title.word_wrap = True
    p_title = tf_title.paragraphs[0]
    p_title.text = "Predicting LTE handovers 1–5 s ahead with distribution-free risk bounds and zero ping-pong"
    p_title.font.size = Pt(20)
    p_title.font.bold = True
    p_title.font.name = FONT
    p_title.font.color.rgb = MAROON
    
    # Top Visual: Flowchart banner
    slide.shapes.add_picture(NARRATIVE_PNG, Inches(L), Inches(2.20), Inches(11.5), Inches(2.0))
    
    # Bottom Half: 4 Key Contribution Summary Cards
    cards_data = [
        ("DATASET & HYGIENE", [
            ("Scale: ", "57 drives across 2 corridors, 10,260 s & 938 confirmed HOs."),
            ("Timeline Fix: ", "Resolved stateful ASN.1 RRC defect affecting 99.4% of frames.")
        ]),
        ("HAZARD FORMULATION", [
            ("Survival Model: ", "Discrete-time S(t) = Π(1 - h(k)) guarantees monotonicity."),
            ("Zero Inversions: ", "0% violations vs 14.8% in unconstrained multi-head baselines.")
        ]),
        ("BENCHMARK ACCURACY", [
            ("Discrimination: ", "AUROC 0.933 at 1 s, AUPRC 0.784 (11.7× lift over floor)."),
            ("Calibration: ", "ECE 0.037. Dominates deep baselines under equal 50-trial tuning.")
        ]),
        ("RISK & OPERATION", [
            ("Conformal Bound: ", "CRC guarantees E[L] ≤ α without parametric assumptions."),
            ("Published Gain: ", "Beats departmental RL baseline (AUROC 0.921 vs 0.489).")
        ])
    ]
    
    card_w = Inches(2.72)
    card_h = Inches(2.05)
    gap = Inches(0.20)
    card_top = Inches(4.35)
    
    for c_idx, (header, bullets) in enumerate(cards_data):
        c_left = Inches(L) + c_idx * (card_w + gap)
        
        # Add background shape
        box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, c_left, card_top, card_w, card_h)
        box.fill.solid()
        box.fill.fore_color.rgb = CARD_BG
        box.line.color.rgb = BORDER_GRAY
        box.line.width = Pt(1)
        
        # Text
        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_top = Inches(0.08)
        tf.margin_bottom = Inches(0.08)
        tf.margin_left = Inches(0.10)
        tf.margin_right = Inches(0.10)
        
        p0 = tf.paragraphs[0]
        p0.text = header
        p0.font.name = FONT
        p0.font.size = Pt(10.5)
        p0.font.bold = True
        p0.font.color.rgb = MAROON
        p0.space_after = Pt(4)
        
        for lead, body in bullets:
            p = tf.add_paragraph()
            p.space_after = Pt(4)
            r1 = p.add_run()
            r1.text = lead
            r1.font.bold = True
            r1.font.size = Pt(9.0)
            r1.font.name = FONT
            r1.font.color.rgb = INK
            
            r2 = p.add_run()
            r2.text = body
            r2.font.size = Pt(9.0)
            r2.font.name = FONT
            r2.font.color.rgb = INK
            
    # Footer Citation
    tb_cite = slide.shapes.add_textbox(Inches(L), Inches(6.58), Inches(11.5), Inches(0.35))
    tf_cite = tb_cite.text_frame
    tf_cite.word_wrap = True
    p_cite = tf_cite.paragraphs[0]
    p_cite.text = "Comprehensive research design synthesis: measurement-grade ground truth, survival hazard formulation, and conformal risk guarantees."
    p_cite.font.size = Pt(10)
    p_cite.font.name = FONT
    p_cite.font.color.rgb = MUTED
    
    print("Created Slide 2: Abstract / Executive Summary")

# ==============================================================================
# Helper to create Slide 12: Feature Representation & Ablation
# ==============================================================================
def create_feature_slide():
    slide = prs.slides.add_slide(blank_layout)
    # Background picture
    slide.shapes.add_picture(BG_IMAGE_PATH, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    
    # Breadcrumb
    tb_bc = slide.shapes.add_textbox(Inches(L), Inches(0.85), Inches(7.0), Inches(0.32))
    tf_bc = tb_bc.text_frame
    tf_bc.word_wrap = True
    p_bc = tf_bc.paragraphs[0]
    p_bc.text = "FEATURE REPRESENTATION & ABLATION"
    p_bc.font.size = Pt(11)
    p_bc.font.bold = True
    p_bc.font.name = FONT
    p_bc.font.color.rgb = MUTED
    
    # Action Title
    tb_title = slide.shapes.add_textbox(Inches(L), Inches(1.18), Inches(9.5), Inches(0.95))
    tf_title = tb_title.text_frame
    tf_title.word_wrap = True
    p_title = tf_title.paragraphs[0]
    p_title.text = "Physical RF dynamics and dwell time carry predictive power; raw signalling alone is insufficient"
    p_title.font.size = Pt(20)
    p_title.font.bold = True
    p_title.font.name = FONT
    p_title.font.color.rgb = MAROON
    
    # Left Visual: fig27_feature_ablation.png
    slide.shapes.add_picture(FIG27_PNG, Inches(L), Inches(2.25), Inches(7.40), Inches(4.15))
    
    # Right Side Card: Interpretive Analysis
    card_left = Inches(8.55)
    card_top = Inches(2.25)
    card_w = Inches(3.85)
    card_h = Inches(4.15)
    
    box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, card_left, card_top, card_w, card_h)
    box.fill.solid()
    box.fill.fore_color.rgb = CARD_BG
    box.line.color.rgb = BORDER_GRAY
    box.line.width = Pt(1)
    
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_top = Inches(0.12)
    tf.margin_bottom = Inches(0.12)
    tf.margin_left = Inches(0.15)
    tf.margin_right = Inches(0.15)
    
    p0 = tf.paragraphs[0]
    p0.text = "CAUSAL FEATURE FAMILIES & POWER"
    p0.font.name = FONT
    p0.font.size = Pt(11)
    p0.font.bold = True
    p0.font.color.rgb = MAROON
    p0.space_after = Pt(8)
    
    bullets = [
        ("Continuous Channel Dynamics: ", "Serving dwell time (0.874 AUROC) and SINR (0.830) dominate instantaneous signal. RF+Mobility+History alone reaches 0.940 AUROC at 1 s."),
        ("Catalytic Role of Signalling: ", "Pure ASN.1 signalling features reach 0.826 AUROC (5.05× lift). When fused with RF dynamics, they sharpen boundary discrimination to 0.942 AUROC."),
        ("Strict Causal Ingestion: ", "All features computed via causal backward rolling windows (3 s, 5 s, 10 s). Zero future lookahead or whole-drive aggregates ever contaminate test folds.")
    ]
    
    for lead, body in bullets:
        p = tf.add_paragraph()
        p.space_after = Pt(8)
        r1 = p.add_run()
        r1.text = lead
        r1.font.bold = True
        r1.font.size = Pt(9.5)
        r1.font.name = FONT
        r1.font.color.rgb = MAROON
        
        r2 = p.add_run()
        r2.text = body
        r2.font.size = Pt(9.5)
        r2.font.name = FONT
        r2.font.color.rgb = INK
        
    # Footer Citation
    tb_cite = slide.shapes.add_textbox(Inches(L), Inches(6.58), Inches(11.5), Inches(0.35))
    tf_cite = tb_cite.text_frame
    tf_cite.word_wrap = True
    p_cite = tf_cite.paragraphs[0]
    p_cite.text = "Stage 16 Feature Representation & Signalling Ablation across 57 grouped holdout drives (Dhaka LTE Corpus)."
    p_cite.font.size = Pt(10)
    p_cite.font.name = FONT
    p_cite.font.color.rgb = MUTED
    
    print("Created Slide 12: Feature Representation & Ablation")

# Create the two new slides (they will be at the end of prs.slides initially)
create_abstract_slide()
create_feature_slide()

abstract_idx = len(prs.slides) - 2
feature_idx = len(prs.slides) - 1

# ==============================================================================
# Define the Target Academic Research Design Sequence
# ==============================================================================
# Old slide indices (0-indexed):
# 0: Title (Old 1)
# 1: Motivation (Old 2 - A3 event)
# 2: Research Question (Old 3)
# 3: Roadmap (Old 4)
# 4: Literature 1 (Old 5 - Two literatures)
# 5: Literature 2 (Old 6 - 22 papers)
# 6: Literature 3 (Old 7 - Four literatures)
# 7: Data 1 (Old 8 - ASN.1 timeline)
# 8: Data 2 (Old 9 - 57 drives)
# 9: Data 3 (Old 10 - Handovers cluster)
# 10: Data 4 (Old 11 - Rare-event prevalence)
# 11: Theory (Old 12 - Hazard concept)
# 12: Method 1 (Old 13 - Grouped drive holdout)
# 13: Method 2 (Old 14 - 18-stage pipeline)
# 14: Results 1 (Old 15 - Model comparison)
# 15: Results 2 (Old 16 - Hazard results)
# 16: Results 3 (Old 17 - Tuning budget)
# 17: Results 4 (Old 18 - Deep baselines)
# 18: Results 5 (Old 19 - Leakage audit)
# 19: Guarantee 1 (Old 20 - CRC formulation)
# 20: Guarantee 2 (Old 21 - Risk control frontier)
# 21: Generalisation 1 (Old 22 - Highway transfer)
# 22: Generalisation 2 (Old 23 - Astana transfer)
# 23: Generalisation 3 (Old 24 - Domain adaptation)
# 24: Mechanism 1 (Old 25 - Feature power inversion)
# 25: Mechanism 2 (Old 26 - A3 conversion collapse)
# 26: Mechanism 3 (Old 27 - Hawkes process)
# 27: Mechanism 4 (Old 28 - Ping-pong definitions)
# 28: Mechanism 5 (Old 29 - Ping-pong mechanism)
# 29: Benefit (Old 30 - Warning benefit curve)
# 30: Positioning (Old 31 - Shafi departmental baseline)
# 31: Literature Benchmark (Old 32 - 22-study matrix)
# 32: Synthesis (Old 33 - 6 negative results)
# 33: Limitations (Old 34 - What this work cannot claim)
# 34: Future Directions (Old 35 - Four directions / Causal)
# 35: Conclusions (Old 36)
# 36: References (Old 37)
# 37: Thank you (Old 38)
# 38-44: Appendix A-G (Old 39-45)

target_order = [
    # 1. Title
    0,
    # 2. Abstract / Executive Summary (NEW)
    abstract_idx,
    # 3. Theory: A3 physics & reactive lag (Old 2)
    1,
    # 4. Theory: Discrete-time survival hazard formulation (Old 12)
    11,
    # 5. Problem Formulation: Multi-horizon contract & rare-event prevalence floors (Old 11)
    10,
    # 6. Problem Formulation: Distribution-free risk bounds via CRC (Old 20)
    19,
    # 7. Related Work: The two literatures gap (Old 5)
    4,
    # 8. Literature Audit: 22-paper systematic protocol audit (Old 6)
    5,
    # 9. Dataset & Ground Truth: 57 drives across 2 corridors (Old 9)
    8,
    # 10. Dataset & Ground Truth: Spatial link degradation & ping-pong clustering (Old 10)
    9,
    # 11. Data Hygiene: Resolving ASN.1 dynamic timeline defect (Old 8)
    7,
    # 12. Feature Representation & Ablation: Physical RF dynamics vs signalling (NEW)
    feature_idx,
    # 13. Methodology & Protocol: Grouped drive holdout cross-validation (Old 13)
    12,
    # 14. Methodology & Pipeline: 18-stage end-to-end pipeline (Old 14)
    13,
    # 15. Methodological Decisions: Equal 50-trial Bayesian tuning budget (Old 17)
    16,
    # 16. Empirical Results: Primary benchmark at 1s & 5s (Old 15)
    14,
    # 17. Empirical Results: Survival coherence & ECE calibration (Old 16)
    15,
    # 18. Empirical Results: Deep sequence baselines ablation (Old 18)
    17,
    # 19. Empirical Results: Architecture-dependent temporal leakage audit (Old 19)
    18,
    # 20. Empirical Results: Conformal Risk Control cost frontier (Old 21)
    20,
    # 21. Generalisation Outcomes: High-speed highway LOCO transfer (Old 22)
    21,
    # 22. Generalisation Outcomes: Astana cross-country public dataset transfer (Old 23)
    22,
    # 23. Generalisation Outcomes: Domain adaptation negative result (Old 24)
    23,
    # 24. Physical Mechanisms: Feature power inversion (Old 25)
    24,
    # 25. Physical Mechanisms: 61.3% A3 report conversion decline (Old 26)
    25,
    # 26. Physical Mechanisms: Hawkes self-exciting point process (Old 27)
    26,
    # 27. Physical Mechanisms: Ping-pong definition sensitivity (Old 28)
    27,
    # 28. Physical Mechanisms: Carrier aggregation & 320ms TTT root cause (Old 29)
    28,
    # 29. Operational Value: Early warning benefit frontier (Old 30)
    29,
    # 30. Benchmarking: Shafi et al. RL head-to-head re-implementation (Old 31)
    30,
    # 31. Literature Benchmark: 22-study comparative matrix (Old 32)
    31,
    # 32. Synthesis & Ablations: Controlled ablation of 6 negative results (Old 33)
    32,
    # 33. Limitations: Three bounded engineering limitations (Old 34)
    33,
    # 34. Future Directions: Causal fuzzy regression discontinuity roadmap (Old 35)
    34,
    # 35. Conclusions: Four primary takeaways (Old 36)
    35,
    # 36. References (Old 37)
    36,
    # 37. Thank You & Q&A (Old 38)
    37,
    # 38. Backup: Roadmap (Old 4)
    3,
    # 39. Backup: Research Question (Old 3)
    2,
    # 40. Backup: Literature taxonomy (Old 7)
    6,
    # 41-47. Appendix A-G (Old 39-45)
    38, 39, 40, 41, 42, 43, 44
]

print(f"Target order length: {len(target_order)}, Total slides before reorder: {len(prs.slides)}")

# Reorder sldIdLst
sldIdLst = prs.slides._sldIdLst
id_elements = [sldIdLst[i] for i in target_order]
sldIdLst.clear()
for elem in id_elements:
    sldIdLst.append(elem)

# Now update breadcrumbs on all slides to reflect formal academic sections
breadcrumb_map = {
    1: None, # Title
    2: "ABSTRACT & RESEARCH SUMMARY",
    3: "THEORETICAL FOUNDATION",
    4: "THEORETICAL FOUNDATION",
    5: "PROBLEM FORMULATION",
    6: "PROBLEM FORMULATION",
    7: "RELATED WORK",
    8: "LITERATURE AUDIT",
    9: "DATASET & GROUND TRUTH",
    10: "DATASET & GROUND TRUTH",
    11: "DATA HYGIENE & PARSING",
    12: "FEATURE REPRESENTATION & ABLATION",
    13: "METHODOLOGY & PROTOCOL",
    14: "METHODOLOGY & PIPELINE",
    15: "METHODOLOGICAL DECISIONS",
    16: "EMPIRICAL RESULTS",
    17: "EMPIRICAL RESULTS",
    18: "EMPIRICAL RESULTS",
    19: "EMPIRICAL RESULTS",
    20: "EMPIRICAL RESULTS",
    21: "GENERALISATION OUTCOMES",
    22: "GENERALISATION OUTCOMES",
    23: "GENERALISATION OUTCOMES",
    24: "PHYSICAL MECHANISMS",
    25: "PHYSICAL MECHANISMS",
    26: "PHYSICAL MECHANISMS",
    27: "PHYSICAL MECHANISMS",
    28: "PHYSICAL MECHANISMS",
    29: "OPERATIONAL VALUE",
    30: "BENCHMARKING",
    31: "LITERATURE BENCHMARK",
    32: "SYNTHESIS & ABLATIONS",
    33: "LIMITATIONS",
    34: "FUTURE DIRECTIONS",
    35: "CONCLUSIONS",
    36: "REFERENCES",
    37: "DEFENCE & DISCUSSION"
}

for s_num, new_bc in breadcrumb_map.items():
    if not new_bc:
        continue
    slide = prs.slides[s_num - 1]
    # Update breadcrumb textbox (usually Shape 1, or find first short textbox)
    for shape in slide.shapes:
        if shape.has_text_frame:
            t = shape.text_frame.text.strip()
            # If it's a breadcrumb text
            if shape.top < Inches(1.1) and len(t) < 45 and not t.isdigit():
                shape.text_frame.text = new_bc
                p = shape.text_frame.paragraphs[0]
                p.font.name = FONT
                p.font.size = Pt(11)
                p.font.bold = True
                p.font.color.rgb = MUTED
                break

prs.save(PPTX_PATH)
print("Successfully reordered deck, injected new slides, and updated breadcrumbs!")
