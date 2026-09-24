import docx

doc = docx.Document('Docs/Handover_Thesis_Manuscript_Revised.docx')
for i, p in enumerate(doc.paragraphs):
    if p.style.name.startswith('Heading') or 'Chapter' in p.text or 'Appendix' in p.text:
        txt = p.text.strip().encode('ascii', 'replace').decode()
        if len(txt) > 0 and len(txt) < 80:
            print(f"P{i:3d} [{p.style.name:10s}]: {txt}")
