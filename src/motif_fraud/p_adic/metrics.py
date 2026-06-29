"""Number-theoretic p-adic metric primitives."""

from __future__ import annotations

import math


def is_prime(value: int) -> bool:
    """Return True when *value* is prime."""
    if value < 2:
        return False
    if value == 2:
        return True
    if value % 2 == 0:
        return False
    limit = int(math.sqrt(value)) + 1
    for divisor in range(3, limit, 2):
        if value % divisor == 0:
            return False
    return True


def next_prime_at_least(value: int) -> int:
    """Smallest prime >= value."""
    candidate = max(2, int(value))
    while not is_prime(candidate):
        candidate += 1
    return candidate


def _require_prime(p: int) -> None:
    if not is_prime(p):
        raise ValueError(f"p must be prime, got {p!r}")


def p_adic_valuation(value: int, p: int) -> float:
    """Return v_p(value), with v_p(0)=infinity."""
    _require_prime(p)
    value = abs(int(value))
    if value == 0:
        return float("inf")
    valuation = 0
    while value % p == 0:
        valuation += 1
        value //= p
    return float(valuation)


def p_adic_norm(value: int, p: int) -> float:
    """Return |value|_p = p^-v_p(value)."""
    valuation = p_adic_valuation(value, p)
    if math.isinf(valuation):
        return 0.0
    return float(p ** (-int(valuation)))


def p_adic_distance(left: int, right: int, p: int) -> float:
    """Return d_p(left, right)=|left-right|_p."""
    return p_adic_norm(int(left) - int(right), p)
