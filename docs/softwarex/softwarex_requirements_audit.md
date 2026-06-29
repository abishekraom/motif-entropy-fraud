# SoftwareX Requirements Audit

Date: 2026-06-29
Target: SoftwareX Original Software Publication
Project root: `D:/motif-entropy-fraud/motif-entropy-fraud`

## Authoritative sources checked

| Source | URL | Requirement extracted |
|---|---|---|
| SoftwareX homepage | https://www.sciencedirect.com/journal/softwarex | SoftwareX publishes software articles; submissions consist of a short descriptive paper and open-source software distribution. Metrics found: Impact Factor 1.9, CiteScore 3.9, APC USD 1560 excluding taxes. |
| SoftwareX Guide for Authors | https://www.sciencedirect.com/journal/softwarex/publish/guide-for-authors | 4000-word limit, mandatory journal template, open-source GitHub repository, README.md, LICENSE.txt, source in `src/`, highlights, data statement, AI disclosure if used, declarations. |
| Elsevier SoftwareX guide mirror | https://www.elsevier.com/journals/softwarex/2352-7110/guide-for-authors | Confirms public GitHub requirement, OSI license, metadata table, template sections, 6 figure limit. |
| SoftwareX template | https://legacyfileshare.elsevier.com/promis_misc/softwarex-osp-template.tex | Template states five required main sections and says missing GitHub README/License can cause return/rejection. |
| SoftwareX OA options | https://www.sciencedirect.com/journal/softwarex/publish/open-access-options | APC USD 1560; open access licenses CC BY / CC BY-NC / CC BY-NC-ND for the article. |

## Requirements checklist

| Requirement | Current status | Evidence / action |
|---|---|---|
| Article type is Original Software Publication | PASS-PREP | Draft uses SoftwareX Original Software Publication template. |
| Manuscript uses SoftwareX template | PASS-PREP | `paper/softwarex/softwarex-osp-template.tex` downloaded; draft at `paper/softwarex/motif_entropy_fraud_softwarex.tex`. |
| Manuscript <= 4000 words | TO VERIFY | Checked by `scripts/softwarex_readiness_check.py`. |
| Abstract <= 250 words | TO VERIFY | Checked by readiness script. |
| Figures <= 6 | TO VERIFY | Draft currently uses no embedded figures; figures can be added later if needed. |
| 1-7 keywords | TO VERIFY | Checked by readiness script. |
| 3-5 highlights <= 85 chars each | TO VERIFY | `paper/softwarex/highlights.txt`; checked by readiness script. |
| Open-source software distribution | PASS-PREP / SUBMISSION-BLOCKED | Local repo prepared; actual SoftwareX submission still needs public GitHub. |
| Public GitHub URL in metadata table | PASS-PREP | Target public GitHub URL set to `https://github.com/abishekraom/motif-entropy-fraud`; must be verified after push. |
| README.md explains use, installation, purpose | PASS-PREP | `README.md` exists and is claim-safe; may need final public-facing polish. |
| LICENSE.txt with OSI-approved license | PASS-PREP | Added MIT `LICENSE.txt`; author should confirm license choice before public release. |
| Source in `src/` | PASS | `src/motif_fraud/` exists. |
| Data statement | PASS-PREP | `docs/softwarex/data_availability_statement.md` and manuscript section. |
| Generative AI disclosure | PASS-PREP | Draft includes disclosure before references. User/author must review before submission. |
| Competing interests/declarations | PASS-PREP | Draft includes declaration placeholder; Elsevier declaration form still required at submission. |
| Editable source file, not PDF-only | PASS | `.tex` draft exists. |
| Claims fact-backed | PASS-PREP | `docs/softwarex/claim_provenance_audit.md` maps claims to artifacts/commands. |

## Immediate blocker

SoftwareX requires a public GitHub repository for actual submission. The target public repository has been assigned; verify it resolves after push before submission:

```text
LOCALLY_PREPARED_PUBLIC_GITHUB_URL_ASSIGNED_VERIFY_AFTER_PUSH
```

This is not optional or a preference; it is a SoftwareX guide/template requirement.
