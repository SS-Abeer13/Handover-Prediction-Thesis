"""Build paper/references.tex from the thesis bibliography, in order of first citation in main.tex."""
import re
s = open('main.tex', encoding='utf-8').read()
keys = []
for m in re.finditer(r'\\cite\{([^}]*)\}', s):
    for k in m.group(1).split(','):
        k = k.strip()
        if k not in keys:
            keys.append(k)
ref = open('../latex/references.tex', encoding='utf-8').read()
items = dict(re.findall(r'\\bibitem\{(ref\d+)\}(.*?)(?=\n\s*\\bibitem|\n\\end\{thebibliography\})', ref, re.S))
out = ['\\begin{thebibliography}{%d}' % len(keys)]
for k in keys:
    b = items[k].strip()
    b = re.sub(r'\s*\[(Preprint; )?Row \d+ of Table~\\ref\{tab:D_1\}\.\]', '', b)
    out.append('\\bibitem{%s} %s\n' % (k, b))
out.append('\\end{thebibliography}')
open('references.tex', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print(len(keys), 'references')
