"""Shared slide helpers for the IUT thesis decks.

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
                col_w=None, fs=13.5, hi_last_col=True, takeaway=None,
                body_left=False):
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
    def al(j):
        if j == 0 or body_left:
            return PP_ALIGN.LEFT
        return PP_ALIGN.CENTER
    for j, txt in enumerate(header):
        last = hi_last_col and j == ncol - 1
        fill(tbl.cell(0, j), txt, True, MAROON if last else INK, al(j), HDR)
    for i, row in enumerate(rows):
        shade = WHITE if i % 2 == 0 else ALT
        for j, txt in enumerate(row):
            last = hi_last_col and j == ncol - 1
            fill(tbl.cell(i + 1, j), txt, (j == 0) or last,
                 MAROON if last else INK, al(j), shade)
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



def new_deck():
    """A copy of the template with every sample slide removed."""
    prs = Presentation(TPL)
    for i in range(len(prs.slides._sldIdLst) - 1, -1, -1):
        rId = prs.slides._sldIdLst[i].rId
        prs.part.drop_rel(rId)
        del prs.slides._sldIdLst[i]
    return prs
