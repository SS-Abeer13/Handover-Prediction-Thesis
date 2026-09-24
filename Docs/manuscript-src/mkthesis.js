// Thesis builder — EEE 4700/4800, Islamic University of Technology
// Format rules taken from "EEE_4700_4800_Project and Thesis Guidelines updated221.pdf"
// 12 pt Times New Roman, 1.5 spacing, margins L3 / R2.5 / T2.5 / B2.5 cm, 1 cm indent.
const fs = require('fs');
const d = require('docx');
const { Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, Table, TableRow,
        TableCell, WidthType, BorderStyle, PageBreak, PageNumber, NumberFormat, Footer,
        TableOfContents, StyleLevel, ImageRun, TabStopType, TabStopPosition } = d;

const SRC = process.argv[2], OUT = process.argv[3];
const md = fs.readFileSync(SRC, 'utf8').split('\n');

const FONT = 'Times New Roman';
const SZ = 24;                    // 12 pt
const LINE = 360;                 // 1.5 spacing
const INDENT = 567;               // 1 cm
const CM = (n) => Math.round(n * 567);
const CONTENT = 12240 - CM(3) - CM(2.5);   // Letter width minus margins, in DXA

// ---------- inline formatting: **bold**, *italic*, `code`, <sub>, <sup> ----------
function runs(text, base = {}) {
  const b = { font: FONT, size: SZ, ...base };
  const out = [];
  const re = /(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`|<sub>[^<]*<\/sub>|<sup>[^<]*<\/sup>)/g;
  let last = 0, m;
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) out.push(new TextRun({ ...b, text: text.slice(last, m.index) }));
    const t = m[0];
    if (t.startsWith('**')) out.push(new TextRun({ ...b, text: t.slice(2, -2), bold: true }));
    else if (t.startsWith('`')) out.push(new TextRun({ ...b, text: t.slice(1, -1) }));
    else if (t.startsWith('<sub>')) out.push(new TextRun({ ...b, text: t.slice(5, -6), subScript: true }));
    else if (t.startsWith('<sup>')) out.push(new TextRun({ ...b, text: t.slice(5, -6), superScript: true }));
    else out.push(new TextRun({ ...b, text: t.slice(1, -1), italics: true }));
    last = m.index + t.length;
  }
  if (last < text.length) out.push(new TextRun({ ...b, text: text.slice(last) }));
  return out.length ? out : [new TextRun({ ...b, text: '' })];
}

const body = (text, opts = {}) => new Paragraph({
  alignment: AlignmentType.JUSTIFIED,
  spacing: { line: LINE, after: 0 },
  indent: { firstLine: opts.noIndent ? 0 : INDENT },
  children: runs(text),
});
const blank = (n = 1) => Array.from({ length: n }, () => new Paragraph({
  spacing: { line: LINE }, children: [new TextRun({ font: FONT, size: SZ, text: '' })] }));

// ---------- tables ----------
function buildTable(rows) {
  const n = Math.max(...rows.map(r => r.length));
  // width each column in proportion to the longest cell it holds, with a floor and a ceiling
  const score = Array.from({ length: n }, (_, c) => {
    const lens = rows.map(r => (r[c] || '').replace(/[*`]/g, '').length);
    return Math.max(6, Math.min(60, Math.max(...lens) * 0.45 + (lens.reduce((a, b) => a + b, 0) / lens.length) * 0.55));
  });
  const tot = score.reduce((a, b) => a + b, 0);
  const widths = score.map(v => Math.max(CM(1.6), Math.round(CONTENT * v / tot)));
  const over = widths.reduce((a, b) => a + b, 0) - CONTENT;
  if (over !== 0) widths[score.indexOf(Math.max(...score))] -= over;
  return new Table({
    columnWidths: widths,
    width: { size: CONTENT, type: WidthType.DXA },
    rows: rows.map((cells, ri) => new TableRow({
      tableHeader: ri === 0,
      children: Array.from({ length: n }, (_, ci) => new TableCell({
        width: { size: widths[ci], type: WidthType.DXA },
        margins: { top: 60, bottom: 60, left: 100, right: 100 },
        children: [new Paragraph({
          alignment: AlignmentType.LEFT,
          spacing: { line: 240, before: 0, after: 0 },       // single-spaced inside tables
          children: runs(cells[ci] === undefined ? '' : cells[ci], { size: 22, bold: ri === 0 }),
        })],
      })),
    })),
  });
}

// ---------- pre-scan: collect TOC / LOF / LOT entries in document order ----------
const tocE = [], figE = [], tabE = [];
{
  let seenChapter = false;
  for (const ln of md) {
    const t = ln.trim();
    if (t.startsWith('@@PRELIM|')) {
      const h = t.slice(9);
      if (h !== 'DECLARATION' && h !== 'APPROVAL' && h !== 'TABLE OF CONTENTS')
        tocE.push({ key: 'P::' + h, label: h.charAt(0) + h.slice(1).toLowerCase(), lvl: 0, roman: true });
    } else if (t.startsWith('@@CHAPTER|')) {
      const p = t.split('|'); seenChapter = true;
      tocE.push({ key: 'C::CHAPTER ' + p[1], label: 'Chapter ' + p[1] + '  ' + p[2].charAt(0) + p[2].slice(1).toLowerCase(), lvl: 0 });
    } else if (t.startsWith('@@APPENDIX|')) {
      const p = t.split('|');
      tocE.push({ key: 'C::APPENDIX ' + p[1], label: 'Appendix ' + p[1] + '  ' + p[2].charAt(0) + p[2].slice(1).toLowerCase(), lvl: 0 });
    } else if (t === '@@REFSTART') {
      tocE.push({ key: 'C::REFERENCES', label: 'References', lvl: 0 });
    } else if (t.startsWith('## ') && seenChapter) {
      tocE.push({ key: 'H::' + t.slice(3), label: t.slice(3), lvl: 1 });
    } else if (t.startsWith('### ') && seenChapter) {
      tocE.push({ key: 'H::' + t.slice(4), label: t.slice(4), lvl: 2 });
    } else if (t.startsWith('@@FIG|')) {
      const cap = t.split('|')[2];
      figE.push({ key: 'F::' + cap.slice(0, 11).trim(), label: cap });
    } else if (t.startsWith('@@TCAP|')) {
      const cap = t.slice(7);
      tabE.push({ key: 'T::' + cap.slice(0, 10).trim(), label: cap });
    }
  }
}
let PAGES = {};
try { PAGES = JSON.parse(fs.readFileSync('/home/claude/thesis/pages.json', 'utf8')); } catch (e) {}
fs.writeFileSync('/home/claude/thesis/entries.json',
  JSON.stringify({ toc: tocE, fig: figE, tab: tabE }, null, 1));

function listLine(label, key, lvl) {
  const bold = (lvl || 0) === 0;
  const leftIndent = [0, CM(0.8), CM(1.6), 0][lvl || 0];
  const pg = PAGES[key] || '0';
  return new Paragraph({
    spacing: { line: 240, after: 80 },
    indent: { left: leftIndent, right: CM(0.2), hanging: 0 },
    tabStops: [{ type: TabStopType.RIGHT, position: CONTENT - CM(0.2), leader: 'dot' }],
    children: [...runs(label, { bold, size: 24 }),
               new TextRun({ font: FONT, size: 24, bold, text: '\t' + pg })],
  });
}

// ---------- document assembly ----------
const prelim = [];   // roman-numbered section
const main = [];     // arabic-numbered section
let sink = prelim;
const push = (x) => Array.isArray(x) ? x.forEach(e => sink.push(e)) : sink.push(x);

let i = 0, inRefs = false;
while (i < md.length) {
  const raw = md[i], t = raw.trim();
  if (t === '') { i++; continue; }

  // ---- title page ----
  if (t === '@@TITLEPAGE') {
    i++;
    push(new Paragraph({
      alignment: AlignmentType.CENTER, spacing: { before: 240, after: 120, line: 240, lineRule: 'auto' },
      children: [new ImageRun({ type: 'png',
        data: fs.readFileSync('/home/claude/thesis/assets/iut_logo.png'),
        transformation: { width: 132, height: 164 } })],
    }));
    push(new Paragraph({
      alignment: AlignmentType.CENTER, spacing: { after: 360, line: LINE },
      children: runs('Islamic University of Technology', { size: 28, bold: true }),
    }));
    while (i < md.length && md[i].trim() !== '@@ENDTITLE') {
      const [tag, ...rest] = md[i].trim().split('|');
      const txt = rest.join('|');
      const style = {
        '@@T':  { size: 40, bold: true,  after: 480, before: 240 },
        '@@N':  { size: 28, bold: false, after: 480 },
        '@@S':  { size: 24, bold: false, after: 240 },
        '@@D':  { size: 24, bold: true,  after: 480 },
        '@@I':  { size: 28, bold: false, after: 40 },
        '@@Y':  { size: 28, bold: false, after: 40, before: 400 },
      }[tag];
      if (style) push(new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { line: LINE, after: style.after, before: style.before || 0 },
        children: runs(txt, { size: style.size, bold: style.bold }),
      }));
      i++;
    }
    i++; continue;
  }

  // ---- preliminary page heading ----
  if (t.startsWith('@@PRELIM|')) {
    push(new Paragraph({
      pageBreakBefore: true,
      alignment: AlignmentType.CENTER,
      spacing: { line: LINE, after: 360 },
      children: runs(t.slice(9), { size: 32, bold: true }),
    }));
    i++; continue;
  }

  if (t.startsWith('@@CENTER|') || t.startsWith('@@CENTERB|')) {
    const bold = t.startsWith('@@CENTERB|');
    push(new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { line: LINE, after: 0 },
      children: runs(t.slice(bold ? 10 : 9), { bold }),
    }));
    i++; continue;
  }

  if (t === '@@TOC') { tocE.forEach(e => push(listLine(e.label, e.key, e.lvl))); i++; continue; }
  if (t === '@@LOF') { figE.forEach(e => push(listLine(e.label, e.key, 3))); i++; continue; }
  if (t === '@@LOT') { tabE.forEach(e => push(listLine(e.label, e.key, 3))); i++; continue; }

  if (t.startsWith('@@ACRO|')) {
    const rows = [];
    while (i < md.length && md[i].trim().startsWith('@@ACRO|')) {
      const p = md[i].trim().split('|'); rows.push([p[1], p[2]]); i++;
    }
    const w1 = 2200, w2 = CONTENT - w1;
    push(new Table({
      columnWidths: [w1, w2],
      width: { size: CONTENT, type: WidthType.DXA },
      borders: ['top','bottom','left','right','insideHorizontal','insideVertical']
        .reduce((o, k) => (o[k] = { style: BorderStyle.NONE }, o), {}),
      rows: rows.map(r => new TableRow({ children: [
        new TableCell({ width: { size: w1, type: WidthType.DXA }, margins: { top: 20, bottom: 20 },
          children: [new Paragraph({ spacing: { line: 240, after: 0 }, children: runs(r[0], { bold: true }) })] }),
        new TableCell({ width: { size: w2, type: WidthType.DXA }, margins: { top: 20, bottom: 20 },
          children: [new Paragraph({ spacing: { line: 240, after: 0 }, children: runs(r[1]) })] }),
      ] })),
    }));
    continue;
  }

  // ---- chapter / appendix openers: switch to the arabic-numbered section ----
  if (t.startsWith('@@CHAPTER|') || t.startsWith('@@APPENDIX|')) {
    const isApp = t.startsWith('@@APPENDIX|');
    const parts = t.split('|');
    const firstOfBody = (sink === prelim);
    if (firstOfBody) sink = main;                   // first chapter starts the body section
    push(new Paragraph({
      pageBreakBefore: !firstOfBody,
      alignment: AlignmentType.CENTER,
      spacing: { line: LINE, after: 0 },
      children: runs((isApp ? 'APPENDIX ' : 'CHAPTER ') + parts[1], { size: 40, bold: true }),
    }));
    push(blank(1));
    push(new Paragraph({
      heading: HeadingLevel.HEADING_1,
      alignment: AlignmentType.CENTER,
      spacing: { line: LINE, before: 0, after: 0 },
      children: runs(parts[2], { size: 32, bold: true }),
    }));
    push(blank(2));
    i++; continue;
  }

  if (t === '@@REFSTART') {
    push(new Paragraph({
      heading: HeadingLevel.HEADING_1,
      pageBreakBefore: true,
      alignment: AlignmentType.CENTER,
      spacing: { line: LINE, after: 360 },
      children: runs('REFERENCES', { size: 32, bold: true }),
    }));
    inRefs = true; i++; continue;
  }

  // ---- figure ----
  if (t.startsWith('@@FIG|')) {
    const [, src, cap, wIn] = t.split('|');
    let dim = { width: 1600, height: 900 };
    try {
      const buf = fs.readFileSync(src);
      if (buf.slice(0, 8).toString('hex') === '89504e470d0a1a0a')
        dim = { width: buf.readUInt32BE(16), height: buf.readUInt32BE(20) };
    } catch (e) { /* keep default aspect */ }
    const wid = parseFloat(wIn) * 96, hei = wid * dim.height / dim.width;
    push(new Paragraph({
      alignment: AlignmentType.CENTER, spacing: { before: 240, after: 120, line: 240, lineRule: 'auto' },
      keepNext: true,
      children: [new ImageRun({ type: 'png', data: fs.readFileSync(src),
        transformation: { width: Math.round(wid), height: Math.round(hei) } })],
    }));
    push(new Paragraph({                       // caption BELOW the figure, centred
      style: 'FigureCaption',
      alignment: AlignmentType.CENTER, spacing: { after: 240, line: 240 },
      children: runs(cap, { size: 22 }),
    }));
    i++; continue;
  }

  // ---- table with its caption ABOVE ----
  if (t.startsWith('@@TCAP|')) {
    push(new Paragraph({
      style: 'TableCaption',
      alignment: AlignmentType.CENTER, spacing: { before: 240, after: 120, line: 240 },
      children: runs(t.slice(7), { size: 22 }),
    }));
    i++;
    const rows = [];
    while (i < md.length && md[i].trim().startsWith('|')) {
      const cells = md[i].trim().replace(/^\||\|$/g, '').split('|').map(s => s.trim());
      if (!cells.every(c => /^:?-{2,}:?$/.test(c))) rows.push(cells);
      i++;
    }
    push(buildTable(rows));
    push(new Paragraph({ spacing: { after: 120, line: 240 }, children: [new TextRun({ font: FONT, size: 12, text: '' })] }));
    continue;
  }

  // ---- displayed equation ----
  if (t.startsWith('@@EQ|')) {
    const p = t.split('|');
    const kids = runs(p[1], { italics: true });
    if (p[2]) {
      kids.push(new TextRun({ font: FONT, size: SZ, text: '\t' + p[2] }));
    }
    push(new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 180, after: 180, line: LINE },
      tabStops: p[2] ? [{ type: TabStopType.RIGHT, position: CONTENT }] : [],
      children: kids,
    }));
    i++; continue;
  }

  // ---- headings ----
  if (t.startsWith('#### ')) {
    push(new Paragraph({ heading: HeadingLevel.HEADING_4, alignment: AlignmentType.LEFT,
      spacing: { before: 240, after: 120, line: LINE },
      children: runs(t.slice(5), { italics: true }) })); i++; continue;
  }
  if (t.startsWith('### ')) {
    push(new Paragraph({ heading: HeadingLevel.HEADING_3, alignment: AlignmentType.LEFT,
      spacing: { before: 280, after: 120, line: LINE },
      children: runs(t.slice(4), { bold: true }) })); i++; continue;
  }
  if (t.startsWith('## ')) {
    push(new Paragraph({ heading: HeadingLevel.HEADING_2, alignment: AlignmentType.LEFT,
      spacing: { before: 360, after: 140, line: LINE },
      children: runs(t.slice(3), { bold: true }) })); i++; continue;
  }

  // ---- bullets ----
  if (/^[-*]\s+/.test(t)) {
    push(new Paragraph({ bullet: { level: 0 }, alignment: AlignmentType.JUSTIFIED,
      spacing: { line: LINE, after: 60 }, children: runs(t.replace(/^[-*]\s+/, '')) }));
    i++; continue;
  }

  // ---- references: single-spaced, hanging indent 0.5 cm ----
  if (inRefs && /^\[\d+\]/.test(t)) {
    push(new Paragraph({
      alignment: AlignmentType.JUSTIFIED,
      spacing: { line: 240, after: 120 },
      indent: { left: CM(0.5), hanging: CM(0.5) },
      children: runs(t),
    }));
    i++; continue;
  }

  push(body(t)); i++;
}

// ---------- footers ----------
const pageNo = (fmt) => new Footer({ children: [new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { line: 240, before: 0, after: 0 },
  children: [new TextRun({ font: FONT, size: SZ, children: [PageNumber.CURRENT] })],
})] });
const emptyFooter = new Footer({ children: [new Paragraph({ children: [new TextRun('')] })] });

const pageSetup = {
  size: { width: 12240, height: 15840 },
  margin: { top: CM(2.5), bottom: CM(2.5), left: CM(3), right: CM(2.5),
            header: CM(1), footer: CM(1) },
};

const doc = new Document({
  creator: 'Abeer Saadman',
  title: 'Uncertainty-Aware Multi-Horizon Handover Prediction from LTE Drive-Test Signalling',
  features: { updateFields: true },
  styles: {
    default: { document: { run: { font: FONT, size: SZ, color: '000000' },
                           paragraph: { spacing: { line: LINE } } } },
    paragraphStyles: [
      { id: 'FigureCaption', name: 'Figure Caption', basedOn: 'Normal', next: 'Normal',
        quickFormat: true, run: { font: FONT, size: 22 } },
      { id: 'TableCaption', name: 'Table Caption', basedOn: 'Normal', next: 'Normal',
        quickFormat: true, run: { font: FONT, size: 22 } },
      { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { font: FONT, size: 32, bold: true, color: '000000' } },
      { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { font: FONT, size: SZ, bold: true, color: '000000' } },
      { id: 'Heading3', name: 'Heading 3', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { font: FONT, size: SZ, bold: true, color: '000000' } },
      { id: 'Heading4', name: 'Heading 4', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { font: FONT, size: SZ, italics: true, color: '000000' } },
    ],
  },
  sections: [
    { properties: { page: { ...pageSetup,
        pageNumbers: { start: 1, formatType: NumberFormat.LOWER_ROMAN } }, titlePage: true },
      footers: { default: pageNo(), first: emptyFooter },
      children: prelim },
    { properties: { page: { ...pageSetup,
        pageNumbers: { start: 1, formatType: NumberFormat.DECIMAL } } },
      footers: { default: pageNo() },
      children: main },
  ],
});

Packer.toBuffer(doc).then(b => { fs.writeFileSync(OUT, b); console.log('wrote', OUT, b.length, 'bytes'); });
