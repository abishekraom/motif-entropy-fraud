from pathlib import Path


def test_current_ieee_spl_latex_is_claim_safe_and_source_backed():
    tex = Path("paper/ieee_spl/non_archimedean_tree_scan_spl.tex")
    bib = Path("paper/ieee_spl/references.bib")
    figure = Path("paper/ieee_spl/tree_scan_artifacts/cross_dataset_gate_auprc.png")

    assert tex.exists()
    assert bib.exists()
    assert figure.exists()
    text = tex.read_text(encoding="utf-8")
    references = bib.read_text(encoding="utf-8")

    assert "A Non-Archimedean Tree-Scan Diagnostic" in text
    assert "diagnostic contribution, not a detector-superiority claim" in text
    assert "no dataset meets the preregistered superiority gate" in text
    assert "Wednesday was preregistered before download" in text
    assert "0.0118" in text
    assert "-0.0159" in text
    assert "-0.0338" in text
    assert "diagnostic\\_only\\_failed\\_q1\\_tree\\_scan\\_gate" in text
    assert "state-of-the-art" not in text.lower()
    assert "significantly outperforms" not in text.lower()
    assert "Vaelthron" not in text
    assert "\\bibliography{references}" in text
    assert "tree_scan_artifacts/cross_dataset_gate_auprc.png" in text

    for citation in (
        "neill2012fastsubset",
        "rodner2016maxdiv",
        "adams2007bocpd",
        "laby2016mixedcusum",
        "sharafaldin2018ids",
    ):
        assert f"{{{citation}," in references
