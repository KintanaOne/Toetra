from __future__ import annotations

import math
from decimal import Decimal

import pytest

from dsl.provenance.fingerprint import (
    CanonicalizationError,
    canonical_json_bytes,
    fingerprint_canonical_json,
    fingerprint_text,
)


def test_text_fingerprint_is_deterministic() -> None:
    assert fingerprint_text("target <= 1") == fingerprint_text("target <= 1")
    assert fingerprint_text("target <= 1") != fingerprint_text("target < 1")


def test_canonical_mapping_order_does_not_change_fingerprint() -> None:
    left = fingerprint_canonical_json({"a": 1, "b": [2, 3]}, canonicalization="test_v1")
    right = fingerprint_canonical_json(
        {"b": [2, 3], "a": 1}, canonicalization="test_v1"
    )
    assert left == right


def test_canonicalization_preserves_float_identity() -> None:
    assert canonical_json_bytes(0.0) != canonical_json_bytes(-0.0)
    assert canonical_json_bytes(0.1) != canonical_json_bytes(math.nextafter(0.1, 1.0))


def test_opaque_object_fails_closed() -> None:
    with pytest.raises(CanonicalizationError):
        canonical_json_bytes(object())


def test_decimal_canonicalization_is_stable_and_representation_preserving() -> None:
    assert canonical_json_bytes(Decimal("0.80")) == canonical_json_bytes(
        Decimal("0.80")
    )
    assert canonical_json_bytes(Decimal("0.80")) != canonical_json_bytes(Decimal("0.8"))
    assert canonical_json_bytes(Decimal("0")) != canonical_json_bytes(Decimal("-0"))
