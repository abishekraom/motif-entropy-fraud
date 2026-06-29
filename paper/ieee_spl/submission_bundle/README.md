# IEEE SPL submission bundle

This bundle contains the compiled draft PDF, LaTeX source, BibTeX references, claim audit, key result tables, reproduction plan, and compile status.

Main PDF: `p_adic_prefix_rarity_spl.pdf`

Brutal claim boundary: the p-adic signal survives hierarchy/flat-rarity controls but is not competitive as a standalone detector against LightGBM/CatBoost/XGBoost.

Reproduce from repository root:

```bash
pytest -q
python -m motif_fraud.p_adic.reproduce_all --skip-tests
cd paper/ieee_spl && tectonic p_adic_prefix_rarity_spl.tex
```

Verified state at bundle creation:

- Tectonic 0.16.9 compiled the PDF.
- PDF pages: 3.
- Full tests: 44 passed.
- Reproduction runner: all artifact checks passed.
