from __future__ import annotations

import pytest

from toetra._backends.diagnostics import (
    BackendDiagnosticSeverity,
    BackendResultDiagnostic,
)
from toetra._backends.results import VerificationResult, VerificationStatus
from toetra._backends.z3_backend.capabilities import Z3_CAPABILITIES
from toetra._backends.router import BackendRoute
from toetra._compiler.ir.ir1.nodes import (
    ComparisonIR,
    ConstantExpressionIR,
    ScopeIR,
    TargetExpressionIR,
)
from toetra._compiler.ir.ir2.enums import NormalFormKind, VerificationSemantics
from toetra._compiler.ir.ir2.dsl.nodes import (
    NNFFormulaIR2,
    VerificationTaskIR2,
)
from toetra._compiler.ir.ir2.requirements import IR2Requirements
from toetra._language.vocabulary.backends import EnumBackend
from toetra._language.vocabulary.operators import EnumComparisonOperator
from toetra._language.vocabulary.properties import EnumProperty
from toetra._reporting.model import ReportAssignmentKind
from toetra._reporting.builder import build_verification_report
from toetra._compiler.semantic.types.enums import EnumDataType


def _task() -> VerificationTaskIR2:
    comparison = ComparisonIR(
        left=TargetExpressionIR(feature="score", dtype=EnumDataType.FLOAT),
        op=EnumComparisonOperator.LTE,
        right=ConstantExpressionIR(value=7.0, dtype=EnumDataType.FLOAT),
    )
    formula = NNFFormulaIR2(expression=comparison)
    semantics = VerificationSemantics.REFUTATION
    return VerificationTaskIR2(
        property_type=EnumProperty.BOUND,
        scope=ScopeIR(
            kind="quantifier",
            variables={"x0": "bound"},
            neighborhood=None,
            domain=None,
            quantifier="forall",
        ),
        backend=EnumBackend.Z3,
        assumptions=(),
        spec_formula=formula,
        verification_condition=formula,
        semantics=semantics,
        normal_form=NormalFormKind.NNF,
        requirements=IR2Requirements(
            requires_boolean_logic=True,
            requires_numeric_comparisons=True,
            requires_problem_predicates=False,
            requires_model_assertions=False,
            requires_domains=False,
            requires_neighborhoods=False,
            normal_form=NormalFormKind.NNF,
            uses_quantified_scope=True,
            requires_native_quantifiers=False,
            required_verification_semantics=semantics,
        ),
    )


def _route() -> BackendRoute:
    return BackendRoute(
        backend=EnumBackend.Z3,
        capabilities=Z3_CAPABILITIES,
        reason="requested backend satisfies IR2 requirements",
    )


def test_report_builder_combines_task_route_and_result() -> None:
    diagnostic = BackendResultDiagnostic(
        code="EXAMPLE",
        severity=BackendDiagnosticSeverity.WARNING,
        message="example diagnostic",
    )
    result = VerificationResult(
        status=VerificationStatus.COUNTEREXAMPLE,
        backend=EnumBackend.Z3,
        backend_status="sat",
        assignments={
            "x0.a": "3",
            "_model.score": "7",
            "internal": "1",
        },
        message="Property violated",
        diagnostics=(diagnostic,),
    )

    report = build_verification_report(
        _task(),
        _route(),
        result,
        property_index=2,
    )

    assert report.property_index == 2
    assert report.property_type is EnumProperty.BOUND
    assert report.semantics is VerificationSemantics.REFUTATION
    assert report.scope.kind == "quantifier"
    assert report.scope.quantifier == "forall"
    assert report.scope.variables[0].name == "x0"
    assert report.specification == "_model.score <= 7.0"
    assert report.backend is EnumBackend.Z3
    assert report.backend_status == "sat"
    assert report.status is VerificationStatus.COUNTEREXAMPLE
    assert report.summary == "Property violated"
    assert report.route_reason == "requested backend satisfies IR2 requirements"
    assert report.diagnostics == (diagnostic,)
    assert report.has_failure is True

    assert [(item.display_name, item.kind) for item in report.assignments] == [
        ("score", ReportAssignmentKind.OUTPUT),
        ("internal", ReportAssignmentKind.AUXILIARY),
        ("x0.a", ReportAssignmentKind.INPUT),
    ]
    assert [item.display_name for item in report.inputs] == ["x0.a"]
    assert [item.display_name for item in report.outputs] == ["score"]
    assert [item.display_name for item in report.auxiliary_assignments] == ["internal"]


def test_report_builder_handles_result_without_assignments() -> None:
    result = VerificationResult(
        status=VerificationStatus.PROVED,
        backend=EnumBackend.Z3,
        backend_status="unsat",
        assignments=None,
        message="proved",
    )

    report = build_verification_report(
        _task(),
        _route(),
        result,
        property_index=0,
    )

    assert report.assignments == ()
    assert report.inputs == ()
    assert report.outputs == ()
    assert report.has_failure is False


def test_report_builder_rejects_route_result_backend_mismatch() -> None:
    result = VerificationResult(
        status=VerificationStatus.UNKNOWN,
        backend=EnumBackend.ERAN,
        backend_status="unknown",
    )

    with pytest.raises(ValueError, match="does not match"):
        build_verification_report(
            _task(),
            _route(),
            result,
            property_index=0,
        )
