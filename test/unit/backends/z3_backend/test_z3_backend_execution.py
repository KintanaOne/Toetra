from __future__ import annotations

from dsl.backends.z3_backend.runner import VerificationStatus, Z3Runner
from dsl.ir.ir1.nodes import AndIR, ComparisonIR, NotIR, ScopeIR
from dsl.ir.ir2.enums import (
    AssumptionSource,
    NormalFormKind,
    VerificationSemantics,
)
from dsl.ir.ir2.nodes import (
    AffineExpressionIR2,
    AffineOutputConstraintIR2,
    AffineTermIR2,
    AssumptionIR2,
    NNFFormulaIR2,
    VerificationTaskIR2,
)
from dsl.ir.ir2.requirements import IR2Requirements
from dsl.language.vocabulary.backends import EnumBackend
from dsl.language.vocabulary.operators import EnumComparisonOperator
from dsl.language.vocabulary.properties import EnumProperty


def _pointwise_scope() -> ScopeIR:
    return ScopeIR(
        kind="pointwise",
        variables={"x": "anchor"},
        neighborhood=None,
        domain=None,
    )


def _requirements(
    *,
    semantics: VerificationSemantics,
    requires_model_assertions: bool = False,
) -> IR2Requirements:
    return IR2Requirements(
        requires_boolean_logic=True,
        requires_numeric_comparisons=True,
        requires_problem_predicates=False,
        requires_model_assertions=requires_model_assertions,
        # Compatibility field during the quantifier migration.
        requires_quantifiers=False,
        requires_domains=False,
        requires_neighborhoods=False,
        normal_form=NormalFormKind.NNF,
        uses_quantified_scope=False,
        requires_native_quantifiers=False,
        required_verification_semantics=semantics,
    )


def _task(
    *,
    spec: NNFFormulaIR2,
    vc: NNFFormulaIR2,
    semantics: VerificationSemantics,
    assumptions: tuple[AssumptionIR2, ...] = (),
    requires_model_assertions: bool = False,
) -> VerificationTaskIR2:
    return VerificationTaskIR2(
        property_type=EnumProperty.LOGIC,
        scope=_pointwise_scope(),
        backend=EnumBackend.Z3,
        assumptions=assumptions,
        spec_formula=spec,
        verification_condition=vc,
        semantics=semantics,
        normal_form=NormalFormKind.NNF,
        requirements=_requirements(
            semantics=semantics,
            requires_model_assertions=requires_model_assertions,
        ),
    )


def _comparison() -> ComparisonIR:
    return ComparisonIR(
        entity="x",
        feature="a",
        op=EnumComparisonOperator.LTE,
        value=1.0,
    )


def _contradiction(atom: ComparisonIR) -> AndIR:
    return AndIR(
        operands=[
            atom,
            NotIR(atom),
        ]
    )


def test_z3_runner_returns_counterexample_for_sat_refutation() -> None:
    atom = _comparison()

    task = _task(
        spec=NNFFormulaIR2(expression=atom),
        vc=NNFFormulaIR2(expression=atom),
        semantics=VerificationSemantics.REFUTATION,
    )

    result = Z3Runner().run(task)

    assert result.status is VerificationStatus.COUNTEREXAMPLE
    assert result.solver_status == "sat"
    assert result.model is not None
    assert "x.a" in result.model


def test_z3_runner_returns_proved_for_unsat_refutation() -> None:
    atom = _comparison()

    task = _task(
        spec=NNFFormulaIR2(expression=atom),
        vc=NNFFormulaIR2(
            expression=_contradiction(atom),
        ),
        semantics=VerificationSemantics.REFUTATION,
    )

    result = Z3Runner().run(task)

    assert result.status is VerificationStatus.PROVED
    assert result.solver_status == "unsat"
    assert result.model is None


def test_z3_runner_returns_witness_for_sat_satisfaction() -> None:
    atom = _comparison()

    task = _task(
        spec=NNFFormulaIR2(expression=atom),
        vc=NNFFormulaIR2(expression=atom),
        semantics=VerificationSemantics.SATISFACTION,
    )

    result = Z3Runner().run(task)

    assert result.status is VerificationStatus.WITNESS
    assert result.solver_status == "sat"
    assert result.model is not None
    assert "x.a" in result.model


def test_z3_runner_returns_no_witness_for_unsat_satisfaction() -> None:
    atom = _comparison()

    task = _task(
        spec=NNFFormulaIR2(expression=atom),
        vc=NNFFormulaIR2(
            expression=_contradiction(atom),
        ),
        semantics=VerificationSemantics.SATISFACTION,
    )

    result = Z3Runner().run(task)

    assert result.status is VerificationStatus.NO_WITNESS
    assert result.solver_status == "unsat"
    assert result.model is None


def test_z3_runner_supports_affine_model_output_constraint() -> None:
    atom = AffineOutputConstraintIR2(
        output_entity="_model",
        output_feature="MyTarget",
        op=EnumComparisonOperator.EQ,
        expression=AffineExpressionIR2(
            terms=(
                AffineTermIR2(
                    entity="x",
                    feature="a",
                    coefficient=2.0,
                ),
            ),
            bias=1.0,
        ),
    )

    assumption = AssumptionIR2(
        source=AssumptionSource.MODEL,
        formula=NNFFormulaIR2(expression=atom),
        description="test affine model equation",
    )

    contradiction = AndIR(
        operands=[
            atom,
            NotIR(atom),
        ]
    )

    task = _task(
        spec=NNFFormulaIR2(expression=atom),
        vc=NNFFormulaIR2(expression=contradiction),
        semantics=VerificationSemantics.REFUTATION,
        assumptions=(assumption,),
        requires_model_assertions=True,
    )

    result = Z3Runner().run(task)

    assert result.status is VerificationStatus.PROVED
    assert result.solver_status == "unsat"
    assert result.model is None
