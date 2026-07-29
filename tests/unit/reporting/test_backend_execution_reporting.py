from __future__ import annotations

from toetra._backends.execution import (
    BackendExecutionEvidence,
    BackendExecutionPolicy,
    BackendExecutionStatus,
    BackendResourceLimits,
)
from toetra._backends.results import VerificationResult, VerificationStatus
from toetra._backends.router import BackendRoute
from toetra._backends.z3_backend.capabilities import Z3_CAPABILITIES
from toetra._compiler.ir.ir1.nodes import ComparisonIR, ConstantExpressionIR, ScopeIR
from toetra._compiler.ir.ir2.enums import NormalFormKind, VerificationSemantics
from toetra._compiler.ir.ir2.dsl.nodes import (
    NNFFormulaIR2,
    VerificationTaskIR2,
)
from toetra._compiler.ir.ir2.requirements import IR2Requirements
from toetra._language.vocabulary.backends import EnumBackend
from toetra._language.vocabulary.operators import EnumComparisonOperator
from toetra._language.vocabulary.properties import EnumProperty
from toetra._reporting.builder import build_verification_report
from toetra._compiler.semantic.types.enums import EnumDataType


def _task() -> VerificationTaskIR2:
    comparison = ComparisonIR(
        left=ConstantExpressionIR(value=1, dtype=EnumDataType.INT),
        op=EnumComparisonOperator.LTE,
        right=ConstantExpressionIR(value=2, dtype=EnumDataType.INT),
    )
    formula = NNFFormulaIR2(expression=comparison)
    return VerificationTaskIR2(
        property_type=EnumProperty.LOGIC,
        scope=ScopeIR(
            kind="pointwise",
            variables={},
            neighborhood=None,
            domain=None,
        ),
        backend=EnumBackend.Z3,
        assumptions=(),
        spec_formula=formula,
        verification_condition=formula,
        semantics=VerificationSemantics.REFUTATION,
        normal_form=NormalFormKind.NNF,
        requirements=IR2Requirements(
            requires_boolean_logic=True,
            requires_numeric_comparisons=True,
            requires_problem_predicates=False,
            requires_model_assertions=False,
            requires_domains=False,
            requires_neighborhoods=False,
            normal_form=NormalFormKind.NNF,
            required_verification_semantics=VerificationSemantics.REFUTATION,
        ),
    )


def _report():
    policy = BackendExecutionPolicy(
        timeout_ms=750,
        resources=BackendResourceLimits(
            max_backend_units=100,
            max_memory_mb=32,
        ),
        deterministic_seed=4,
        backend_options={"adapter_option": True},
    )
    result = VerificationResult(
        status=VerificationStatus.UNKNOWN,
        backend=EnumBackend.Z3,
        backend_status="unknown",
        message="Verification inconclusive: the backend execution timed out.",
        execution=BackendExecutionEvidence(
            status=BackendExecutionStatus.TIMEOUT,
            duration_ms=751.25,
            policy=policy.snapshot(),
            reason="The total deadline expired.",
            backend_reason="timeout",
        ),
    )
    route = BackendRoute(
        backend=EnumBackend.Z3,
        capabilities=Z3_CAPABILITIES,
        reason="test route",
    )
    return build_verification_report(_task(), route, result, property_index=0)


def test_execution_evidence_is_exposed_in_all_report_formats() -> None:
    report = _report()
    payload = report.to_dict()["execution"]["backend_execution"]

    assert payload == {
        "status": "timeout",
        "duration_ms": 751.25,
        "reason": "The total deadline expired.",
        "backend_reason": "timeout",
        "policy": {
            "timeout_ms": 750,
            "max_backend_units": 100,
            "max_memory_mb": 32,
            "deterministic_seed": 4,
            "backend_options": {"adapter_option": True},
        },
    }

    text = report.to_text()
    html = report.to_html()
    assert "Execution     : timeout" in text
    assert "Duration      : 751.250 ms" in text
    assert "Backend units : 100" in text
    assert "Memory        : 32 MB" in text
    assert "Seed          : 4" in text
    assert "Backend opts  : adapter_option=True" in text
    assert "Native reason : timeout" in text
    assert "Backend execution" in html
    assert "751.250 ms" in html
    assert "Backend options" in html
    assert "adapter_option=True" in html
    assert "timeout" in html
