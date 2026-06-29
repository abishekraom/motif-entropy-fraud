"""Dataset provenance contracts for the p-adic fraud pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DatasetCard:
    """Minimal audit card for a real benchmark dataset."""

    name: str
    source_type: str
    official_url: str
    local_paths: tuple[str, ...]
    target_column: str
    temporal_column: str | None
    allowed_for_primary_claims: bool
    leakage_columns: tuple[str, ...] = ()
    notes: str = ""


@dataclass(frozen=True)
class DatasetValidation:
    """Validation result for manuscript claim eligibility."""

    name: str
    is_valid_for_primary_claims: bool
    reasons: tuple[str, ...]
    missing_paths: tuple[str, ...]


def validate_real_dataset_card(card: DatasetCard, project_root: str | Path = ".") -> DatasetValidation:
    """Validate whether a dataset card is eligible for primary non-synthetic claims."""
    reasons: list[str] = []
    missing_paths: list[str] = []
    source_type = card.source_type.strip().lower()
    if source_type in {"synthetic", "simulated", "simulation"}:
        reasons.append("synthetic_or_simulated_dataset_not_allowed_for_primary_claims")
    if not card.official_url.startswith(("https://", "http://")):
        reasons.append("missing_official_url")
    if not card.target_column:
        reasons.append("missing_target_column")
    if not card.allowed_for_primary_claims:
        reasons.append("card_disallows_primary_claims")
    root = Path(project_root)
    for local_path in card.local_paths:
        if not (root / local_path).exists():
            missing_paths.append(local_path)
    if missing_paths:
        reasons.append("local_dataset_files_missing")
    return DatasetValidation(
        name=card.name,
        is_valid_for_primary_claims=not reasons,
        reasons=tuple(reasons),
        missing_paths=tuple(missing_paths),
    )
