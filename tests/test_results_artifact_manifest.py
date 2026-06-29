import json
from pathlib import Path


MANIFEST = Path("results/artifact_manifest.json")


def test_curated_artifact_manifest_paths_and_byte_counts_match_files():
    rows = json.loads(MANIFEST.read_text(encoding="utf-8"))

    assert rows
    for row in rows:
        result_path = Path(row["result_path"])
        assert row["copied"] is True
        assert result_path.exists(), result_path
        assert result_path.is_file(), result_path
        expected_bytes = int(row["bytes"])
        raw = result_path.read_bytes()
        candidate_sizes = {len(raw)}
        if b"\n" in raw:
            candidate_sizes.add(len(raw.replace(b"\r\n", b"\n")))
            candidate_sizes.add(len(raw.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")))
        assert expected_bytes in candidate_sizes, result_path
