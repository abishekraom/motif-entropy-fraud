"""Initial reproducibility pipeline for the Q1 rebuild."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score

from motif_fraud.data.elliptic import load_elliptic
from motif_fraud.evaluation.claims import build_claim_table
from motif_fraud.evaluation.statistics import paired_permutation_p_value
from motif_fraud.features.egonet import extract_egonet_edges, local_degree_features
from motif_fraud.motifs.local import local_motif_features
from motif_fraud.nulls.local import er_edge_count_null

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATA_ROOT = PROJECT_ROOT / "data" / "elliptic_plusplus" / "elliptic_bitcoin_dataset"


def _ensure_dirs(output_root: Path) -> None:
    for subdir in ("tables", "metrics", "manifests"):
        (output_root / subdir).mkdir(parents=True, exist_ok=True)


def _write_table(df: pd.DataFrame, path: Path) -> None:
    df.to_csv(path, index=False)
    df.to_markdown(path.with_suffix(".md"), index=False)


def _balanced_labeled_centers(nodes: pd.DataFrame, sample_nodes: int, seed: int) -> pd.DataFrame:
    labeled = nodes[nodes["label"].isin(["licit", "illicit"])].copy()
    rng = np.random.default_rng(seed)
    groups = []
    per_class = max(1, sample_nodes // 2)
    for label in ("illicit", "licit"):
        group = labeled[labeled["label"] == label]
        take = min(per_class, len(group))
        idx = rng.choice(group.index.to_numpy(), size=take, replace=False)
        groups.append(group.loc[idx])
    sample = pd.concat(groups).sample(frac=1.0, random_state=seed).reset_index(drop=True)
    return sample.head(sample_nodes)


def _safe_auc(y_true: list[int], scores: list[float]) -> float:
    if len(set(y_true)) < 2:
        return float("nan")
    return float(roc_auc_score(y_true, scores))


def _safe_ap(y_true: list[int], scores: list[float]) -> float:
    if len(set(y_true)) < 2:
        return float("nan")
    return float(average_precision_score(y_true, scores))


def _center_feature_row(
    center: int,
    nodes: pd.DataFrame,
    edges: pd.DataFrame,
    null_permutations: int,
    seed: int,
) -> dict[str, Any]:
    time_cutoff = int(nodes.loc[nodes["tx_id"] == center, "time_step"].iloc[0])
    egonet = extract_egonet_edges(center, nodes, edges, hops=1, time_cutoff=time_cutoff)
    degree = local_degree_features(center, nodes, edges, hops=1, time_cutoff=time_cutoff)
    motifs = local_motif_features(egonet)
    motif_score = float(motifs["cycle_3_per_edge"] + motifs["chain_2_per_edge"])

    egonet_nodes = sorted(set(egonet["src"]).union(set(egonet["dst"]))) if not egonet.empty else [center]
    null_scores = []
    for i in range(null_permutations):
        null_edges = er_edge_count_null(egonet_nodes, len(egonet), seed=seed + i + int(center) % 100_000)
        null_motifs = local_motif_features(null_edges)
        null_scores.append(float(null_motifs["cycle_3_per_edge"] + null_motifs["chain_2_per_edge"]))
    null_mean = float(np.mean(null_scores)) if null_scores else 0.0

    row = {
        **degree,
        **motifs,
        "time_step": time_cutoff,
        "motif_score": motif_score,
        "er_null_motif_score": motif_score - null_mean,
        "er_null_mean": null_mean,
    }
    return row


def run_initial_local_audit(
    data_root: Path = DEFAULT_DATA_ROOT,
    sample_nodes: int = 1000,
    null_permutations: int = 8,
    seed: int = 13,
) -> dict[str, pd.DataFrame]:
    dataset = load_elliptic(data_root)
    centers = _balanced_labeled_centers(dataset.nodes, sample_nodes=sample_nodes, seed=seed)
    labels_by_id = dataset.nodes.set_index("tx_id")["label"].to_dict()

    rows = []
    for center in centers["tx_id"].astype(int):
        row = _center_feature_row(
            center=center,
            nodes=dataset.nodes,
            edges=dataset.edges,
            null_permutations=null_permutations,
            seed=seed,
        )
        row["label"] = labels_by_id[center]
        row["target_illicit"] = 1 if labels_by_id[center] == "illicit" else 0
        rows.append(row)
    features = pd.DataFrame(rows)

    y = features["target_illicit"].astype(int).tolist()
    baselines = pd.DataFrame(
        [
            {
                "dataset": "elliptic_bitcoin",
                "task": "sampled_local_node_ranking",
                "method": "center_total_degree",
                "auc": _safe_auc(y, (features["center_in_degree"] + features["center_out_degree"]).tolist()),
                "auprc": _safe_ap(y, (features["center_in_degree"] + features["center_out_degree"]).tolist()),
            },
            {
                "dataset": "elliptic_bitcoin",
                "task": "sampled_local_node_ranking",
                "method": "egonet_edge_count",
                "auc": _safe_auc(y, features["egonet_edges"].tolist()),
                "auprc": _safe_ap(y, features["egonet_edges"].tolist()),
            },
        ]
    )
    motif_auc = _safe_auc(y, features["er_null_motif_score"].tolist())
    motif_ap = _safe_ap(y, features["er_null_motif_score"].tolist())
    best_baseline = baselines.sort_values("auc", ascending=False).iloc[0]
    best_baseline_scores = (
        (features["center_in_degree"] + features["center_out_degree"]).tolist()
        if best_baseline["method"] == "center_total_degree"
        else features["egonet_edges"].tolist()
    )
    paired_p_value = paired_permutation_p_value(
        y,
        features["er_null_motif_score"].tolist(),
        best_baseline_scores,
        n_permutations=200,
        seed=seed,
    )
    motif_results = pd.DataFrame(
        [
            {
                "dataset": "elliptic_bitcoin",
                "task": "sampled_local_node_ranking",
                "method": "er_null_local_motif_score",
                "auc": motif_auc,
                "auprc": motif_ap,
                "best_simple_baseline": best_baseline["method"],
                "best_simple_baseline_auc": float(best_baseline["auc"]),
                "delta_vs_best_simple_baseline": float(motif_auc - best_baseline["auc"]),
                "paired_permutation_p_value": paired_p_value,
                "sample_nodes": int(len(features)),
                "null_permutations": int(null_permutations),
            }
        ]
    )
    claims = build_claim_table(
        [
            {
                "dataset": "elliptic_bitcoin",
                "task": "sampled_local_node_ranking",
                "method": "er_null_local_motif_score",
                "method_auc": motif_auc,
                "best_simple_baseline": best_baseline["method"],
                "best_simple_baseline_auc": float(best_baseline["auc"]),
                "paired_delta": float(motif_auc - best_baseline["auc"]),
                "paired_p_value": paired_p_value,
                "validation_scope": "single_dataset_smoke_sample",
            }
        ]
    )
    summary = pd.DataFrame([dataset.summary()]).drop(columns=["label_counts"])
    label_counts = dataset.summary()["label_counts"]
    for key, value in label_counts.items():
        summary[f"label_{key}"] = value

    return {
        "dataset_summary": summary,
        "local_features": features,
        "simple_baselines": baselines,
        "local_motif_null_results": motif_results,
        "claim_table": claims,
    }


def reproduce_all(
    output_root: str | Path = "outputs",
    sample_nodes: int = 1000,
    null_permutations: int = 8,
    seed: int = 13,
) -> dict[str, Any]:
    output_root = Path(output_root)
    _ensure_dirs(output_root)
    # Initial rebuild validation is a smoke-scale local audit. Full-scale sampling will be
    # added after the data contracts, egonet cache, and external dataset cards are locked.
    effective_sample_nodes = min(sample_nodes, 100)
    tables = run_initial_local_audit(
        sample_nodes=effective_sample_nodes,
        null_permutations=null_permutations,
        seed=seed,
    )

    artifact_paths = {
        "dataset_summary": output_root / "tables" / "table1_dataset_summary.csv",
        "simple_baselines": output_root / "tables" / "table2_simple_baselines.csv",
        "local_motif_null_results": output_root / "tables" / "table3_local_motif_null_results.csv",
        "claim_table": output_root / "tables" / "table4_claim_discipline.csv",
    }
    _write_table(tables["dataset_summary"], artifact_paths["dataset_summary"])
    _write_table(tables["simple_baselines"], artifact_paths["simple_baselines"])
    _write_table(tables["local_motif_null_results"], artifact_paths["local_motif_null_results"])
    _write_table(tables["claim_table"], artifact_paths["claim_table"])
    tables["local_features"].to_csv(output_root / "metrics" / "sampled_local_features.csv", index=False)

    manifest = {
        "phase": "q1_rebuild_initial_local_audit",
        "parameters": {
            "sample_nodes": int(sample_nodes),
            "effective_sample_nodes": int(effective_sample_nodes),
            "null_permutations": int(null_permutations),
            "seed": int(seed),
        },
        "artifacts": {key: str(path) for key, path in artifact_paths.items()},
    }
    manifest_path = output_root / "manifests" / "rebuild_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def main() -> None:
    manifest = reproduce_all()
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
