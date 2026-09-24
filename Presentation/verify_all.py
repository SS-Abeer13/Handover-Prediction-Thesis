import pptx
import docx
import os

# 1. PPTX verification
prs = pptx.Presentation(r"D:\Handover Thesis\Presentation\Handover-Thesis-Defence.pptx")
print("=== PPTX VERIFICATION ===")
print(f"Total slides: {len(prs.slides)}")
assert len(prs.slides) == 47, f"Expected 47 slides, got {len(prs.slides)}"
print("Slide 2 Title:", prs.slides[1].shapes[2].text_frame.text[:50])
print("Slide 12 Title:", prs.slides[11].shapes[2].text_frame.text[:50])
print("Slide 31 Title:", prs.slides[30].shapes[2].text_frame.text[:50])

# 2. DOCX verification
for name, p in [("Standard", r"D:\Handover Thesis\Presentation\Thesis_Defence_Presentation_Script.docx"),
                ("Dense", r"D:\Handover Thesis\Presentation\Thesis_Defence_Presentation_Script_Dense.docx")]:
    doc = docx.Document(p)
    tbl = doc.tables[0]
    print(f"=== DOCX {name} VERIFICATION ===")
    print(f"Paragraphs: {len(doc.paragraphs)}, Tables: {len(doc.tables)}")
    print(f"Pacing table rows: {len(tbl.rows)} (Header + 37 slides)")
    assert len(tbl.rows) == 38, f"Expected 38 rows in pacing table, got {len(tbl.rows)}"
    total_sec = sum([int(r.cells[3].text.replace("s","")) for r in tbl.rows[1:]])
    print(f"Total duration: {total_sec} seconds = {total_sec // 60}:{total_sec % 60:02d}")

# 3. MD verification
for name, p in [("Standard", r"D:\Handover Thesis\Presentation\Defence-Script.md"),
                ("Dense", r"D:\Handover Thesis\Presentation\Defence-Script-Dense.md")]:
    with open(p, "r", encoding="utf-8") as f:
        lines = f.readlines()
    say_count = sum(1 for l in lines if l.startswith('> "'))
    words = sum(len(l.split()) for l in lines if l.startswith('> "'))
    print(f"=== MD {name} VERIFICATION ===")
    print(f"Total lines: {len(lines)}, Spoken SAY blocks: {say_count}, Spoken words: {words}")
    assert say_count == 37, f"Expected 37 SAY blocks, got {say_count}"
