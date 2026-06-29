#!/usr/bin/env python3
"""Minimal SoftwareX readiness checker for motif-entropy-fraud.

ponytail: stdlib-only checks; this is a gatekeeper, not a full linter.
"""
from __future__ import annotations
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper/softwarex/motif_entropy_fraud_softwarex.tex"
HIGHLIGHTS = ROOT / "paper/softwarex/highlights.txt"

required = [
    "README.md",
    "LICENSE.txt",
    "CITATION.cff",
    "src/motif_fraud",
    "pyproject.toml",
    "paper/softwarex/softwarex-osp-template.tex",
    "paper/softwarex/motif_entropy_fraud_softwarex.tex",
    "paper/softwarex/highlights.txt",
    "paper/softwarex/ai_disclosure.md",
    "paper/softwarex/competing_interests.md",
    "docs/softwarex/softwarex_requirements_audit.md",
    "docs/softwarex/scope_fit_decision.md",
    "docs/softwarex/claim_provenance_audit.md",
    "docs/softwarex/data_availability_statement.md",
    "docs/softwarex/verification_log.md",
]

errors, warnings, metrics = [], [], {}
for rel in required:
    if not (ROOT / rel).exists():
        errors.append(f"missing required path: {rel}")

if PAPER.exists():
    tex = PAPER.read_text(encoding="utf-8", errors="ignore")
    abs_m = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", tex, re.S)
    abstract = abs_m.group(1) if abs_m else ""
    abstract_words = re.findall(r"[A-Za-z0-9_'-]+", re.sub(r"\\[a-zA-Z]+", " ", abstract))
    metrics["abstract_words"] = len(abstract_words)
    if not abs_m:
        errors.append("abstract environment missing")
    elif len(abstract_words) > 250:
        errors.append(f"abstract exceeds 250 words: {len(abstract_words)}")

    key_m = re.search(r"\\begin\{keyword\}(.*?)\\end\{keyword\}", tex, re.S)
    keywords = [k.strip() for k in key_m.group(1).split(r"\sep")] if key_m else []
    keywords = [k for k in keywords if k and not k.startswith("%%")]
    metrics["keywords"] = len(keywords)
    if not 1 <= len(keywords) <= 7:
        errors.append(f"keyword count must be 1-7, found {len(keywords)}")

    fig_count = tex.count(r"\includegraphics")
    metrics["figures"] = fig_count
    if fig_count > 6:
        errors.append(f"figure count exceeds 6: {fig_count}")

    # Approximate manuscript word count, excluding metadata table and bibliography is hard in TeX;
    # this conservative count strips commands and counts full body text.
    body = re.sub(r"\\begin\{thebibliography\}.*?\\end\{thebibliography\}", " ", tex, flags=re.S)
    body = re.sub(r"\\[a-zA-Z*]+(?:\[[^\]]*\])?(?:\{[^{}]*\})?", " ", body)
    words = re.findall(r"[A-Za-z0-9_'-]+", body)
    metrics["approx_total_tex_words"] = len(words)
    if len(words) > 4000:
        errors.append(f"approximate TeX word count exceeds 4000: {len(words)}")

    required_sections = [
        "Motivation and significance",
        "Software description",
        "Illustrative examples",
        "Impact",
        "Conclusions",
    ]
    for section in required_sections:
        if section not in tex:
            errors.append(f"missing required SoftwareX section: {section}")

    if "TO_BE_PUBLIC_GITHUB_URL_BEFORE_SUBMISSION" in tex or "TO\\_BE\\_PUBLIC\\_GITHUB" in tex:
        errors.append("public GitHub URL placeholder remains; SoftwareX submission blocked")
    if "TODO:" in tex:
        warnings.append("TODO markers remain in manuscript")

if HIGHLIGHTS.exists():
    lines = [l.strip("-• ").strip() for l in HIGHLIGHTS.read_text(encoding="utf-8").splitlines() if l.strip()]
    metrics["highlights"] = len(lines)
    if not 3 <= len(lines) <= 5:
        errors.append(f"highlights must contain 3-5 bullets, found {len(lines)}")
    too_long = [(i + 1, len(line), line) for i, line in enumerate(lines) if len(line) > 85]
    for i, n, line in too_long:
        errors.append(f"highlight {i} exceeds 85 chars ({n}): {line}")

lic = ROOT / "LICENSE.txt"
if lic.exists() and "MIT License" not in lic.read_text(encoding="utf-8", errors="ignore"):
    warnings.append("LICENSE.txt exists but is not detected as MIT; verify OSI-approved license")

result = {
    "status": "BLOCKED" if errors else "PASS",
    "errors": errors,
    "warnings": warnings,
    "metrics": metrics,
}
print(json.dumps(result, indent=2))
(ROOT / "docs/softwarex/final_readiness_audit.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
raise SystemExit(1 if errors else 0)
