import glob, re

issues = 0
for f in sorted(glob.glob('latex/**/*.tex')):
    with open(f, 'r', encoding='utf-8') as fp:
        lines = fp.readlines()
    for idx, l in enumerate(lines, 1):
        # 1. odd $ count
        dollars = re.findall(r'(?<!\\)\$', l)
        if len(dollars) % 2 != 0:
            print(f"{f}:{idx} [ODD $]: {l.strip()[:80]}")
            issues += 1
        # 2. unescaped %
        # skip comment lines
        if not l.strip().startswith('%'):
            for m in re.finditer(r'(?<!\\)%', l):
                before = l[:m.start()]
                if any(c.isalnum() for c in before):
                    print(f"{f}:{idx} [UNESCAPED %]: {l.strip()[:80]}")
                    issues += 1
        # 3. ^ outside $
        # remove $...$ and check if ^ remains
        stripped = re.sub(r'\$.*?\$', '', l)
        stripped = re.sub(r'\\begin\{equation\}.*?\\end\{equation\}', '', stripped)
        if '^' in stripped and not stripped.strip().startswith('%'):
            print(f"{f}:{idx} [CARET OUTSIDE MATH]: {l.strip()[:80]}")
            issues += 1

if issues == 0:
    print("ALL TEX FILES PASSED VALIDATION PERFECTLY!")
else:
    print(f"Total issues found: {issues}")
