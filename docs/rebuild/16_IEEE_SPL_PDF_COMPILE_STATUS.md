# IEEE SPL PDF compile and finalization status

Date: 2026-06-09

## Completed in this pass

The missing LaTeX toolchain blocker was removed and the IEEE SPL manuscript now compiles to PDF.

## Toolchain installed

Installed Tectonic locally under the user bin directory:

- `C:/Users/Abishek Rao M/bin/tectonic.exe`
- version: `Tectonic 0.16.9`

Verification:

```bash
command -v tectonic
tectonic --version
```

Observed:

```text
/c/Users/Abishek Rao M/bin/tectonic
Tectonic 0.16.9
```

Also installed `pypdf` in the active Python 3.13 environment for PDF page-count verification.

## Manuscript compiled

Source:

`paper/ieee_spl/p_adic_prefix_rarity_spl.tex`

References:

`paper/ieee_spl/references.bib`

Compiled PDF:

`paper/ieee_spl/p_adic_prefix_rarity_spl.pdf`

Compile command:

```bash
cd paper/ieee_spl
tectonic p_adic_prefix_rarity_spl.tex
```

Result:

- exit code: 0
- PDF size: 920,625 bytes
- pages: 3
- page size: 612 x 792 pt for all pages

## Warnings fixed

Initial compile exposed:

- overfull hbox in the long selected-hierarchy equation;
- overfull hbox in the first results table;
- BibTeX warnings for empty authors/journals in several references.

Fixes applied:

- converted the selected hierarchy from a long display equation into inline text;
- shortened the first table labels (`R@1%FPR`, `Flat rarity`, `Digit-map check`);
- filled missing BibTeX authors/journal metadata using DOI/Crossref and arXiv metadata.

Final compile warning state:

- no overfull boxes reported;
- no BibTeX empty-author/empty-journal warnings reported;
- remaining warning: underfull hbox in title/author block at line 15. This is visually/layout-minor and common in title blocks, but should still be checked visually before submission.

## Test and reproduction verification

Full test suite:

```bash
pytest -q
```

Result:

```text
44 passed
```

Artifact reproduction:

```bash
python -m motif_fraud.p_adic.reproduce_all --skip-tests
```

Result:

```text
[reproduce] all artifact checks passed
```

This reran/checks:

1. official IEEE-CIS p-adic audit;
2. logistic/IsolationForest baseline context;
3. 600 dpi official IEEE-CIS publication figures;
4. LightGBM/CatBoost/XGBoost strong baseline audit;
5. vehicle-claim external validation;
6. claim audit.

## Visual PDF inspection

Rendered all 3 pages to images and inspected the combined page rendering.

Visual QA result:

- no blank pages;
- no content cut off;
- no obvious table overflow;
- no figure overflow;
- captions are present and attached to the intended figures;
- page 2/3 float placement is dense but usable for a draft;
- figures are readable enough at page scale, though final submission could still benefit from caption/label polish.

The temporary rendered page images were removed after inspection.

## Cleanup performed

Removed temporary install/build artifacts:

- `/tmp/tectonic-install`
- `/tmp/tectonic_compile.log`
- `/tmp/tectonic_compile2.log`
- local LaTeX `.aux`, `.blg`, `.log` files

Kept final deliverables:

- `.tex`
- `references.bib`
- compiled `.pdf`
- result artifacts under `outputs/`
- status docs under `docs/rebuild/`

## Skill saved

Created reusable Hermes skill:

`ieee-spl-reproducible-latex-package`

Purpose:

- install/verify LaTeX toolchain;
- compile IEEE SPL-style draft;
- inspect warnings;
- verify PDF;
- run reproduction/tests;
- clean temp files;
- maintain claim discipline.

## Current project level

The project has now moved from "blocked on LaTeX compilation" to:

**compiled IEEE SPL draft package with verified reproducible artifacts.**

Brutal status:

- The submission package exists as source + PDF.
- The empirical story remains narrow because raw p-adic is far below LightGBM/CatBoost/XGBoost.
- The paper is viable only as an interpretable non-Archimedean categorical signal/control-discipline letter, not as a detector-superiority paper.

## Remaining before actual submission

1. Visual PDF inspection page-by-page.
2. Final IEEE SPL author/affiliation cleanup.
3. Final caption/table spacing polish if visual inspection reveals issues.
4. Decide whether to submit this narrow story to IEEE SPL or retarget to a more suitable anomaly/interpretable-ML venue.
