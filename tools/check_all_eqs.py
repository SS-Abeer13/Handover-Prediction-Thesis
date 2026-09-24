import docx, re

doc = docx.Document('Docs/Handover_Thesis_Manuscript_Revised.docx')
for i, p in enumerate(doc.paragraphs):
    txt = p.text.strip()
    m = re.search(r'\((\d+\.\d+)\)\s*$', txt)
    if m:
        print(f"P{i:3d} [Eq {m.group(1)}]: {txt.encode('ascii', 'replace').decode()[:80]}")
