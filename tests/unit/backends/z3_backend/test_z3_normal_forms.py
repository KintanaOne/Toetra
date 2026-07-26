from __future__ import annotations

from toetra._backends.z3_backend.runner import VerificationStatus, Z3Runner
from toetra._compiler.ir.ir1.nodes import (
    AttributeExpressionIR,
    ComparisonIR,
    ConstantExpressionIR,
    ScopeIR,
)
from toetra._compiler.ir.ir2.enums import (
    NormalFormKind,
    Polarity,
    VerificationSemantics,
)
from toetra._compiler.ir.ir2.dsl.nodes import (
    ClauseIR2,
    CNFFormulaIR2,
    DNFFormulaIR2,
    FormulaIR2,
    LiteralIR2,
    NNFFormulaIR2,
    TermIR2,
    VerificationTaskIR2,
)
from toetra._compiler.ir.ir2.requirements import IR2Requirements
from toetra._language.vocabulary.backends import EnumBackend
from toetra._language.vocabulary.operators import EnumComparisonOperator
from toetra._language.vocabulary.properties import EnumProperty
from toetra._compiler.semantic.types.enums import EnumDataType


def _atom() -> ComparisonIR:
    return ComparisonIR(
        left=AttributeExpressionIR(entity="x", feature="a"),
        op=EnumComparisonOperator.LTE,
        right=ConstantExpressionIR(value=1.0, dtype=EnumDataType.FLOAT),
    )


def _pointwise_scope() -> ScopeIR:
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
        normal_form=normal_form,
    )


def _task(
    *,
    spec: NNFFormulaIR2,
    vc: FormulaIR2,
    normal_form: NormalFormKind,
) -> VerificationTaskIR2:
    return VerificationTaskIR2(
        property_type=EnumProperty.LOGIC,
        scope=_pointwise_scope(),
        backend=EnumBackend.Z3,
        assumptions=(),
        spec_formula=spec,
        verification_condition=vc,
        semantics=VerificationSemantics.REFUTATION,
        normal_form=normal_form,
        requirements=_requirements(normal_form),
    )


def _positive(atom: ComparisonIR) -> LiteralIR2:
    return LiteralIR2(
        atom=atom,
        polarity=Polarity.POSITIVE,
    )


def _negative(atom: ComparisonIR) -> LiteralIR2:
    return LiteralIR2(
        atom=atom,
        polarity=Polarity.NEGATIVE,
    )


def test_z3_runner_proves_unsat_cnf_contradiction() -> None:
    atom = _atom()

    # CNF:
    #   (A) AND (NOT A)
    #
    # This is UNSAT, therefore Toetra status must be PROVED.
    vc = CNFFormulaIR2(
        clauses=(
            ClauseIR2(literals=(_positive(atom),)),
            ClauseIR2(literals=(_negative(atom),)),
        )
    )

    task = _task(
        spec=NNFFormulaIR2(expression=atom),
        vc=vc,
        normal_form=NormalFormKind.CNF,
    )

    result = Z3Runner().run(task)

    assert result.status == VerificationStatus.PROVED
    assert result.solver_status == "unsat"
    assert result.model is None


def test_z3_runner_finds_counterexample_for_sat_cnf() -> None:
    atom = _atom()

    # CNF:
    #   (A)
    #
    # This is SAT as a verification condition, therefore Toetra status
    # must be COUNTEREXAMPLE.
    vc = CNFFormulaIR2(clauses=(ClauseIR2(literals=(_positive(atom),)),))

    task = _task(
        spec=NNFFormulaIR2(expression=atom),
        vc=vc,
        normal_form=NormalFormKind.CNF,
    )

    result = Z3Runner().run(task)

    assert result.status == VerificationStatus.COUNTEREXAMPLE
    assert result.solver_status == "sat"
    assert result.model is not None
    assert "x.a" in result.model


def test_z3_runner_proves_unsat_dnf_contradiction() -> None:
    atom = _atom()

    # DNF:
    #   (A AND NOT A)
    #
    # This is UNSAT, therefore Toetra status must be PROVED.
    vc = DNFFormulaIR2(
        terms=(
            TermIR2(
                literals=(
                    _positive(atom),
                    _negative(atom),
                )
            ),
        )
    )

    task = _task(
        spec=NNFFormulaIR2(expression=atom),
        vc=vc,
        normal_form=NormalFormKind.DNF,
    )

    result = Z3Runner().run(task)

    assert result.status == VerificationStatus.PROVED
    assert result.solver_status == "unsat"
    assert result.model is None


def test_z3_runner_finds_counterexample_for_sat_dnf() -> None:
    atom = _atom()

    # DNF:
    #   (A) OR (NOT A)
    #
    # This is SAT as a verification condition, therefore Toetra status
    # must be COUNTEREXAMPLE.
    vc = DNFFormulaIR2(
        terms=(
            TermIR2(literals=(_positive(atom),)),
            TermIR2(literals=(_negative(atom),)),
        )
    )

    task = _task(
        spec=NNFFormulaIR2(expression=atom),
        vc=vc,
        normal_form=NormalFormKind.DNF,
    )

    result = Z3Runner().run(task)

    assert result.status == VerificationStatus.COUNTEREXAMPLE
    assert result.solver_status == "sat"
    assert result.model is not None
    assert "x.a" in result.model
