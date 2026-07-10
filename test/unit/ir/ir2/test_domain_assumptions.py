from __future__ import annotations

import pytest

from dsl.ir.ir1.nodes import ComparisonIR
from dsl.ir.ir2.domain_assumptions import (
    DomainAssumptionEncoder,
    NumericFeatureBounds,
)
from dsl.ir.ir2.enums import AssumptionSource
from dsl.ir.ir2.nodes import NNFFormulaIR2
from dsl.language.vocabulary.operators import EnumComparisonOperator


def test_domain_assumption_encoder_emits_lower_and_upper_bounds() -> None:
    assumptions = DomainAssumptionEncoder().encode(
        (
            NumericFeatureBounds(
                entity="x0",
                feature="a",
                lower=0.0,
                upper=3.0,
            ),
        )
    )

    assert len(assumptions) == 2

    lower, upper = assumptions

    assert lower.source == AssumptionSource.DOMAIN
    assert upper.source == AssumptionSource.DOMAIN

    assert isinstance(lower.formula, NNFFormulaIR2)
    assert isinstance(upper.formula, NNFFormulaIR2)

    assert isinstance(lower.formula.expression, ComparisonIR)
    assert isinstance(upper.formula.expression, ComparisonIR)

    assert lower.formula.expression.entity == "x0"
    assert lower.formula.expression.feature == "a"
    assert lower.formula.expression.op == EnumComparisonOperator.GTE
    assert lower.formula.expression.value == 0.0

    assert upper.formula.expression.entity == "x0"
    assert upper.formula.expression.feature == "a"
    assert upper.formula.expression.op == EnumComparisonOperator.LTE
    assert upper.formula.expression.value == 3.0


def test_domain_assumption_encoder_emits_only_lower_bound() -> None:
    assumptions = DomainAssumptionEncoder().encode(
        (
            NumericFeatureBounds(
                entity="x0",
                feature="a",
                lower=0.0,
            ),
        )
    )

    assert len(assumptions) == 1

    atom = assumptions[0].formula.expression

    assert isinstance(atom, ComparisonIR)
    assert atom.op == EnumComparisonOperator.GTE
    assert atom.value == 0.0


def test_domain_assumption_encoder_emits_only_upper_bound() -> None:
    assumptions = DomainAssumptionEncoder().encode(
        (
            NumericFeatureBounds(
                entity="x0",
                feature="a",
                upper=3.0,
            ),
        )
    )

    assert len(assumptions) == 1

    atom = assumptions[0].formula.expression

    assert isinstance(atom, ComparisonIR)
    assert atom.op == EnumComparisonOperator.LTE
    assert atom.value == 3.0


def test_domain_assumption_encoder_rejects_empty_bounds() -> None:
    with pytest.raises(ValueError, match="at least one"):
        DomainAssumptionEncoder().encode(
            (
                NumericFeatureBounds(
                    entity="x0",
                    feature="a",
                ),
            )
        )


def test_domain_assumption_encoder_rejects_inverted_bounds() -> None:
    with pytest.raises(ValueError, match="lower=4.0 > upper=3.0"):
        DomainAssumptionEncoder().encode(
            (
                NumericFeatureBounds(
                    entity="x0",
                    feature="a",
                    lower=4.0,
                    upper=3.0,
                ),
            )
        )
