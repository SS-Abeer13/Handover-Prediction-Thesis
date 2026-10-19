# Journal manuscript ("Paper B")

`main.tex` is the journal version of the thesis. It is reframed around the timestamp-alignment audit, and the target journal is *Computer Communications* (Elsevier); *Computer Networks* also works without changes.

## Build

```
pdflatex main && pdflatex main
```

- The default class line is the two-column 5p layout. It gives about 11 pages of article plus a highlights page.
- Most Elsevier submission systems want the single-column review layout instead. To get it, change the class line to `\documentclass[preprint,review,12pt]{elsarticle}`.
- `references.tex` is generated from `../latex/references.tex`. Regenerate it with `python make_refs.py` after adding or removing a `\cite`. It lists the references in order of first citation.

## Before submission

- Replace `zenodo.XXXXXXX` in *Data and code availability* with the DOI that the v1.0.0 release mints.
- Add the corresponding author's e-mail with `\ead{...}` under his `\author` line.
- Check the CRediT roles. They are a draft based on the thesis division of work.
- Keep or reword the generative-AI declaration. Elsevier requires one if AI tools were used in writing.
- Use the journal's reference style if the guide asks for one other than `elsarticle-num`.
