from dsl.backends.z3_backend.runner import VerificationStatus, Z3Runner
from dsl.ir.ir1.nodes import AndIR, ComparisonIR, NotIR, ScopeIR
from dsl.ir.ir2.enums import AssumptionSource, NormalFormKind, VerificationSemantics
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
    requires_model_assertions: bool = False,
) -> IR2Requirements:
    return IR2Requirements(
        requires_boolean_logic=True,
        requires_numeric_comparisons=True,
        requires_problem_predicates=False,
        requires_model_assertions=requires_model_assertions,
        requires_quantifiers=False,
        requires_domains=False,
        requires_neighborhoods=False,
        normal_form=NormalFormKind.NNF,
    )


def _task(
    *,
    spec: NNFFormulaIR2,
    vc: NNFFormulaIR2,
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
        semantics=VerificationSemantics.REFUTATION,
        normal_form=NormalFormKind.NNF,
        requirements=_requirements(
            requires_model_assertions=requires_model_assertions,
        ),
    )


def test_z3_runner_returns_counterexample_when_vc_is_sat() -> None:
    atom = ComparisonIR(
        entity="x",
        feature="a",
        op=EnumComparisonOperator.LTE,
        value=1.0,
    )

    task = _task(
        spec=NNFFormulaIR2(expression=atom),
        vc=NNFFormulaIR2(expression=atom),
    )

    result = Z3Runner().run(task)

    assert result.status == VerificationStatus.COUNTEREXAMPLE
    assert result.solver_status == "sat"
    assert result.model is not None
    assert "x.a" in result.model


def test_z3_runner_returns_proved_when_vc_is_unsat() -> None:
    atom = ComparisonIR(
        entity="x",
        feature="a",
        op=EnumComparisonOperator.LTE,
        value=1.0,
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
    )

    result = Z3Runner().run(task)

    assert result.status == VerificationStatus.PROVED
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
        assumptions=(assumption,),
        requires_model_assertions=True,
    )

    result = Z3Runner().run(task)

    assert result.status == VerificationStatus.PROVED
    assert result.solver_status == "unsat"
    assert result.model is None
