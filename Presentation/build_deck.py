"""Build the thesis-defence deck on the IUT template.

The template supplies the identity: a full-bleed background picture on every
slide, Arial, and the maroon 891313 used for the title. Content and structure
follow the academic-pptx skill: action titles, one exhibit per results slide,
the key finding annotated on the figure itself, citations on slide, a
references slide, and conclusions last before the closing slide.
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
import copy, os

TPL = "/mnt/user-data/uploads/Handover Thesis/Presentation/Sample Thesis Presentation.pptx"
BG_TITLE = "/home/claude/tmpl/x/ppt/media/image1.png"
BG_BODY = "/home/claude/tmpl/x/ppt/media/image2.png"
PNG = "/home/claude/figs/png"
OUT = "/mnt/user-data/outputs/Handover-Thesis-Defence.pptx"

MAROON = RGBColor(0x89, 0x13, 0x13)
INK = RGBColor(0x26, 0x26, 0x26)
NAVY = RGBColor(0x1F, 0x4E, 0x79)
MUTED = RGBColor(0x77, 0x77, 0x77)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
FONT = "Arial"

SW, SH = 13.333, 7.5
L = 0.92                 # left margin used by the template's own placeholders
TITLE_W = 11.4           # full width: the title sits BELOW the maroon header band
BODY_TOP = 2.52
BODY_BOT = 6.56          # the maroon footer bar starts just below


def add_slide(prs, bg=BG_BODY):
    s = prs.slides.add_slide(prs.slide_layouts[6])   # Blank
    s.shapes.add_picture(bg, 0, 0, Inches(SW), Inches(SH))
    return s


def textbox(slide, x, y, w, h, anchor=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    return tf


def para(tf, text, size, color, bold=False, first=False, space_after=8,
         align=PP_ALIGN.LEFT, italic=False, space_before=0):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.alignment = align
    p.space_after = Pt(space_after)
    p.space_before = Pt(space_before)
    r = p.add_run(); r.text = text
    r.font.size = Pt(size); r.font.bold = bold; r.font.italic = italic
    r.font.name = FONT; r.font.color.rgb = color
    return p


def bullets(tf, items, size=22, color=INK, first=True, space_after=13):
    """items: list of (lead, rest) - lead is bolded, rest is regular."""
    for i, it in enumerate(items):
        p = tf.paragraphs[0] if (first and i == 0) else tf.add_paragraph()
        p.space_after = Pt(space_after)
        if isinstance(it, tuple):
            lead, rest = it
            r = p.add_run(); r.text = lead
            r.font.size = Pt(size); r.font.bold = True; r.font.name = FONT
            r.font.color.rgb = MAROON
            if rest:
                r2 = p.add_run(); r2.text = rest
                r2.font.size = Pt(size); r2.font.name = FONT; r2.font.color.rgb = color
        else:
            r = p.add_run(); r.text = it
            r.font.size = Pt(size); r.font.name = FONT; r.font.color.rgb = color


def head(slide, breadcrumb, title):
    if breadcrumb:
        tf = textbox(slide, L, 0.95, 7.0, 0.34)
        para(tf, breadcrumb.upper(), 12, MUTED, bold=True, first=True, space_after=0)
    tf = textbox(slide, L, 1.45, TITLE_W, 1.00)
    para(tf, title, 27, MAROON, bold=True, first=True, space_after=0)


def cite(slide, text):
    tf = textbox(slide, L, 6.62, 11.0, 0.30)
    para(tf, text, 11, MUTED, first=True, space_after=0)


def figure(slide, name, x, y, w, h):
    """Place a PNG inside the box (x,y,w,h), preserving aspect ratio."""
    from PIL import Image
    p = os.path.join(PNG, name + ".png")
    iw, ih = Image.open(p).size
    ar = iw / ih
    if w / h > ar:
        fh, fw = h, h * ar
    else:
        fw, fh = w, w / ar
    slide.shapes.add_picture(p, Inches(x + (w - fw) / 2), Inches(y + (h - fh) / 2),
                             Inches(fw), Inches(fh))


def fit_size(notes, w_in, h_in, base=18.0, floor=13.5):
    """Largest body size at which the interpretation column still fits."""
    import math
    size = base
    while size >= floor:
        cpl = max(12, w_in * 72.0 / (size * 0.50))
        sa = 12 if size >= 18 else 10
        lines = sum(max(1, math.ceil((len(a) + len(b)) / cpl)) for a, b in notes)
        h = lines * size * 1.24 / 72.0 + len(notes) * sa / 72.0
        if h <= h_in:
            return size, sa
        size -= 0.5
    return floor, 8


def fig_slide(prs, crumb, title, fig, notes, cite_text=None, wide=False,
              portrait=False, takeaway=None):
    """Figure left, interpretation right - the skill's results layout."""
    s = add_slide(prs)
    head(s, crumb, title)
    if portrait:
        takeaway = None          # a tall figure needs the full column height
    bot = (BODY_BOT - 0.50) if takeaway else BODY_BOT
    if portrait:
        # a tall figure gets a narrow column and a wider commentary block
        figure(s, fig, L, 1.97, 3.62, bot - 1.97)
        tf = textbox(s, 5.00, BODY_TOP + 0.20, 7.40, bot - BODY_TOP - 0.20)
        bullets(tf, notes, size=19, space_after=17)
    elif wide:
        figure(s, fig, L, BODY_TOP - 0.05, 11.5, bot - BODY_TOP + 0.05)
        if notes:
            tf = textbox(s, L, bot - 0.30, 11.5, 0.36)
            para(tf, notes[0], 17, INK, first=True, space_after=0)
    else:
        figure(s, fig, L, BODY_TOP - 0.05, 7.05, bot - BODY_TOP + 0.05)
        tf = textbox(s, 8.30, BODY_TOP + 0.05, 4.10, bot - BODY_TOP)
        fs, sa = fit_size(notes, 4.10, bot - BODY_TOP - 0.05)
        bullets(tf, notes, size=fs, space_after=sa)
    if takeaway:
        takeaway_bar(s, takeaway)
    if cite_text:
        cite(s, cite_text)
    return s


def flow_slide(prs, crumb, title, diagram, notes, cite_text=None, dh=None, takeaway=None):
    """Mermaid workflow across the full width, takeaways in two columns below."""
    from PIL import Image
    s = add_slide(prs)
    head(s, crumb, title)
    p = os.path.join(PNG, diagram + ".png")
    iw, ih = Image.open(p).size
    hmax = (dh if dh else 2.45) - (0.34 if takeaway else 0.0)
    w = 11.5
    h = w * ih / iw
    if h > hmax:
        h = hmax; w = h * iw / ih
    s.shapes.add_picture(p, Inches(L + (11.5 - w) / 2), Inches(BODY_TOP - 0.10),
                         Inches(w), Inches(h))
    ty = BODY_TOP - 0.10 + h + 0.22
    bot = (BODY_BOT - 0.50) if takeaway else BODY_BOT
    half = (len(notes) + 1) // 2
    tf = textbox(s, L, ty, 5.55, bot - ty)
    bullets(tf, notes[:half], size=(16 if not takeaway else 15), space_after=(9 if not takeaway else 7))
    if notes[half:]:
        tf2 = textbox(s, 6.85, ty, 5.55, bot - ty)
        bullets(tf2, notes[half:], size=(16 if not takeaway else 15), space_after=(9 if not takeaway else 7))
    if takeaway:
        takeaway_bar(s, takeaway)
    if cite_text:
        cite(s, cite_text)
    return s


def bullet_slide(prs, crumb, title, items, cite_text=None, size=22, two_col=None, takeaway=None):
    s = add_slide(prs)
    head(s, crumb, title)
    if two_col:
        a, b = two_col
        tf = textbox(s, L, BODY_TOP, 5.45, 4.5)
        para(tf, a[0], 20, NAVY, bold=True, first=True, space_after=12)
        bullets(tf, a[1], size=size, first=False, space_after=14)
        tf2 = textbox(s, 6.85, BODY_TOP, 5.55, 4.5)
        para(tf2, b[0], 20, NAVY, bold=True, first=True, space_after=12)
        bullets(tf2, b[1], size=size, first=False, space_after=14)
    else:
        tf = textbox(s, L, BODY_TOP, 11.4, (3.55 if takeaway else 4.6))
        bullets(tf, items, size=size, space_after=16)
    if takeaway:
        takeaway_bar(s, takeaway)
    if cite_text:
        cite(s, cite_text)
    return s


def takeaway_bar(slide, text, y=None):
    """The one-sentence conclusion strip that closes every content slide."""
    from pptx.enum.shapes import MSO_SHAPE
    yy = 6.18 if y is None else y
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(L), Inches(yy),
                                Inches(11.5), Inches(0.42))
    sh.fill.solid(); sh.fill.fore_color.rgb = RGBColor(0xF4, 0xEC, 0xEC)
    sh.line.fill.background(); sh.shadow.inherit = False
    tf = sh.text_frame; tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = Inches(0.18); tf.margin_right = Inches(0.18)
    tf.margin_top = 0; tf.margin_bottom = 0
    para(tf, text, 15, MAROON, bold=True, first=True, space_after=0)
    return sh


def table_slide(prs, crumb, title, header, rows, cite_text=None, note=None,
                col_w=None, fs=13.5, hi_last_col=True, takeaway=None):
    """A data table - used where a figure would only redraw a table badly."""
    from pptx.util import Pt as _Pt
    s = add_slide(prs)
    head(s, crumb, title)
    ncol = len(header); nrow = len(rows) + 1
    total_w = 11.5
    if col_w is None:
        first = 3.15
        col_w = [first] + [(total_w - first) / (ncol - 1)] * (ncol - 1)
    top = BODY_TOP - 0.02
    bot = (BODY_BOT - 0.50) if takeaway else BODY_BOT
    h = min(0.40, (bot - top - (0.5 if note else 0.0)) / nrow)
    shp = s.shapes.add_table(nrow, ncol, Inches(L), Inches(top),
                             Inches(total_w), Inches(h * nrow))
    tbl = shp.table
    tbl.first_row = True; tbl.horz_banding = False
    for j, w in enumerate(col_w):
        tbl.columns[j].width = Inches(w)
    for i in range(nrow):
        tbl.rows[i].height = Inches(h)

    def fill(cell, text, bold, colr, align, shade):
        cell.margin_left = Inches(0.08); cell.margin_right = Inches(0.06)
        cell.margin_top = Inches(0.02); cell.margin_bottom = Inches(0.02)
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        cell.fill.solid(); cell.fill.fore_color.rgb = shade
        tf = cell.text_frame; tf.word_wrap = True
        pr = tf.paragraphs[0]; pr.alignment = align
        r = pr.add_run(); r.text = text
        r.font.size = _Pt(fs); r.font.bold = bold
        r.font.name = FONT; r.font.color.rgb = colr

    HDR = RGBColor(0xF1, 0xEC, 0xEC)
    ALT = RGBColor(0xFA, 0xFA, 0xFA)
    for j, txt in enumerate(header):
        last = hi_last_col and j == ncol - 1
        fill(tbl.cell(0, j), txt, True, MAROON if last else INK,
             PP_ALIGN.LEFT if j == 0 else PP_ALIGN.CENTER, HDR)
    for i, row in enumerate(rows):
        shade = WHITE if i % 2 == 0 else ALT
        for j, txt in enumerate(row):
            last = hi_last_col and j == ncol - 1
            fill(tbl.cell(i + 1, j), txt, (j == 0) or last,
                 MAROON if last else INK,
                 PP_ALIGN.LEFT if j == 0 else PP_ALIGN.CENTER, shade)
    if note:
        tf = textbox(s, L, top + h * nrow + 0.08, 11.5, 0.42)
        para(tf, note, 14, INK, first=True, space_after=0)
    if takeaway:
        takeaway_bar(s, takeaway)
    if cite_text:
        cite(s, cite_text)
    return s


def callout(slide, x, y, w, h, lines, size=22):
    from pptx.enum.shapes import MSO_SHAPE
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y),
                                Inches(w), Inches(h))
    sh.fill.solid(); sh.fill.fore_color.rgb = RGBColor(0xF7, 0xF0, 0xF0)
    sh.line.color.rgb = MAROON; sh.line.width = Pt(1.5)
    sh.shadow.inherit = False
    tf = sh.text_frame; tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = Inches(0.25); tf.margin_right = Inches(0.25)
    for i, ln in enumerate(lines):
        bold = ln.startswith("*")
        txt = ln[1:] if bold else ln
        para(tf, txt, size, MAROON if bold else INK, bold=bold, first=(i == 0),
             space_after=8, align=PP_ALIGN.CENTER)
    return sh


# --------------------------------------------------------------------------
prs = Presentation(TPL)
for i in range(len(prs.slides._sldIdLst) - 1, -1, -1):        # start from a clean deck
    rId = prs.slides._sldIdLst[i].rId
    prs.part.drop_rel(rId)
    del prs.slides._sldIdLst[i]

# ---------------------------------------------------------------- 0. title
s = add_slide(prs, BG_TITLE)
tf = textbox(s, 0.80, 0.92, 7.5, 1.6)
para(tf, "Uncertainty-Aware Multi-Horizon Handover Prediction\nfrom Drive-Test Signalling",
     30, MAROON, bold=True, first=True, space_after=0)
tf = textbox(s, 0.80, 2.44, 8.6, 0.5)
para(tf, "How far ahead can the next LTE handover be seen, and with what guarantee?",
     16, INK, first=True, italic=True, space_after=0)
tf = textbox(s, 0.80, 2.90, 8.6, 1.35)
para(tf, "Abeer Saadman", 19, INK, bold=True, first=True, space_after=2)
para(tf, "Student ID [ID]", 13, MUTED, space_after=7)
para(tf, "Supervisor: [Supervisor Name, Title]", 15, INK, space_after=6)
para(tf, "Department of Electrical and Electronic Engineering", 13, MUTED, space_after=1)
para(tf, "Islamic University of Technology, Gazipur, Bangladesh", 13, MUTED, space_after=1)
tf = textbox(s, 0.80, 4.08, 8.6, 0.4)
para(tf, "B.Sc. Thesis Defence   |   [Date]", 14, MAROON, bold=True, first=True, space_after=0)

# ======================= CONTENT SLIDES (31) =======================

# ===== ACT I - the problem and the gap =====

# R - defence roadmap, four questions
bullet_slide(prs, "Overview", "Defence roadmap",
    [("01  Why this problem?  ", "What the reactive rule costs, what the literature does and does not do, and the five objectives that follow."),
     ("02  What was developed?  ", "Signalling-grounded labels, a hazard formulation, 107 features, and an evaluation protocol built to resist leakage."),
     ("03  What does the evidence show?  ", "Benchmark, calibration, a certified warning threshold, generalisation to an unseen corridor, and why any of it works."),
     ("04  What has been achieved?  ", "Objectives closed against their evidence, what is novel, what is refuted, and what this work does not claim.")],
    size=19,
    takeaway="A prediction is useful only if its probability, its lead time and its false-alarm cost are all stated.")

# ============ PART 1 - WHY THIS PROBLEM? ============
# 1
fig_slide(prs, "Motivation",
    "LTE hands over with a rule that acts only after the radio has already changed",
    "fig01_a3_event",
    [("Event A3 is reactive. ", "It fires once a neighbour is already better by an offset, and stays better through a time-to-trigger."),
     ("Everything downstream follows: ", "the interruption, the throughput dip, the ping-pong back."),
     ("One or two seconds of warning ", "is enough to prepare, pre-empt or suppress.")],
    "Entering condition and TTT per 3GPP TS 36.331. Curves illustrative; parameters are the deployed ones (+1 dB offset, 1 dB hysteresis, 320 ms TTT).",
    takeaway='A rule that fires at the handover is doing its job. It is simply not a predictor.')

# 1b - why the study is necessary
fig_slide(prs, "Motivation",
    "The cost is measurable, and the predictor does not exist",
    "fig27_necessity",
    [("938 handovers in under three hours, ", "a median 3.5 s apart."),
     ("A quarter go straight back, ", "and 341 times the link dropped."),
     ("Three in five A3 reports ", "are declined - signalling that bought nothing."),
     ("And no one has built the predictor ", "on this ground truth.")],
    "Left: counted from the four captures in this campaign. Right: the 22-paper protocol audit.",
    takeaway='Every figure on the left is a count from this campaign, not a model output or an estimate.')

# 4
bullet_slide(prs, "Related work",
    "Two literatures exist, and neither does what a deployable predictor needs",
    None, two_col=(
      ("Measurement studies", [
        ("Deng et al., IMC 2018: ", "recover operator mobility configurations from signalling."),
        ("Ghoshal et al., 2025: ", "handover configurations across three US operators, 48k handovers."),
        ("Strength: ", "measurement-grade ground truth."),
        ("Gap: ", "they build no predictor."),
      ]),
      ("Prediction studies", [
        ("108 references screened over three passes; ", "22 predict handover, radio-link failure or next-cell occupancy."),
        ("Mostly simulation, ", "mostly without grouped splits."),
        ("Strength: ", "models and architectures."),
        ("Gap: ", "protocol, calibration, operating cost."),
      ])),
    takeaway='The gap is structural: measurement-grade truth on one side, an ML-grade protocol on the other.',
    cite_text="Deng et al. (2018) IMC; Ghoshal et al. (2025) arXiv:2511.03116. Screening protocol and full audit in the thesis.",
    size=17)

# 5
fig_slide(prs, "Related work",
    "Of 22 comparable papers, none splits by drive and none reports calibration",
    "fig06_protocol_audit",
    [("The audit is on protocol, ", "not on headline numbers."),
     ("The survey was widened twice. ", "These rows did not move."),
     ("Naming the exceptions: ", "five split on a unit coarser than a row - by zone, device, time, travel day, deployment event. None is a per-timestep task on measured radio."),
     ("This is the gap: ", "measurement-grade truth on one side, an ML-grade protocol on the other.")],
    "Screened set of 108 references; 22 are models predicting handover, RLF or next-cell occupancy. Counting rules stated in the thesis.",
    takeaway="The audit is on protocol, never on anyone's headline number - and five papers do split coarser than a row.")

# F - foundations of the framework
table_slide(prs, "Related work",
    "Foundations: what is borrowed, and what for",
    ["Methodological strand", "The established idea", "Role in this work"],
    [["Discrete-time survival\nWiegrebe et al., 2024", "conditional event hazards", "coherent cumulative probabilities from a single fit"],
     ["Conformal risk control\nAngelopoulos et al., 2024", "distribution-free expected-risk control", "a warning threshold certified at a target miss rate"],
     ["Wireless conformal prediction\nCohen 2022; Simeone 2025", "uncertainty inside wireless systems", "shows the open question is the exchangeable unit"],
     ["Self-exciting point process\nHawkes 1971; Ogata 1988", "event clustering, and residual testing of the fit", "measures handover burstiness, with the kernel tested"],
     ["Unsupervised adaptation\nSun and Saenko, 2016", "feature alignment without target labels", "tried as a zero-cost transfer fix; reported as a negative"],
     ["Signalling measurement\nDeng 2018; Ghoshal 2025", "configurations recovered from decoded RRC", "ground truth, and a deployed rule that is measured"]],
    col_w=[3.55, 3.45, 4.50], fs=12.5,
    takeaway="The contribution is the pairing and the protocol, not new survival or conformal theory.",
    cite_text="Each source is cited again in the section that uses it, not only here. Appendix G maps the four literatures that nearly meet at this problem.")

# 2
s = add_slide(prs)
head(s, "Objectives", "The question this thesis answers, stated once")
callout(s, 1.5, 2.55, 10.3, 1.35,
        ["*Given what a phone can observe right now, how well can the next handover be",
         "*predicted, how far ahead, and with what guarantee?"], size=21)
tf = textbox(s, L, 4.20, 11.4, 2.3)
bullets(tf, [
    ("How well?  ", "Against a prevalence-aware floor, never accuracy on an imbalanced task."),
    ("How far ahead?  ", "0.5, 1, 2, 3 and 5 seconds, with the horizons kept mutually coherent."),
    ("With what guarantee?  ", "A distribution-free bound on missed handovers, per drive."),
    ("On what evidence?  ", "Real drive-test data with handover truth from decoded RRC signalling."),
], size=20, space_after=14)
takeaway_bar(s, "Each clause of the question names a standard this deck is held to for the next sixteen minutes.")

# O - objectives
bullet_slide(prs, "Objectives", "Five objectives, and where each one is answered",
    [("O1  Predict the next handover at five horizons ", "from what a phone can observe at the time  -  slides 14 and 19."),
     ("O2  Establish a benchmark a reviewer would accept: ", "seven learners grouped by drive, with the cost of getting the split wrong measured  -  slides 18, 22, 23."),
     ("O3  Make the probabilities usable, not merely well ranked: ", "coherent across horizons, calibrated, and bounded per drive  -  slides 16, 20, 24, 25."),
     ("O4  Test generalisation beyond the training capture, ", "by holding out a whole corridor and by scoring on an independent dataset  -  slides 26 and 27."),
     ("O5  Explain the mechanism rather than only reporting accuracy: ", "what predicts, what the network actually does with a report, and where ping-pong comes from  -  slides 29 to 33.")],
    size=17,
    takeaway="Each objective is closed on slide 38, with the evidence delivered and the boundary of the claim.",
    cite_text="The objectives were fixed before the fourth capture was driven, which is what makes the leave-one-capture-out test on slide 26 meaningful.")

# ============ PART 2 - WHAT WAS DEVELOPED? ============
# 6
flow_slide(prs, "Data",
    "A flat parse of the signalling misattributes, and does it silently",
    "m02_signalling",
    [("The symptom that gave it away: ", "99.4% of reports resolved to A3, which is impossible when 43% of reports carry no neighbour."),
     ("Found by comparison, not by inspection ", "- checking our extraction against a published method."),
     ("It changed four claims, ", "two of them ours. The deployed offsets are negative, not the +3 dB assumed in published work on this network.")],
    "RRC measConfig is incremental: AddMod inserts or replaces. The timeline reconstructs the state in force at each report.",
    takeaway='Found by comparison with a published method, not by inspection. It changed four claims, two of them mine.')

# 7
fig_slide(prs, "Data",
    "57 drives, two corridors, 938 signalling-confirmed handovers",
    "fig03_map_routes",
    [("Four campaigns, two regimes. ", "Three urban corridors, and one highway run to Gazipur at 49.5 km/h mean."),
     ("The drive is the unit of everything: ", "segmentation, grouping, bootstrap, and the risk-control guarantee."),
     ("Handovers are dense: ", "a median of 3.5 s apart - half are followed by another within 5 s.")],
    "GPS from the XCAL export; handover positions joined to the 1 Hz grid by nearest timestamp. Figure generated in MATLAB over OpenStreetMap tiles (map data (c) OpenStreetMap contributors, ODbL).",
    portrait=True,
    takeaway='The drive is the unit of segmentation, of grouping, of the bootstrap, and of the guarantee.')

# 7b - dataset statistics
table_slide(prs, "Data",
    "The campaign in numbers, capture by capture",
    ["", "10 Sept", "12 Sept", "13 Sept", "15 Sept", "Pooled"],
    [["corridor", "urban arterial", "urban loop", "dense urban", "HIGHWAY", "2 regimes"],
     ["drives (after quality control)", "15", "8", "20", "14", "57"],
     ["samples on the 1 Hz grid", "2,700", "1,440", "3,600", "2,520", "10,260"],
     ["duration", "46 min", "24 min", "60 min", "43 min", "2.9 h"],
     ["signalling-confirmed handovers", "290", "174", "297", "177", "938"],
     ["measurement-report instants", "4,688", "3,702", "4,098", "3,237", "15,725"],
     ["RRC re-establishments", "113", "64", "159", "5", "341"],
     ["A3 reports declined within 2 s", "57.2%", "60.1%", "63.3%", "71.9%", "62.9%"]],
    note="957 handovers are in the raw logs; the 938 inside quality-controlled drives are what the models see.",
    takeaway='The A3 configuration is identical across all four captures, which is what makes the corridor holdout a geography test.',
    cite_text="Quality control is 60 s and 60 samples per drive. A3 offsets (-15, -10, -6.5, +1, +5 dB) and TTT values (160-1024 ms) are identical across all four captures. 152 feature columns built, 107 used.")

# 8
fig_slide(prs, "Data",
    "Handovers cluster where the link is weak, and a quarter are ping-pongs",
    "fig04_map_rsrp",
    [("Ping-pong is not rare: ", "24.5% of handovers go straight back to the cell just left."),
     ("It is not uniform either: ", "the clusters sit at specific junctions, not along the whole route."),
     ("This is what motivates ", "the self-exciting point-process analysis later in the talk.")],
    "Ping-pong defined at the literature-standard 15 s return window with a per-handover denominator. Figure generated in MATLAB over OpenStreetMap tiles (map data (c) OpenStreetMap contributors, ODbL).",
    portrait=True,
    takeaway='Clustering is what motivates the self-exciting point process later in the talk.')

# 9
fig_slide(prs, "Data",
    "Every horizon is a rare-event problem, so every metric is read against its floor",
    "fig05_dataset",
    [("10,260 samples ", "on a uniform 1 Hz grid across 57 drives and four captures."),
     ("Prevalence moves ", "from 3.7% at 0.5 s to 26.0% at 5 s - accuracy would be meaningless."),
     ("The 0.5 s horizon is legitimate: ", "the event clock is millisecond-precise even though the sample clock is not.")],
    "Label prevalence computed on labelable samples only; drives shorter than 60 s are rejected by quality control.",
    takeaway='The 1 Hz grid bounds event detection at 90.5%. It does not bound horizon resolution.')

# ===== ACT III - method =====

# EF - the end-to-end framework
flow_slide(prs, "Method", "The framework end to end, in five stages", "m14_framework",
    [("Stage 02 is what makes the rest possible. ", "Handover truth is a decoded RRC command with a millisecond timestamp, not a vendor counter."),
     ("Stage 04 is the methodological claim: ", "one hazard fit rather than five classifiers, so the horizons cannot contradict each other."),
     ("Stage 05 is what the comparable literature omits: ", "a certified threshold, and a warning cost an operator would be charged for."),
     ("Executed by 18 pipeline stages with 17 passing tests. ", "A rebuild from the raw captures returns 10,260 samples and 938 handovers exactly.")],
    dh=1.35,
    takeaway="The leakage guards are structural rather than conventional: grouping by drive is enforced in the split constructor.",
    cite_text="Appendix F shows the stage graph. Every number in the thesis is written by a stage, not typed by hand.")

# 11
flow_slide(prs, "Method",
    "Handover prediction is a survival problem, not five binary tasks",
    "m04_hazard",
    [("Five independent heads can contradict each other. ", "A 1 s alarm above a 2 s alarm is impossible, yet 43.6% of rows did exactly that."),
     ("One hazard fit fixes it by identity, ", "not by post-processing - and the property holds for any learner."),
     ("One consequence worth stating: ", "class reweighting is forbidden here, because it compounds through the product.")],
    "Discrete-time survival with right-censoring at the end of each drive.",
    takeaway='Coherence here is a property of the identity, so it holds for any learner dropped into it.')

# 11b - feature engineering
flow_slide(prs, "Implementation",
    "152 columns built, 107 used, four blocks, two guards",
    "m13_features",
    [("The smallest block is the strongest: ", "seven history features, and dwell time alone reaches AUROC 0.874."),
     ("Guard one: ", "every window is backward-looking, closed at t, and none crosses a drive boundary."),
     ("Guard two: ", "a report precedes its handover command by 50-200 ms - inside one sample - so report counts stop one sample early. Seven unit tests pin that boundary."),
     ("Fitted per fold, on training rows only: ", "the degenerate filter and the robust scaler.")],
    dh=2.70,
    takeaway='The smallest block is the strongest: seven history features, and dwell time alone reaches AUROC 0.874.')

# 12
flow_slide(prs, "Evaluation",
    "Every drive is tested exactly once, and nothing from a test fold is ever fitted",
    "m03_protocol",
    [("Why not one 15% split? ", "57 drives leave 8 in test, and a bootstrap over 8 groups is wide for the wrong reason."),
     ("Paired testing needs power: ", "with 4 folds a two-sided Wilcoxon cannot return below p = 0.125 whatever the data says."),
     ("So the whole rotation repeats ", "over 5 seeds, giving 20 paired observations and a bootstrap interval on every delta.")],
    takeaway='Five seeds exist for test power: with four folds a Wilcoxon cannot return a p below 0.125.')

# ============ PART 3 - WHAT DOES THE EVIDENCE SHOW? ============
# 13
fig_slide(prs, "Results",
    "Gradient boosting reaches AUROC 0.933 at 1 s - twelve times the prevalence floor",
    "fig10_model_comparison",
    [("AUPRC 0.784 at 1 s, ", "11.7x the 6.7% prevalence floor, with an ECE of 0.024."),
     ("A linear model is second. ", "On 57 drives the sequence models have nothing extra to learn."),
     ("The deployed rule ", "reaches AUROC 0.653 and detects 5.5% of handovers one second ahead."),
     ("Event level: ", "44.7% of handovers detected at 1 s, 65.1% at 5 s.")],
    "Out-of-fold over 57 drives from four captures under the grouped rotation. Figure generated in MATLAB from the pipeline tables.",
    takeaway='Every number is read against its own floor. Accuracy would be meaningless at 6.7% prevalence.')

# 17
fig_slide(prs, "Results",
    "The hazard model earns coherence; per-horizon calibration buys ECE and destroys it",
    "fig13_hazard_results",
    [("Calibration: ", "better than an uncalibrated baseline, ECE -0.006 to -0.030, p < 0.0001 over 20 paired folds."),
     ("But a calibrated baseline wins on ECE ", "- at the cost of a held-out split and 2-5 AUPRC points."),
     ("Isotonic alone makes coherence worse: ", "maximum violation grows from 0.495 to 0.596."),
     ("The claim, narrowed: ", "calibration, coherence and ranking together, from one fit.")],
    "Six arms on identical folds, 5 seeds x 4 folds = 20 paired observations.",
    takeaway='The narrowed claim, and the defensible one: calibration, coherence and ranking together, from one fit.')

# 14
flow_slide(prs, "Results",
    "Before claiming a winner, every model was given the same tuning budget",
    "m06_tuning",
    [("The objection is standard ", "and it deserved a measurement rather than an argument: the deep baselines are under-tuned."),
     ("Equal means equal: ", "the same number of trials, the same objective, the same folds, the same seed."),
     ("The default arm is re-run here too, ", "so the two arms differ by the parameters alone.")],
    "Objective is mean inner AUPRC at the 2 s horizon - the middle horizon, so nothing is tuned to an extreme.")

# 15
fig_slide(prs, "Results",
    "The deep baselines really were under-tuned - and it does not change the answer",
    "fig11_tuning",
    [("They gain a lot: ", "Transformer +0.109 AUPRC, TCN +0.102, both far outside their confidence intervals."),
     ("They still lose: ", "no tuned sequence model reaches an untuned logistic regression."),
     ("Tuning LightGBM costs 0.021, ", "so its margin is not an artefact of favourable defaults."),
     ("One correction falls out: ", "logistic regression's ECE was a class-weight artefact.")],
    "Paired deltas with a drive-level bootstrap interval, 1 s horizon.",
    takeaway='The same search that lifts every competitor cannot lift the winner.')

# 16
fig_slide(prs, "Results",
    "Leakage is architecture-dependent: a GRU inflates by 74%, logistic regression by 4%",
    "fig12_leakage",
    [("Same data, same metrics. ", "The only change is replacing grouped-drive with random-row splitting."),
     ("The mechanism: ", "a 10 s window straddling a random split shares samples with its own training set."),
     ("Implication for the literature: ", "a published GRU result on a randomly split drive-test set reads as roughly double.")],
    "Both arms run under an identical protocol, or the comparison would measure the protocol rather than the leak.",
    takeaway='The inflation is differential, so a careless split does not merely raise scores - it reorders them.')

# 18
flow_slide(prs, "Uncertainty",
    "A distribution-free bound on missed handovers, and what it costs to hold it",
    "m05_crc",
    [("Not my machinery. ", "Conformal is already in wireless: Cohen 2022, Simeone 2025."),
     ("Mine is the exchangeable unit: ", "the whole drive, which sets the floor n ≥ 1/α − 1."),
     ("Honest about price: ", "at a 20% target the threshold alarms on 23% of samples."),
     ("Below a 15% target it rises steeply, ", "and the frontier is published, not one flattering point.")],
    "Prior wireless conformal work bounds prediction SETS for i.i.d.-within-frame tasks; this bounds a KPI over a per-drive exchangeable stream.",
    takeaway='Conformal prediction in wireless is not new. The exchangeable unit is what is new here.')

# 19
fig_slide(prs, "Uncertainty",
    "The guarantee is affordable above a 15% miss rate and expensive below it",
    "fig14_riskcontrol",
    [("Two curves, one decision: ", "the certified alarm rate falls as the tolerated miss rate rises."),
     ("At alpha = 0.20: ", "alarms on 23% of samples, misses 12.6% of handovers, bound held on 82% of test drives."),
     ("At alpha = 0.05 the alarm rate is 61%, ", "which is a guarantee nobody would deploy."),
     ("Stated, not implied: ", "a distribution-free bound is not free.")],
    "Realised test miss rate stays below the target at every operating point on the frontier.",
    takeaway='The bound is on the expected risk for a fresh drive, not on every individual drive.')

# ===== ACT V - generalisation =====

# 9b - the fourth capture and what it bought
fig_slide(prs, "Robustness",
    "A fourth capture, a new corridor, twice the speed - and the same result",
    "fig25_capture_transfer",
    [("A highway run to Gazipur, ", "49.5 km/h mean - driven after the model was frozen."),
     ("Adding it moved pooled AUROC by zero. ", "0.933 before, 0.933 after."),
     ("Held out whole it scores 0.927, ", "with the highest lift and lowest calibration error of the four."),
     ("Failures collapse too: ", "159 in the urban core, 5 on the highway.")],
    "Stage 21: train on three captures, test on the fourth, four times over. Four captures give four points - a strong design, not a large sample.",
    takeaway='Four captures give four points. This is a strong design, not a large sample.')

# 20
fig_slide(prs, "Robustness",
    "Real-to-real transfer holds, and the model matches an independent dataset's own ceiling",
    "fig15_transfer",
    [("Across captures: ", "AUROC 0.88-0.93 with nothing shared - not drives, routes, cells or scaler."),
     ("Out of domain: ", "0.752 on a public dataset whose own in-domain ceiling is 0.745."),
     ("Nothing is shared across the boundary: ", "no drive, no route, no cell, and the scaler is refitted on the target side."),
     ("Across A3 regimes: ", "a real cost of 0.088 AUROC that A3 features do not recover.")],
    "Public dataset: Shafi et al. (2025), Mendeley Data, DOI 10.17632/n2pvmtyn2j.1. Our parser agrees 310/310 with the vendor's event counter.",
    takeaway='Configuration is a real domain boundary, and conditioning on the measured A3 parameters recovers none of it.')

# 21
flow_slide(prs, "Robustness",
    "Both zero-cost domain adaptations make transfer worse, not better",
    "m07_transfer",
    [("Tried in good faith: ", "per-drive standardisation and CORAL - unsupervised, no target labels, free at deployment."),
     ("Both lose on both sides, ", "including matched-domain accuracy, which rules out a robustness trade."),
     ("Why: ", "the absolute radio level carries the signal, and feature alignment is exactly what deletes it.")],
    "LightGBM, identical held-out drives on every arm. Figures comparable across adaptations within this experiment only.")

# ===== ACT VI - mechanism =====

# 22
fig_slide(prs, "Network analysis",
    "The quantity the deployed rule thresholds on is the weakest predictor available",
    "fig17_mechanism",
    [("Dwell time wins: ", "how long the phone has already been on the cell, AUROC 0.874."),
     ("The A3 gap loses: ", "0.566, barely above chance."),
     ("Why: ", "the gap condition is necessary but not sufficient - it holds on 27% of samples, and three in five resulting reports are declined."),
     ("Signalling features are informative alone ", "and redundant in combination.")],
    "Single-feature AUROC at the 1 s horizon, out-of-fold over 57 drives.",
    takeaway='The A3 gap condition is necessary, and nowhere near sufficient.')

# 24
flow_slide(prs, "Network analysis",
    "Three in five A3 reports are declined, and most of all on the highway",
    "m09_conversion",
    [("62.9% of A3 reports declined at 2 s ", "- report set and window stated, because both move the number."),
     ("It rises with cell size: ", "57.2% urban arterial, 63.3% dense urban, 71.9% on the highway."),
     ("Reporting a condition is not acting on it. ", "The entering condition is necessary, nowhere near sufficient.")],
    "Ghoshal et al. (2025) report 69-87% non-conversion across three US operators; their report set and window are not stated, so the comparison is directional.",
    takeaway='Report set and window both move this number by ten to twenty points, so both are stated with it.')

# 23
fig_slide(prs, "Network analysis",
    "Handovers are strongly self-exciting: six in ten follow another handover",
    "fig18_hawkes",
    [("Branching ratio 0.605 ", "[0.524, 0.673], stable across four captures and two mobility regimes."),
     ("Decisively non-Poisson, ", "and not a renewal process either."),
     ("Honest about fit: ", "the exponential kernel is itself rejected by an Ogata residual test."),
     ("So 0.61 is ", "a calibrated measure of clustering strength under a stated kernel, not a generative claim.")],
    "Pooled over four captures and 930 events; the highway capture sits lowest at 0.513, as wider cells should.",
    takeaway='A calibrated measure of clustering strength under a stated kernel - not a generative claim.')

# 23b - the definition ladder
fig_slide(prs, "Network analysis",
    "The same 938 handovers give a ping-pong rate anywhere from 24.5% to 41.3%",
    "fig23_pingpong_definitions",
    [("Three choices, rarely stated. ", "Same cell? Immediate return? Which events count?"),
     ("Cell identity: 4.5 points. ", "Six carriers, and PCIs repeat across them."),
     ("The return rule: 9.5 points. ", "Handovers come a median 3.5 s apart."),
     ("So published rates ", "are not comparable. That is a finding, not a complaint.")],
    "All four rows computed on the same 938 signalling-confirmed handovers. The thesis quotes the top row and states all three choices with it.",
    takeaway='Published ping-pong rates are not comparable with one another. That is a finding, not a complaint.')

# 23c - the mechanism
fig_slide(prs, "Network analysis",
    "Ping-pong is one carrier layer and one A3 profile, not speed",
    "fig24_pingpong_mechanism",
    [("Five times the rate ", "when the handover stays on its carrier: 31.0% vs 6.5%."),
     ("Not the negative offsets. ", "-15 and -10 dB are the inter-frequency profiles."),
     ("One profile carries it: ", "+1 dB, 320 ms TTT, 72% of all handovers, 29.2%."),
     ("The lever is that TTT. ", "Not speed: the highway still returns 31.1%.")],
    "Ping-pong flagged as A to B and straight back within 15 s, cell identified by PCI and carrier.",
    takeaway='The lever is a time-to-trigger of 320 ms, and that is a parameter an operator can change.')

# ===== ACT VII - value and positioning =====

# 25
fig_slide(prs, "Benefit",
    "A warning earns its alarm budget only up to about 20% of samples",
    "fig20_benefit",
    [("Coverage alone is not evidence. ", "The reference is a same-rate random alarm."),
     ("Without that reference ", "the benefit is overstated by two thirds at a 10% budget."),
     ("A prediction of mine was refuted: ", "a dedicated ping-pong model reaches AUROC 0.51 - chance."),
     ("Because ", "every ping-pong is a handover, and handovers are far more predictable.")],
    "Excess coverage over a same-rate random alarm, by alarm budget. Actuator efficacy is stated, not estimated.",
    takeaway='Without a same-rate random reference the benefit is overstated by two thirds at a 10% alarm budget.')

# ============ PART 4 - WHAT HAS BEEN ACHIEVED? ============
# 26
flow_slide(prs, "Positioning",
    "The nearest published method on this network scores 0.489 where this work scores 0.921",
    "m10_departmental",
    [("Reimplemented exactly, ", "then scored generously on the rows its own dataset always has."),
     ("Their five features are informative: ", "our learner reaches 0.766 from them. The gap is the method, not the inputs."),
     ("Their own reward beats their agent, ", "0.624 against 0.489 - the reinforcement learning adds nothing the reward did not already contain.")],
    "Same operator, city and instrument. No publication record found; held as an unpublished manuscript.",
    takeaway='The gap is the method, not the features: our learner reaches 0.766 on their own five inputs.')

# 26b - the fair comparison with the literature
fig_slide(prs, "Positioning",
    "The two comparisons with the literature that are actually fair",
    "fig26_literature_headtohead",
    [("Left: reimplemented, not quoted. ", "Same 654 rows, same protocol."),
     ("Right: why headlines do not travel. ", "Always saying no scores 93.3% accuracy here - and 6.7% AUPRC."),
     ("7 of 22 audited papers ", "quote accuracy on an imbalanced task."),
     ("So we compare on protocol ", "and on reimplementation, never across datasets.")],
    "Stage 20 on the four-capture dataset. Cross-dataset accuracy comparisons are not made anywhere in this work.",
    takeaway='Compare by reimplementation, or on protocol. Never by quoting a number across datasets.')

# 26c - novelty
fig_slide(prs, "Novelty",
    "Every method here is borrowed on purpose; what is new is where each one is pointed",
    "fig28_novelty",
    [("Nothing on the left is invented, ", "and each component is cited where it is used."),
     ("The right column is the thesis: ", "a survival identity aimed at handover, a conformal guarantee whose unit is the drive, a branching ratio for handover arrivals."),
     ("Borrowing well is a contribution ", "when the pairing is new and the protocol is honest.")],
    "Full contribution table with nineteen numbered items in the thesis; appendix F carries the provenance map.",
    takeaway='Borrowing well is a contribution when the pairing is new and the protocol is honest.')

# AC - achievements against the objectives
table_slide(prs, "Achievements",
    "Objectives, evidence, and the boundary of each claim",
    ["Objective", "Evidence delivered", "Status and boundary"],
    [["O1  Multi-horizon prediction", "five horizons; 1 s AUPRC 0.784, AUROC 0.933, ECE 0.024  -  11.7x the floor", "Met  -  on 57 drives, one operator, four days"],
     ["O2  A credible benchmark", "seven learners, grouped rotation over 5 seeds, equal tuning budget, leakage study", "Met  -  the tuned arm is still a three-capture run"],
     ["O3  Usable probabilities", "0% coherence violations against 43.6%; ECE -0.006 to -0.029; a certified per-drive bound", "Met  -  under per-drive exchangeability, stated"],
     ["O4  Generalisation", "leave-one-capture-out 0.909 to 0.949; external 0.752 against that data's own 0.745", "Met  -  a four-point design, not a large sample"],
     ["O5  Mechanism", "dwell 0.874 against the A3 gap 0.566; 62.9% of reports declined; branching ratio 0.605", "Met  -  the Hawkes kernel is misspecified, and said so"],
     ["(not claimed)  Network benefit", "a counting upper bound against a same-rate random alarm; no controlled intervention", "Future work  -  off-policy evaluation is unidentified"]],
    col_w=[2.85, 5.05, 3.60], fs=12,
    takeaway="Every objective is met on the evidence stated. The causal claim is the one this work does not make.",
    cite_text="The boundary column uses the same wording as the thesis limitations section, so the two cannot drift apart.")

# 27
fig_slide(prs, "Synthesis",
    "More information and more machinery did not help; formulation and configuration did",
    "fig22_negatives",
    [("Five channels added in good faith, ", "each expected to help, each measured."),
     ("Every negative is measured, not assumed ", "- which is what makes the pattern worth stating at all."),
     ("Three things moved the result: ", "reformulating the target, the configuration regime, and grouping the split by drive.")],
    "Each row is a controlled comparison run under the same protocol.",
    takeaway='Every negative here is a controlled comparison with a stated mechanism, not an absence of effort.')

# ===== ACT VIII - close =====

# 28
bullet_slide(prs, "Discussion", "What this work cannot claim",
    [("Scale.  ", "57 drives, two corridors, one operator, four days. Enough for grouped cross-validation with 57 bootstrap groups and a four-point leave-one-capture-out design; not enough to claim generality across cities or operators."),
     ("Sampling rate.  ", "1 Hz caps event detection at 90.5%. It does not cap horizon resolution - the event clock is finer than the sample clock."),
     ("Cross-regime transfer rests on one regime pair.  ", "Only two A3 profiles clear the 60-handover bar on an identical test set."),
     ("No causal estimate of the actuator.  ", "Off-policy evaluation is unidentified here because the logging policy is deterministic: A3 either fires or it does not."),
     ("The Hawkes kernel is misspecified, ", "and the thesis says so rather than leaving a reviewer to find it."),
     ], size=17,
    takeaway='Every limitation is stated with the measurement that bounds it.',
    cite_text="Each limitation is stated in the thesis alongside the measurement that bounds it.")

# 29
bullet_slide(prs, "Future work",
    "Four directions, and one of them makes the causal question identifiable",
    [("Fuzzy regression discontinuity at the A3 boundary.  ", "The identifiable alternative to off-policy evaluation: compare drives just inside and just outside the firing condition."),
     ("A second corridor and a third A3 regime.  ", "One more capture day on a new route turns one regime pair into a matrix."),
     ("Close the loop to an outcome.  ", "Connect the two-second warning to a measured throughput or interruption effect, not a counting bound."),
     ("Release the code and the dataset.  ", "Two of 22 audited papers release code and one releases data; a release is a citable output in its own right."),
     ], size=17,
    takeaway='The first direction is the identifiable route to the causal effect the previous slide rules out.')

# 30 - conclusions (last main slide, stays up during Q&A)
s = add_slide(prs)
head(s, "Conclusion", "Conclusions")
tf = textbox(s, L, 2.50, 11.4, 3.95)
bullets(tf, [
    ("1.  Handover is predictable well ahead of the rule that causes it.  ",
     "AUROC 0.933 and AUPRC 0.784 at 1 s on signalling ground truth - nearly twelve times the prevalence floor, with calibrated probabilities and a per-drive bound. Unchanged when a highway capture was added."),
    ("2.  Formulation beats information.  ",
     "A discrete-time hazard delivers coherence, calibration and ranking from one fit; five separate information channels delivered nothing."),
    ("3.  The protocol is as much the contribution as the model.  ",
     "Grouped splits, a prevalence floor, event-level costs and a distribution-free bound - none of which the comparable literature reports."),
    ("4.  Negative results were measured and published, not discarded.  ",
     "Including one prediction of my own that was refuted."),
], size=17, space_after=14)
tf = textbox(s, L, 6.50, 11.4, 0.40)
para(tf, "Abeer Saadman  |  Department of EEE, Islamic University of Technology  |  [email]",
     14, MAROON, bold=True, first=True, space_after=0)

# 31 - references
s = add_slide(prs)
head(s, "References", "Selected references")
refs = [
 "3GPP TS 36.331. Evolved Universal Terrestrial Radio Access (E-UTRA); Radio Resource Control (RRC); Protocol specification.",
 "Angelopoulos, A.N., Bates, S., Candes, E.J., Jordan, M.I. & Lei, L. (2022). Conformal Risk Control. arXiv:2208.02814.",
 "Ankome, T. & Hanada, E. (2026). Reactive to Predictive Mobility Management: A Systematic Review of ML-Driven Handover Optimization in 5G and Beyond. Machine Learning and Knowledge Extraction, 8(5), 133.",
 "Cohen, K.M., Park, S., Simeone, O. & Shamai Shitz, S. (2022). Calibrating AI Models for Wireless Communications via Conformal Prediction. arXiv:2212.07775.",
 "Deng, Y., Peng, C., Fida, M.-R., Meng, J. & Hu, Y.C. (2018). Mobility Support in Cellular Networks: A Measurement Study on Its Configurations and Implications. ACM IMC, 147-160.",
 "Ghoshal, M., Khan, I., Dinh, T., Kong, Z., Basit, A., Wang, W., Feng, Y., Hu, Y.C. & Koutsonikolas, D. (2025). Handover Configurations in Operational 5G Networks. arXiv:2511.03116.",
 "Hasan, K., Trappenberg, T. & Haque, I. (2024). A Generalized Transformer-based Radio Link Failure Prediction Framework in 5G RANs. arXiv:2407.05197.",
 "Hawkes, A.G. (1971). Spectra of some self-exciting and mutually exciting point processes. Biometrika, 58(1), 83-90.",
 "Ke, G., Meng, Q., Finley, T., Wang, T., Chen, W., Ma, W., Ye, Q. & Liu, T.-Y. (2017). LightGBM: A Highly Efficient Gradient Boosting Decision Tree. NeurIPS.",
 "Laub, P.J., Lee, Y., Pollett, P.K. & Taimre, T. (2025). Hawkes Models and Their Applications. Annual Review of Statistics and Its Application, 12, 233-258.",
 "Ogata, Y. (1988). Statistical models for earthquake occurrences and residual analysis for point processes. JASA, 83(401), 9-27.",
 "Price-Williams, M. & Heard, N.A. (2020). Nonparametric self-exciting models for computer network traffic. Statistics and Computing, 30(2), 209-220.",
 "Shafi, M.M.S., Istiaque, K.M., Sowad, S.S. & Kawser, M.T. (2025). Drive-Test-Based LTE Handover Dataset for Cellular Mobility Studies in Urban Bangladesh. Mendeley Data, V1. DOI 10.17632/n2pvmtyn2j.1.",
 "Sun, B. & Saenko, K. (2016). Deep CORAL: Correlation Alignment for Deep Domain Adaptation. ECCV 2016 Workshops, LNCS 9915, 443-450.",
 "Wiegrebe, S., Kopper, P., Sonabend, R., Bischl, B. & Bender, A. (2024). Deep learning for survival analysis: a review. Artificial Intelligence Review, 57(3), 65.",
 "Zidic, A., Mastelic, T., Nizetic Kosovic, I., Cagalj, M. & Lorincz, J. (2023). Analyses of ping-pong handovers in real 4G telecommunication networks. Computer Networks, 227, 109699.",
]
half = (len(refs) + 1) // 2
for col, chunk in enumerate((refs[:half], refs[half:])):
    tf = textbox(s, L + col * 5.80, 2.45, 5.55, 4.15)
    for i, r in enumerate(chunk):
        para(tf, r, 10.5, INK, first=(i == 0), space_after=6)
tf = textbox(s, L, 6.66, 11.4, 0.32)
para(tf, "Full bibliography: 108 screened references, 93 verified against the publisher or author record; 22-paper protocol audit.",
     11, MUTED, first=True, space_after=0)

# ---- closing
s = add_slide(prs, BG_TITLE)
tf = textbox(s, 0.80, 1.55, 8.4, 1.2)
para(tf, "Thank you", 44, MAROON, bold=True, first=True, space_after=0)
tf = textbox(s, 0.80, 2.85, 8.4, 1.4)
para(tf, "Questions and feedback welcome", 22, INK, first=True, space_after=12)
para(tf, "Abeer Saadman  |  Department of EEE, Islamic University of Technology", 15, MUTED)

# ======================= APPENDIX (pre-built Q&A) =======================
def appendix(prs, tag, title, fig, notes, cite_text=None):
    s = add_slide(prs)
    tf = textbox(s, L, 0.95, 7.0, 0.34)
    para(tf, tag.upper(), 12, MUTED, bold=True, first=True, space_after=0)
    tf = textbox(s, L, 1.45, TITLE_W, 1.00)
    para(tf, title, 25, MAROON, bold=True, first=True, space_after=0)
    figure(s, fig, L, BODY_TOP - 0.05, 7.05, BODY_BOT - BODY_TOP + 0.05)
    tf = textbox(s, 8.30, BODY_TOP + 0.05, 4.10, 4.5)
    bullets(tf, notes, size=17, space_after=13)
    if cite_text: cite(s, cite_text)

appendix(prs, "Appendix A - backup",
    "The configuration-timeline defect, measured",
    "fig07_config_timeline",
    [("Likely question: ", "how do you know the flat parse was wrong?"),
     ("Because 43% of reports carry no neighbour, ", "so 99.4% A3 attribution is arithmetically impossible."),
     ("The log itself shows ", "1,424 A1, 1,401 A2 and 1,309 A3 configurations in one capture.")])

appendix(prs, "Appendix B - backup",
    "The hazard identity, panel by panel",
    "fig08_hazard_concept",
    [("Likely question: ", "why not just calibrate five heads?"),
     ("Because calibration is per horizon ", "and nothing couples the horizons to each other."),
     ("The product-limit identity couples them ", "before any calibration is applied.")])

appendix(prs, "Appendix C - backup",
    "Domain adaptation, arm by arm",
    "fig16_adaptation",
    [("Likely question: ", "did you try domain adaptation?"),
     ("Yes, two standard unsupervised methods, ", "and both lose on both sides of the transfer."),
     ("Matched-domain AUROC also falls ", "(0.819 to 0.796 / 0.800), which rules out a robustness trade.")])

appendix(prs, "Appendix D - backup",
    "Report conversion, in numbers",
    "fig19_conversion",
    [("Likely question: ", "is report conversion just the A3 rule restated?"),
     ("No: ", "the gate is satisfied for every one of these reports, yet three in five are declined."),
     ("The rate tracks cell size: ", "57.2% urban arterial, 63.3% dense urban, 71.9% on the highway."),
     ("A predictor for this task ", "is left for future work; on four captures it does not yet separate.")])

appendix(prs, "Appendix E - backup",
    "The departmental comparison, arm by arm",
    "fig21_departmental",
    [("Likely question: ", "is this a fair comparison?"),
     ("Every choice was made in their favour: ", "full learned advantage, their own row population, their more favourable gate reading."),
     ("Their published TTT filter ", "consumes TTT seconds of the future, so it is inadmissible as evidence of prediction.")])


# ---- appendix F and G: the pipeline and the literature map
# ---- appendix F and G: demoted from the main path
# 10
flow_slide(prs, "Appendix F - backup", "One pipeline, with the leakage guards built into its architecture",
    "m01_pipeline",
    [("18 stages, 17 passing tests. ", "Every number in the thesis is written by a stage, not typed."),
     ("The guards are structural, not conventions: ", "grouping is by whole drive, and nothing from a test fold is ever fitted."),
     ("Reproducible: ", "a rebuild from the raw captures returns 10,260 samples and 938 handovers exactly.")])

# ===== ACT IV - results =====

# 5b
flow_slide(prs, "Appendix G - backup",
    "Four literatures nearly meet here, and none of them quite touches",
    "m11_litmap",
    [("Measurement studies have the ground truth ", "and build no predictor."),
     ("Prediction studies build predictors ", "on simulation, without grouped splits, without calibration."),
     ("Survival and point-process methods are mature ", "and have never been aimed at a drive test."),
     ("Conformal has entered wireless, ", "but for i.i.d.-in-frame signal processing, not a mobility event stream.")],
    "Pass-3 literature map. Full thread-by-thread synthesis in the thesis.")

# ===== ACT II - the data, and why it can be trusted =====

# 5d
bullet_slide(prs, "Appendix H - backup", "Two claims the widened survey forced me to make smaller",
    [("Conformal prediction in wireless is not new.  ",
      "Cohen et al. (2022) and Simeone et al. (2025) got there first. What survives as mine is narrower and better defended: their guarantee is over prediction SETS for tasks that are i.i.d. within a frame; mine is a RISK guarantee on an operator KPI over a stream exchangeable only by whole drive. The exchangeability unit is the contribution; the feasibility floor n ≥ 1/α − 1 is its consequence."),
     ("The grouped-split claim has now been amended twice.  ",
      "Doc 21 found one paper splitting by time. Pass 3 found two more - by travel day, and by deployment event. The honest form: ten of 22 state no split at all, five split on a unit coarser than a row, and none holds out the mobility unit for a per-timestep classification task on measured radio."),
     ("Why say this out loud in a defence.  ",
      "The leakage result in this talk does not depend on scarcity. It depends on the inflation being real and differential - 74% for a GRU against 4% for logistic regression - and that was measured, not asserted."),
     ], size=17,
    cite_text="Doc 22, sections 2M and 4. Both narrowed claims are stated in the thesis limitations section as well as in the positioning section.")


os.makedirs(os.path.dirname(OUT), exist_ok=True)
prs.save(OUT)
n = len(prs.slides._sldIdLst)
print("slides:", n)
print("saved", OUT)
