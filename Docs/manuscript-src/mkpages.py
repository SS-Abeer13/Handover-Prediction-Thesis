#!/usr/bin/env python3
"""Map every TOC / LOF / LOT entry to the printed page number it lands on."""
import json, re, subprocess, sys, unicodedata

PDF = sys.argv[1]
txt = subprocess.run(['pdftotext', '-layout', PDF, '-'],
                     capture_output=True, text=True).stdout
pages = txt.split('\f')
E = json.load(open('/home/claude/thesis/entries.json'))


def norm(s):
    s = unicodedata.normalize('NFKD', s)
    s = re.sub(r'[‐-―−]', '-', s)
    s = re.sub(r'[^0-9A-Za-z .,%()\[\]/-]', ' ', s)
    return re.sub(r'\s+', ' ', s).strip().lower()


plines = [[norm(l) for l in p.split('\n') if l.strip()] for p in pages]
pflat = [' '.join(ls) for ls in plines]

# arabic page 1 is the page whose first line is "CHAPTER 1"
offset = next(i for i, ls in enumerate(plines) if ls and ls[0] == 'chapter 1')


def roman(n):
    vals = [(1000, 'm'), (900, 'cm'), (500, 'd'), (400, 'cd'), (100, 'c'), (90, 'xc'),
            (50, 'l'), (40, 'xl'), (10, 'x'), (9, 'ix'), (5, 'v'), (4, 'iv'), (1, 'i')]
    out = ''
    for v, s in vals:
        while n >= v:
            out, n = out + s, n - v
    return out


out, missing = {}, []

# --- preliminary pages: a page (before the body) whose first line is the heading ---
for e in E['toc']:
    if not e['key'].startswith('P::'):
        continue
    want = norm(e['key'][3:])
    idx = next((i for i in range(offset) if plines[i] and plines[i][0] == want), None)
    if idx is None:
        missing.append(e['key'])
    else:
        out[e['key']] = roman(idx + 1)          # the title page is i

# --- chapters, appendices, references: first line of a body page ---
cursor = offset
for e in E['toc']:
    if not e['key'].startswith('C::'):
        continue
    want = norm(e['key'][3:])
    idx = next((i for i in range(cursor, len(plines)) if plines[i] and plines[i][0] == want), None)
    if idx is None:
        missing.append(e['key'])
    else:
        cursor = idx
        out[e['key']] = str(idx - offset + 1)

# --- numbered section headings, in document order, body pages only ---
cursor = offset
for e in E['toc']:
    if not e['key'].startswith('H::'):
        continue
    want = norm(e['key'][3:])
    num = want.split(' ')[0]
    idx = None
    for i in range(cursor, len(plines)):
        if any(l.startswith(num + ' ') and want[:38] in l for l in plines[i]):
            idx = i
            break
    if idx is None:
        idx = next((i for i in range(cursor, len(plines)) if want[:38] in pflat[i]), None)
    if idx is None:
        missing.append(e['key'])
    else:
        cursor = idx
        out[e['key']] = str(idx - offset + 1)

# --- figure and table captions, in document order, body pages only ---
for group in ('fig', 'tab'):
    cursor = offset
    for e in E[group]:
        want = norm(e['label'])[:55]
        idx = next((i for i in range(cursor, len(plines)) if want[:40] in pflat[i]), None)
        if idx is None:
            idx = next((i for i in range(offset, len(plines))
                        if norm(e['key'][3:]) in pflat[i]), None)
        if idx is None:
            missing.append(e['key'])
        else:
            cursor = idx
            out[e['key']] = str(idx - offset + 1)

json.dump(out, open('/home/claude/thesis/pages.json', 'w'), indent=1)
print('mapped', len(out), 'entries; body starts at PDF page', offset + 1,
      '; missing', len(missing))
for m in missing[:15]:
    print('  MISSING', m)
