from __future__ import annotations

import pytest

from toetra._compiler.parser.errors import ParserError
from toetra._compiler.semantic.rules.migration import (
    LEGACY_AT_MESSAGE,
    LEGACY_CHECK_AT_MESSAGE,
    LEGACY_PAIRWISE_MESSAGE,
)
from ._point_binding_helpers import build_and_validate


def test_legacy_undeclared_check_at_has_frozen_migration_diagnostic() -> None:
    source = """
        model := "model.joblib"
        target := score

        [BOUND]:
        check_at x0 => target <= 7
    """

    with pytest.raises(ParserError) as caught:
        build_and_validate(source)

    assert LEGACY_CHECK_AT_MESSAGE.format(name="x0") in str(caught.value)


def test_legacy_at_has_frozen_migration_diagnostic() -> None:
    source = """
        model := "model.joblib"
        target := score

        [ROBUSTNESS]:
        at x0 in neighborhood(L2, eps=0.1) => target <= 7
    """

    with pytest.raises(ParserError) as caught:
        build_and_validate(source)

    assert LEGACY_AT_MESSAGE.format(name="x0") in str(caught.value)


def test_legacy_pairwise_has_frozen_migration_diagnostic() -> None:
    source = """
        model := "model.joblib"
        target := score

        [MONOTONICITY]:
        x ~ x' in neighborhood(L2, eps=0.1) => x.a <= 1
    """

    with pytest.raises(ParserError) as caught:
        build_and_validate(source)

    assert LEGACY_PAIRWISE_MESSAGE.format(pair="x ~ x'") in str(caught.value)
