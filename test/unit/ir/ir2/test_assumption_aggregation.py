from __future__ import annotations

from typing import Any, cast

import pytest

from dsl.ir.ir1.nodes import (
    AndIR,
    ComparisonIR,
    OrIR,
    QueryIR,
    ScopeIR,
    VerificationTask,
)
from dsl.ir.ir2.assumptions import AssumptionCollector
from dsl.ir.ir2.builder import IR2Builder
from dsl.ir.ir2.context import IR2BuildContext
from dsl.ir.ir2.enums import (
    AssumptionSource,
    NormalFormKind,
    Polarity,
    VerificationSemantics,
)
from dsl.ir.ir2.errors import IR2ValidationError, InvalidIR2InputError
from dsl.ir.ir2.nodes import (
    AssumptionIR2,
    ClauseIR2,
    CNFFormulaIR2,
    DNFFormulaIR2,
    LiteralIR2,
    NNFFormulaIR2,
    VerificationTaskIR2,
)
from dsl.ir.ir2.requirements import IR2Requirements
from dsl.ir.ir2.validator import IR2Validator
from dsl.language.vocabulary.operators import EnumComparisonOperator
from dsl.language.vocabulary.properties import EnumProperty


def _cmp(feature: str, value: int = 1) -> ComparisonIR:
    return ComparisonIR(
        entity="x",
        feature=feature,
        op=EnumComparisonOperator.LTE,
        value=value,
    )


def _literal_signature(literal: LiteralIR2) -> tuple[str, Polarity]:
    assert isinstance(literal.atom, ComparisonIR)
    return literal.atom.feature, literal.polarity


def _scope() -> ScopeIR:
    return ScopeIR(
        kind="pointwise",
        variables={"x": "anchor"},
        neighborhood=None,
        domain=None,
    )


def _requirements(normal_form: NormalFormKind) -> IR2Requirements:
    return IR2Requirements(
        requires_boolean_logic=True,
        requires_numeric_comparisons=True,
        requires_problem_predicates=False,
        requires_model_assertions=False,
        requires_domains=False,
        requires_neighborhoods=False,
        requires_native_quantifiers=False,
        normal_form=normal_form,
    )


def test_assumption_collector_returns_immutable_tuple() -> None:
    assumption = AssumptionIR2(
        source=AssumptionSource.MODEL,
        formula=NNFFormulaIR2(expression=_cmp("model_constraint")),
    )

    collected = AssumptionCollector().collect([assumption])

    assert collected == (assumption,)


def test_assumption_collector_rejects_non_assumption_items() -> None:
    with pytest.raises(InvalidIR2InputError, match="must be AssumptionIR2"):
        AssumptionCollector().collect(cast(Any, [object()]))


def test_assumption_collector_rejects_non_nnf_assumption_formula() -> None:
    invalid_expression = AndIR(
        operands=[
            _cmp("a"),
            OrIR(operands=[_cmp("b"), _cmp("c")]),
        ]
    )

    assumption = AssumptionIR2(
        source=AssumptionSource.MODEL,
        formula=cast(Any, invalid_expression),
    )

    with pytest.raises(InvalidIR2InputError, match="must contain NNFFormulaIR2"):
        AssumptionCollector().collect([assumption])


def test_ir2_builder_applies_dnf_after_assumption_aggregation() -> None:
    """DNF must be computed on the full Γ ∧ ¬P formula, not per assumption."""

    model_assumption_1 = AssumptionIR2(
        source=AssumptionSource.MODEL,
        formula=NNFFormulaIR2(
            expression=OrIR(
                operands=[
                    _cmp("a"),
                    _cmp("b"),
                ]
            )
        ),
    )
    model_assumption_2 = AssumptionIR2(
        source=AssumptionSource.MODEL,
        formula=NNFFormulaIR2(
            expression=OrIR(
                operands=[
                    _cmp("c"),
                    _cmp("d"),
                ]
            )
        ),
    )
    task_nnf = VerificationTask(
        property_type=EnumProperty.LOGIC,
        scope=_scope(),
        query=QueryIR(expression=_cmp("e")),
        backend=None,
    )

    task_ir2 = IR2Builder().build(
        task_nnf,
        assumptions=[model_assumption_1, model_assumption_2],
        context=IR2BuildContext(preferred_normal_form=NormalFormKind.DNF),
    )

    assert task_ir2.normal_form == NormalFormKind.DNF
    assert isinstance(task_ir2.verification_condition, DNFFormulaIR2)
    assert len(task_ir2.verification_condition.terms) == 4

    branches = {
        tuple(_literal_signature(literal) for literal in term.literals)
        for term in task_ir2.verification_condition.terms
    }

    assert branches == {
        (("a", Polarity.POSITIVE), ("c", Polarity.POSITIVE), ("e", Polarity.NEGATIVE)),
        (("a", Polarity.POSITIVE), ("d", Polarity.POSITIVE), ("e", Polarity.NEGATIVE)),
        (("b", Polarity.POSITIVE), ("c", Polarity.POSITIVE), ("e", Polarity.NEGATIVE)),
        (("b", Polarity.POSITIVE), ("d", Polarity.POSITIVE), ("e", Polarity.NEGATIVE)),
    }


def test_ir2_validator_rejects_empty_cnf_clause() -> None:
    task = VerificationTaskIR2(
        property_type=EnumProperty.LOGIC,
        scope=_scope(),
        backend=None,
        assumptions=(),
        spec_formula=NNFFormulaIR2(expression=_cmp("spec")),
        verification_condition=CNFFormulaIR2(clauses=(ClauseIR2(literals=()),)),
        semantics=VerificationSemantics.REFUTATION,
        normal_form=NormalFormKind.CNF,
        requirements=_requirements(NormalFormKind.CNF),
    )

    with pytest.raises(IR2ValidationError, match="must contain literals"):
        IR2Validator().validate(task)


def test_ir2_validator_rejects_invalid_literal_polarity() -> None:
    task = VerificationTaskIR2(
        property_type=EnumProperty.LOGIC,
        scope=_scope(),
        backend=None,
        assumptions=(),
        spec_formula=NNFFormulaIR2(expression=_cmp("spec")),
        verification_condition=CNFFormulaIR2(
            clauses=(
                ClauseIR2(
                    literals=(
                        LiteralIR2(
                            atom=_cmp("a"),
                            polarity=cast(Any, "positive"),
                        ),
                    )
                ),
            )
        ),
        semantics=VerificationSemantics.REFUTATION,
        normal_form=NormalFormKind.CNF,
        requirements=_requirements(NormalFormKind.CNF),
    )

    with pytest.raises(IR2ValidationError, match="invalid polarity"):
        IR2Validator().validate(task)
