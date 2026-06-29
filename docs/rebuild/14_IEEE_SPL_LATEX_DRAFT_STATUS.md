# IEEE SPL LaTeX draft status

Date: 2026-06-08

## What was completed

A claim-safe IEEE SPL-style LaTeX manuscript draft and BibTeX reference file were created.

Manuscript:

`paper/ieee_spl/p_adic_prefix_rarity_spl.tex`

References:

`paper/ieee_spl/references.bib`

Test:

`tests/test_ieee_spl_manuscript_draft.py`

## Draft title

Non-Archimedean Prefix-Rarity Signals for Temporal Fraud Surveillance

## Draft status

This is a structured IEEE SPL-style draft, not a compiled submission PDF yet.

It includes:

- abstract;
- IEEE keywords;
- introduction and related positioning;
- method equations;
- experimental setup;
- IEEE-CIS control table;
- broader baseline table;
- external validation paragraph;
- figure inclusions for 600 dpi figures;
- limitations;
- conclusion;
- BibTeX references.

## Claim safety

The draft explicitly states:

> p-adic prefix-rarity is an interpretable complementary temporal categorical signal, not a universal standalone fraud detector.

The draft avoids the unsafe claim that the method is a state-of-the-art fraud detector.

## Verification commands run

```bash
pytest tests/test_ieee_spl_manuscript_draft.py -q
```

Result:

```text
1 passed
```

```bash
pytest -q
```

Result:

```text
43 passed
```

Citation sanity check:

- cited keys found: 10
- missing cited BibTeX keys: 0
- brace balance delta: 0

## LaTeX compile status

Blocked in this environment because no LaTeX engine is installed on PATH:

- `pdflatex`: missing
- `latexmk`: missing
- `tectonic`: missing

Therefore, I could validate source structure, citations, tests, and artifact paths, but I could not compile a PDF locally.

## Next concrete step

Install or provide one LaTeX engine, preferably Tectonic or TeX Live/MiKTeX, then run a real PDF build.

Recommended command if Tectonic is installed:

```bash
cd paper/ieee_spl && tectonic p_adic_prefix_rarity_spl.tex
```

Recommended command if TeX Live/MiKTeX is installed:

```bash
cd paper/ieee_spl && pdflatex p_adic_prefix_rarity_spl.tex && bibtex p_adic_prefix_rarity_spl && pdflatex p_adic_prefix_rarity_spl.tex && pdflatex p_adic_prefix_rarity_spl.tex
```

## Current project level

The project is now approximately **91% complete** for an IEEE SPL submission package.

Completed:

- official IEEE-CIS primary audit;
- broader baselines;
- complementarity result;
- external validation;
- 600 dpi figures;
- claim audit;
- literature positioning;
- reproduction runner;
- IEEE-style LaTeX draft;
- 43 passing tests.

Still missing:

1. compiled PDF;
2. final IEEE formatting pass after compilation;
3. final caption/spacing polish;
4. optional stronger external benchmark if reviewer risk needs further reduction.

## Brutal caveat retained

The draft must keep the central caveat:

Raw p-adic does not beat supervised logistic frequency baseline on IEEE-CIS. The publishable claim is interpretability, hierarchy-aware signal structure, and complementarity, not detector superiority.
