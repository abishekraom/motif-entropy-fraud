# No-APC Venue Scan for `motif-entropy-fraud`

Date: 2026-06-29

Scope: venues that can plausibly accept a reproducible research-software / diagnostic-methods paper without mandatory Article Processing Charges (APCs). This scan distinguishes:

- **True diamond/platinum OA**: no fee for authors and no fee for readers.
- **Subscription/hybrid no-APC route**: no APC if the author chooses the traditional subscription route; open access would cost money.
- **Not immediate**: no-APC exists, but the current repo/paper needs a different format, maturity evidence, or a waiting period.

## Bottom line

The best no-APC alternatives are not exact clones of SoftwareX. The strongest practical route is:

1. **SoftwareX now** if APC can be paid / waived / institutionally covered.
2. **Journal of Statistical Software (JSS)** if we are willing to build a stricter statistical-software package, JSS-style paper, and one-hour exact replication script.
3. **JOSS later**, after at least six months of visible public development, releases, docs, issue history, and external impact.
4. **JMLR MLOSS / TMLR** only after reframing as ML software or a technically correct ML reproducibility/diagnostic paper.
5. **Subscription-route journals** if zero APC matters more than open access.

## Venue table

| Rank | Venue | APC status | Fit for this project | Immediate viability | Required changes / risk |
|---:|---|---|---|---|---|
| 1 | Journal of Statistical Software (JSS) | **No author fees or subscription fees**. | Medium-high if framed as statistical/reproducible audit software. | Not immediate. | Needs JSS LaTeX style, source code, replication materials, likely PyPI packaging, GPL-compatible license confirmation, and a standalone replication script expected to run within about one hour on a regular PC. Long and strict review. |
| 2 | Journal of Open Source Software (JOSS) | **Zero APC and zero subscription fees**. | High as a software package, but not for current immediate submission. | Not immediate. | 2026 JOSS requirements demand public open development history for at least six months, impact evidence, open issues/PRs, releases, and iterative public development. The repo was made public today, so immediate JOSS submission would be desk-rejection risk. |
| 3 | JMLR Machine Learning Open Source Software (MLOSS) | JMLR states no publication fees; MLOSS is open-source ML software track. | Medium if positioned as non-trivial ML/anomaly-surveillance software. | Not immediate. | Requires active user community, strong documentation, CI, near-complete tests, open development, comparison to related implementations, and JMLR 4-page software paper. Current project has no external user community yet. |
| 4 | Transactions on Machine Learning Research (TMLR) | **No fees or payments to authors/reviewers/editors** per TMLR editorial policy. | Medium if rewritten as a technically-correct ML reproducibility/diagnostic paper. | Possible later, not same paper. | TMLR is not a software-journal clone. It requires original ML contribution or reproducibility study; no overlap with archival submissions. Would need a separate anonymized OpenReview manuscript. |
| 5 | ReScience C | **Platinum OA: no author or reader fees**. | Low-medium only if pivoted to replication/reproduction of prior published work. | Not for current self-contained SoftwareX paper. | ReScience C is for computational replications/reproductions, usually of prior literature, and does not accept replication of one’s own research. Use only if we reproduce/replicate an existing p-adic/anomaly/fraud paper. |
| 6 | Journal of Systems and Software (Elsevier) | Subscription route: **no publication fee**; OA has APC. | Medium if reframed as software engineering / open science / reproducible research infrastructure. | Possible, but paper must be rewritten. | Needs full-length software-engineering evidence, not a short SoftwareX paper. Negative results and replication studies are in scope if important and well-supported. |
| 7 | Software: Practice and Experience (Wiley) | Author guidelines state **no page charges**; OA is optional and has APC. | Medium if framed as a practical software/system implementation and comparative analysis. | Possible later. | Very selective; official page reports 8% acceptance rate in extracted metrics. Needs stronger practical software-engineering lessons, not just a research artifact. |
| 8 | Journal of Computational Science (Elsevier) | Subscription route: no fee to authors; OA has APC. | Medium if framed as computational-science software for hierarchy-aware event-stream auditing. | Possible later. | Needs broader computational-science positioning and stronger software impact narrative. |
| 9 | Computational Statistics (Springer) | Hybrid journal; subscription route has **no APC**. | Medium if reframed as statistical software/methods for categorical event streams. | Possible later. | Needs statistics-style contribution, stronger methodological framing, and possibly more theory/diagnostic rigor. |
| 10 | Machine Learning (Springer) | Hybrid journal; subscription route has **no APC**. | Low-medium. | Possible only after major reframing. | Current evidence is diagnostic/fail-closed, not a new ML algorithm with strong empirical validation. Use only if we develop a strong ML-methods story. |
| 11 | Pattern Recognition (Elsevier) | Subscription route: **free/no fee**; OA APC listed separately. | Low for current evidence. | Not recommended now. | High-impact venue expecting original PR theory/method/application; current detector-superiority gates fail. Risk of rejection unless reframed with much stronger method contribution. |
| 12 | Expert Systems with Applications (Elsevier) | Subscription route: no publication fee; OA APC listed separately. | Low for current evidence. | Not recommended now. | Expects genuine intelligent-system innovation/application. Current fail-closed diagnostic software is better for SoftwareX/JSS/JOSS. |
| 13 | Computers & Security (Elsevier) | Subscription route: no publication fee; OA APC listed separately. | Low / avoid. | Not recommended. | The extracted journal page reports a moratorium on submissions where AI/ML is a significant component. Our project uses ML/anomaly/fraud-surveillance framing, so scope risk is high. |

## Evidence notes

- JSS author page: states no author fees or subscription fees; requires source code, replication material, JSS LaTeX, GPL/GPL-compatible license, and reproducible figures/tables.
- JOSS homepage/submission docs: states zero APC/subscription fees; 2026 scope requires sustained public open development, demonstrated impact, and open-source practices. A newly public repo is not enough.
- JMLR author page/search result: states no publication fees; MLOSS page requires OSI license, public repo, evidence of active user community, docs, tests, CI, and high-quality ML software.
- TMLR editorial policies: states no fees/payments; accepts technically correct ML papers and reproducibility studies, but not overlapping archival submissions.
- ReScience C FAQ: platinum OA; no author/reader fees; targets computational replication/reproduction, not ordinary software papers.
- Elsevier support: hybrid journals offer a subscription model where authors can publish for free; OA requires APC.
- Springer Nature support: hybrid journals allow subscription route with no APC; subscription-based journals usually have no charge, though color/page charges can apply.
- Wiley SPE author guidelines: no page charges; OA has APC if chosen.

## Recommended no-APC strategy

If APC is impossible, do **not** try to force the current SoftwareX paper unchanged into a random no-APC journal. Use one of these pivots:

1. **JSS pivot** — best scholarly no-APC target if we can make the software package and replication path very clean.
   - Add PyPI release.
   - Add exact `replicate_jss.py` / `replicate_jss.sh` that rebuilds all manuscript tables within one hour using curated artifacts and optional raw-data checks.
   - Convert manuscript to JSS style.
   - Keep MIT only if confirmed GPL-compatible enough for JSS; otherwise dual-license if needed.

2. **JOSS-later pivot** — best no-APC software venue after public history matures.
   - Keep repo public for 6+ months.
   - Add releases, changelog, contributing guide, issue templates, governance/support expectations, documentation site, and external usage evidence.
   - Prepare JOSS `paper.md` and `paper.bib` later.

3. **TMLR/JMLR pivot** — best no-APC ML route if we turn the failed detector story into a technical reproducibility/diagnostic ML contribution.
   - Separate from SoftwareX; avoid concurrent overlapping submissions.
   - Add stronger theory, ablations, broader datasets, and method-comparison narrative.

4. **Subscription-route journal pivot** — no APC, but paywalled.
   - Use Journal of Systems and Software / Journal of Computational Science / Computational Statistics depending on framing.
   - Must rewrite into a conventional full paper; not a SoftwareX-format paper.
