import docx, re

doc = docx.Document('Docs/Handover_Thesis_Manuscript_Revised.docx')
for i in range(491, 672):
    p = doc.paragraphs[i]
    txt = p.text.strip()
    if re.match(r'^\s*5\.\d+', txt):
        print(f"P{i:3d} [{p.style.name:15s}]: {txt[:70]}")
