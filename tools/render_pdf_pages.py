import fitz, os

doc = fitz.open('latex/main.pdf')
out_dir = r"C:\Users\Abeer\.gemini\antigravity\brain\b7bc5a13-623f-4b00-a8fa-6bc24903f90b\.tempmediaStorage"
os.makedirs(out_dir, exist_ok=True)

pages_to_render = [1, 6, 73, 74]
for p_num in pages_to_render:
    page = doc[p_num - 1]
    pix = page.get_pixmap(dpi=150)
    out_path = os.path.join(out_dir, f"page_{p_num}.png")
    pix.save(out_path)
    print(f"Saved page {p_num} to {out_path}")
