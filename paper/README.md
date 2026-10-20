# Journal manuscript ("Paper B")

`main.tex` is the journal version of the thesis. It is reframed around the timestamp-alignment audit, and the target journal is *Computer Communications* (Elsevier); *Computer Networks* also works without changes.

## Build

```
pdflatex main && pdflatex main
```

- The default class line is the two-column 5p layout. It gives about 11 pages of article plus a highlights page.
- Most Elsevier submission systems want the single-column review layout instead. To get it, change the class line to `\documentclass[preprint,review,12pt]{elsarticle}`.
- `references.tex` is generated from `../latex/references.tex`. Regenerate it with `python make_refs.py` after adding or removing a `\cite`. It lists the references in order of first citation.

## Submission package (Computer Communications, Editorial Manager)

| Upload as | File |
|---|---|
| Manuscript (PDF for reviewers) | `main_review.pdf` (single column, line numbers) |
| LaTeX source | `submission_source.zip` (main.tex, references.tex, figures/) |
| Highlights | `highlights.docx` (5 bullets, each at most 85 characters) |
| Cover letter | `cover_letter.docx` (add the date before uploading) |
| Data statement | Zenodo, doi:10.5281/zenodo.23479562 |

- The abstract is 248 words, within the 250-word limit. There are 7 keywords, within the limit of 1 to 7.
- On 20 Oct 2026 every reference was checked against Crossref, DataCite, arXiv or PMLR.
- `main.pdf` is the two-column 5p layout, for reading. Rebuild the review copy from `main.tex` with the class line `\documentclass[preprint,review,12pt]{elsarticle}` and `\linenumbers`.
