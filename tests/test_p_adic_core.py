import pandas as pd
import pytest

from motif_fraud.p_adic.encoding import HierarchySpec, encode_frame, randomize_digit_maps
from motif_fraud.p_adic.metrics import is_prime, next_prime_at_least, p_adic_distance, p_adic_valuation


def test_p_adic_valuation_and_distance_follow_number_theory_definitions():
    assert p_adic_valuation(0, 3) == pytest.approx(float("inf"))
    assert p_adic_valuation(27, 3) == 3
    assert p_adic_valuation(28, 3) == 0
    assert p_adic_distance(10, 19, 3) == pytest.approx(1 / 9)
    assert p_adic_distance(10, 11, 3) == pytest.approx(1.0)


def test_prime_selection_is_explicit_and_validated():
    assert is_prime(2)
    assert is_prime(11)
    assert not is_prime(1)
    assert not is_prime(9)
    assert next_prime_at_least(6) == 7
    with pytest.raises(ValueError):
        p_adic_distance(1, 2, 4)


def test_encoding_preserves_coarse_to_fine_hierarchy_and_returns_audit_maps():
    frame = pd.DataFrame(
        {
            "product": ["digital", "digital", "travel"],
            "network": ["visa", "visa", "visa"],
            "device": ["mobile", "desktop", "mobile"],
        }
    )
    spec = HierarchySpec(name="ieee_like", columns=("product", "network", "device"), prime=3)

    encoded = encode_frame(frame, spec)

    assert encoded.codes.tolist() == [0, 9, 1]
    assert encoded.digit_maps["product"]["digital"] == 0
    assert encoded.digit_maps["product"]["travel"] == 1
    assert encoded.digit_maps["device"]["mobile"] == 0
    assert encoded.digit_maps["device"]["desktop"] == 1
    # Differing at the finest level is closer than differing at the root.
    assert p_adic_distance(encoded.codes[0], encoded.codes[1], 3) == pytest.approx(1 / 9)
    assert p_adic_distance(encoded.codes[0], encoded.codes[2], 3) == pytest.approx(1.0)


def test_randomized_digit_map_control_keeps_categories_but_changes_digit_assignments():
    frame = pd.DataFrame(
        {
            "product": ["digital", "digital", "travel", "retail"],
            "device": ["mobile", "desktop", "mobile", "tablet"],
        }
    )
    spec = HierarchySpec(name="control", columns=("product", "device"), prime=5)
    encoded = encode_frame(frame, spec)
    randomized_maps = randomize_digit_maps(encoded.digit_maps, seed=7)
    randomized = encode_frame(frame, spec, digit_maps=randomized_maps)

    assert set(randomized.digit_maps["product"]) == set(encoded.digit_maps["product"])
    assert randomized.codes.tolist() != encoded.codes.tolist()
