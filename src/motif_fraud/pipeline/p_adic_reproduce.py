"""Reproducibility manifest for p-adic Q1-candidate experiments."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REQUIRED_NEGATIVE_CONTROLS = {"random_digit_map", "random_hierarchy", "flat_categorical"}
MINIMUM_FIGURE_DPI = 600


def build_q1_manifest(artifacts: dict[str, Any], output_path: str | Path) -> dict[str, Any]:
    """Write a manifest only when core Q1 reproducibility controls are registered."""
    negative_controls = set(artifacts.get("negative_controls", []))
    missing_controls = sorted(REQUIRED_NEGATIVE_CONTROLS - negative_controls)
    if missing_controls:
        raise ValueError(f"Missing required negative controls: {missing_controls}")
    figures = artifacts.get("figures", [])
    if figures and min(int(figure.get("dpi", 0)) for figure in figures) < MINIMUM_FIGURE_DPI:
        raise ValueError("All registered raster figures must be at least 600 dpi")
    if not artifacts.get("dataset_cards"):
        raise ValueError("At least one dataset card must be registered")
    if not artifacts.get("claims_table"):
        raise ValueError("A claims table artifact must be registered")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        "quality_gate": "q1_research_grade_candidate",
        "required_negative_controls_present": sorted(negative_controls & REQUIRED_NEGATIVE_CONTROLS),
        "minimum_figure_dpi": MINIMUM_FIGURE_DPI,
        "artifacts": artifacts,
    }
    output_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    manifest["manifest_path"] = str(output_path)
    return manifest
