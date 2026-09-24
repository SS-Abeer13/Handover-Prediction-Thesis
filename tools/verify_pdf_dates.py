import pypdf, re

reader = pypdf.PdfReader('latex/main.pdf')
date_patterns = [
    r'\b10\s*Sept', r'\b12\s*Sept', r'\b13\s*Sept', r'\b15\s*Sept',
    r'Sept(?:ember)?\s*10\b', r'Sept(?:ember)?\s*12\b', r'Sept(?:ember)?\s*13\b', r'Sept(?:ember)?\s*15\b',
    r'10th\s*of\s*Sept', r'12th\s*of\s*Sept', r'13th\s*of\s*Sept', r'15th\s*of\s*Sept'
]

found = False
for idx, page in enumerate(reader.pages, 1):
    text = page.extract_text() or ''
    for pat in date_patterns:
        m = re.search(pat, text, re.I)
        if m:
            print(f"Page {idx}: Found date '{m.group(0)}' in: {text[max(0, m.start()-40):min(len(text), m.end()+40)]}")
            found = True

if not found:
    print(f"SUCCESS: Zero calendar dates found across all {len(reader.pages)} pages of main.pdf!")
