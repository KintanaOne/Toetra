from __future__ import annotations

import pytest

from toetra._backends.errors import UnsupportedScalarExpressionError
from toetra._backends.z3_backend.runner import VerificationStatus, Z3Runner
from toetra._backends.z3_backend.translator import Z3Translator
from toetra._compiler.ir.ir1.nodes import (
    AndIR,
    AttributeExpressionIR,
    BinaryArithmeticExpressionIR,
    ComparisonIR,
    ConstantExpressionIR,
    NotIR,
    ScopeIR,
    UnaryArithmeticExpressionIR,
)
from toetra._compiler.ir.ir2.enums import (
    AssumptionSource,
    NormalFormKind,
    VerificationSemantics,
)
from toetra._compiler.ir.ir2.model.affine import (
    AffineExpressionIR2,
    AffineOutputConstraintIR2,
    AffineTermIR2,
)
from toetra._compiler.ir.ir2.dsl.nodes import (
    AssumptionIR2,
    NNFFormulaIR2,
    VerificationTaskIR2,
)
from toetra._compiler.ir.ir2.requirements import IR2Requirements
from toetra._language.vocabulary.backends import EnumBackend
from toetra._language.vocabulary.operators import (
    EnumArithmeticOperator,
    EnumComparisonOperator,
    EnumUnaryOperator,
)
from toetra._language.vocabulary.properties import EnumProperty
from toetra._compiler.semantic.types.enums import EnumDataType


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
    requires_affine_arithmetic: bool = False,
    requires_nonlinear_arithmetic: bool = False,
    requires_symbolic_division: bool = False,
) -> IR2Requirements:
    return IR2Requirements(
        requires_boolean_logic=True,
        requires_numeric_comparisons=True,
        requires_problem_predicates=False,
        requires_model_assertions=requires_model_assertions,
        requires_domains=False,
        requires_neighborhoods=False,
        normal_form=NormalFormKind.NNF,
        uses_quantified_scope=False,
        requires_native_quantifiers=False,
        required_verification_semantics=semantics,
        requires_affine_arithmetic=requires_affine_arithmetic,
        requires_nonlinear_arithmetic=requires_nonlinear_arithmetic,
        requires_symbolic_division=requires_symbolic_division,
        required_scalar_sorts=frozenset({EnumDataType.INT, EnumDataType.FLOAT}),
    )


def _task(
    *,
    spec: NNFFormulaIR2,
    vc: NNFFormulaIR2,
    semantics: VerificationSemantics,
    assumptions: tuple[AssumptionIR2, ...] = (),
    requires_model_assertions: bool = False,
    requires_affine_arithmetic: bool = False,
    requires_nonlinear_arithmetic: bool = False,
    requires_symbolic_division: bool = False,
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
            requires_affine_arithmetic=requires_affine_arithmetic,
            requires_nonlinear_arithmetic=requires_nonlinear_arithmetic,
            requires_symbolic_division=requires_symbolic_division,
        ),
    )


def _comparison() -> ComparisonIR:
    return ComparisonIR(
        left=AttributeExpressionIR(entity="x", feature="a"),
        op=EnumComparisonOperator.LTE,
        right=ConstantExpressionIR(value=1.0, dtype=EnumDataType.FLOAT),
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


def test_z3_translates_nested_affine_scalar_expression() -> None:
    expression = BinaryArithmeticExpressionIR(
        left=UnaryArithmeticExpressionIR(
            operator=EnumUnaryOperator.MINUS,
            operand=AttributeExpressionIR(
                entity="x", feature="a", dtype=EnumDataType.FLOAT
            ),
        ),
        operator=EnumArithmeticOperator.ADD,
        right=BinaryArithmeticExpressionIR(
            left=ConstantExpressionIR(value=2, dtype=EnumDataType.INT),
            operator=EnumArithmeticOperator.MUL,
            right=AttributeExpressionIR(
                entity="x", feature="b", dtype=EnumDataType.FLOAT
            ),
        ),
    )
    atom = ComparisonIR(
        left=expression,
        op=EnumComparisonOperator.LTE,
        right=ConstantExpressionIR(value=3, dtype=EnumDataType.INT),
    )
    task = _task(
        spec=NNFFormulaIR2(expression=atom),
        vc=NNFFormulaIR2(expression=atom),
        semantics=VerificationSemantics.SATISFACTION,
        requires_affine_arithmetic=True,
    )
    result = Z3Runner().run(task)
    assert result.status is VerificationStatus.WITNESS
    assert result.model is not None
    assert set(result.model) == {"x.a", "x.b"}


def test_z3_translates_division_by_nonzero_constant_expression() -> None:
    denominator = BinaryArithmeticExpressionIR(
        left=ConstantExpressionIR(value=1, dtype=EnumDataType.INT),
        operator=EnumArithmeticOperator.ADD,
        right=ConstantExpressionIR(value=1, dtype=EnumDataType.INT),
    )
    quotient = BinaryArithmeticExpressionIR(
        left=AttributeExpressionIR(entity="x", feature="a", dtype=EnumDataType.FLOAT),
        operator=EnumArithmeticOperator.DIV,
        right=denominator,
    )
    atom = ComparisonIR(
        left=quotient,
        op=EnumComparisonOperator.LTE,
        right=ConstantExpressionIR(value=2, dtype=EnumDataType.INT),
    )
    task = _task(
        spec=NNFFormulaIR2(expression=atom),
        vc=NNFFormulaIR2(expression=atom),
        semantics=VerificationSemantics.SATISFACTION,
        requires_affine_arithmetic=True,
    )
    assert Z3Runner().run(task).status is VerificationStatus.WITNESS


def test_z3_uses_integer_sort_for_typed_integer_variable() -> None:
    atom = ComparisonIR(
        left=AttributeExpressionIR(entity="x", feature="count", dtype=EnumDataType.INT),
        op=EnumComparisonOperator.EQ,
        right=ConstantExpressionIR(value=1, dtype=EnumDataType.INT),
    )
    task = _task(
        spec=NNFFormulaIR2(expression=atom),
        vc=NNFFormulaIR2(expression=atom),
        semantics=VerificationSemantics.SATISFACTION,
    )
    translation = Z3Translator().translate(task)
    assert str(translation.variables["x.count"].sort()) == "Int"


def test_z3_rejects_nonlinear_multiplication() -> None:
    product = BinaryArithmeticExpressionIR(
        left=AttributeExpressionIR(entity="x", feature="a"),
        operator=EnumArithmeticOperator.MUL,
        right=AttributeExpressionIR(entity="x", feature="b"),
    )
    atom = ComparisonIR(
        left=product,
        op=EnumComparisonOperator.LTE,
        right=ConstantExpressionIR(value=3, dtype=EnumDataType.INT),
    )
    task = _task(
        spec=NNFFormulaIR2(expression=atom),
        vc=NNFFormulaIR2(expression=atom),
        semantics=VerificationSemantics.REFUTATION,
    )
    with pytest.raises(
        UnsupportedScalarExpressionError, match="nonlinear multiplication"
    ):
        Z3Runner().run(task)


def test_z3_rejects_symbolic_division() -> None:
    quotient = BinaryArithmeticExpressionIR(
        left=AttributeExpressionIR(entity="x", feature="a"),
        operator=EnumArithmeticOperator.DIV,
        right=AttributeExpressionIR(entity="x", feature="b"),
    )
    atom = ComparisonIR(
        left=quotient,
        op=EnumComparisonOperator.LTE,
        right=ConstantExpressionIR(value=3, dtype=EnumDataType.INT),
    )
    task = _task(
        spec=NNFFormulaIR2(expression=atom),
        vc=NNFFormulaIR2(expression=atom),
        semantics=VerificationSemantics.REFUTATION,
    )
    with pytest.raises(
        UnsupportedScalarExpressionError,
        match="division by a symbolic expression",
    ):
        Z3Runner().run(task)


def test_z3_runner_returns_structured_message_for_each_result() -> None:
    atom = _comparison()
    task = _task(
        spec=NNFFormulaIR2(expression=atom),
        vc=NNFFormulaIR2(expression=atom),
        semantics=VerificationSemantics.REFUTATION,
    )

    result = Z3Runner().run(task)

    assert result.status is VerificationStatus.COUNTEREXAMPLE
    assert result.message.startswith("Property violated")
    assert result.diagnostics == ()


def test_z3_runner_reports_unknown_as_inconclusive(monkeypatch) -> None:
    import toetra._backends.z3_backend.runner as runner_module

    class UnknownSolver:
        def add(self, expression) -> None:
            del expression

        def check(self):
            return runner_module.z3.unknown

    monkeypatch.setattr(runner_module.z3, "Solver", UnknownSolver)

    atom = _comparison()
    task = _task(
        spec=NNFFormulaIR2(expression=atom),
        vc=NNFFormulaIR2(expression=atom),
        semantics=VerificationSemantics.REFUTATION,
    )

    result = Z3Runner().run(task)

    assert result.status is VerificationStatus.UNKNOWN
    assert result.solver_status == "unknown"
    assert result.model is None
    assert result.message == "Verification inconclusive: Z3 returned unknown."


def _inconsistent_assumptions() -> tuple[AssumptionIR2, ...]:
    lower = ComparisonIR(
        left=AttributeExpressionIR(
            entity="x",
            feature="a",
            dtype=EnumDataType.FLOAT,
        ),
        op=EnumComparisonOperator.GTE,
        right=ConstantExpressionIR(value=1.0, dtype=EnumDataType.FLOAT),
    )
    upper = ComparisonIR(
        left=AttributeExpressionIR(
            entity="x",
            feature="a",
            dtype=EnumDataType.FLOAT,
        ),
        op=EnumComparisonOperator.LTE,
        right=ConstantExpressionIR(value=0.0, dtype=EnumDataType.FLOAT),
    )
    return (
        AssumptionIR2(
            source=AssumptionSource.DOMAIN,
            formula=NNFFormulaIR2(expression=lower),
            description="lower bound",
        ),
        AssumptionIR2(
            source=AssumptionSource.DOMAIN,
            formula=NNFFormulaIR2(expression=upper),
            description="upper bound",
        ),
    )


def test_z3_runner_warns_when_universal_proof_is_vacuous() -> None:
    from toetra._backends.diagnostics import BackendDiagnosticSeverity
    from toetra._backends.z3_backend.runner import Z3_VACUOUS_PROOF

    atom = _comparison()
    task = _task(
        spec=NNFFormulaIR2(expression=atom),
        vc=NNFFormulaIR2(expression=_contradiction(atom)),
        semantics=VerificationSemantics.REFUTATION,
        assumptions=_inconsistent_assumptions(),
    )

    result = Z3Runner().run(task)

    assert result.status is VerificationStatus.PROVED
    assert len(result.diagnostics) == 1
    diagnostic = result.diagnostics[0]
    assert diagnostic.code == Z3_VACUOUS_PROOF
    assert diagnostic.severity is BackendDiagnosticSeverity.WARNING
    assert "admissible set is empty" in diagnostic.message


def test_z3_runner_warns_when_no_witness_comes_from_inconsistent_assumptions() -> None:
    from toetra._backends.z3_backend.runner import Z3_INCONSISTENT_ASSUMPTIONS

    atom = _comparison()
    task = _task(
        spec=NNFFormulaIR2(expression=atom),
        vc=NNFFormulaIR2(expression=_contradiction(atom)),
        semantics=VerificationSemantics.SATISFACTION,
        assumptions=_inconsistent_assumptions(),
    )

    result = Z3Runner().run(task)

    assert result.status is VerificationStatus.NO_WITNESS
    assert [diagnostic.code for diagnostic in result.diagnostics] == [
        Z3_INCONSISTENT_ASSUMPTIONS
    ]


def test_z3_runner_does_not_report_vacuity_when_assumptions_are_satisfiable() -> None:
    atom = _comparison()
    satisfiable_assumption = AssumptionIR2(
        source=AssumptionSource.DOMAIN,
        formula=NNFFormulaIR2(expression=atom),
        description="satisfiable domain",
    )
    task = _task(
        spec=NNFFormulaIR2(expression=atom),
        vc=NNFFormulaIR2(expression=_contradiction(atom)),
        semantics=VerificationSemantics.REFUTATION,
        assumptions=(satisfiable_assumption,),
    )

    result = Z3Runner().run(task)

    assert result.status is VerificationStatus.PROVED
    assert result.diagnostics == ()
