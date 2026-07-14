from __future__ import annotations

import pytest

from dsl.ir.ir1.nodes import (
    AttributeExpressionIR,
    ComparisonIR,
    ConstantExpressionIR,
)
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

    lower_atom = lower.formula.expression
    upper_atom = upper.formula.expression

    assert isinstance(lower_atom.left, AttributeExpressionIR)
    assert lower_atom.left.entity == "x0"
    assert lower_atom.left.feature == "a"
    assert lower_atom.op == EnumComparisonOperator.GTE
    assert isinstance(lower_atom.right, ConstantExpressionIR)
    assert lower_atom.right.value == 0.0

    assert isinstance(upper_atom.left, AttributeExpressionIR)
    assert upper_atom.left.entity == "x0"
    assert upper_atom.left.feature == "a"
    assert upper_atom.op == EnumComparisonOperator.LTE
    assert isinstance(upper_atom.right, ConstantExpressionIR)
    assert upper_atom.right.value == 3.0


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
    assert isinstance(atom.right, ConstantExpressionIR)
    assert atom.right.value == 0.0


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
    assert isinstance(atom.right, ConstantExpressionIR)
    assert atom.right.value == 3.0


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
