from __future__ import annotations

import time
from typing import cast

import pytest

from toetra._backends.execution import (
    BackendCancellationToken,
    BackendExecutionPolicy,
    BackendExecutionStatus,
    BackendResourceLimits,
)
from toetra._backends.results import VerificationStatus
from toetra._backends.z3_backend.runner import (
    BACKEND_CANCELLED,
    BACKEND_RESOURCE_LIMIT,
    BACKEND_TIMEOUT,
    Z3Runner,
)
from toetra._backends.z3_backend.translator import Z3Translator
from toetra._compiler.ir.ir1.nodes import (
    AttributeExpressionIR,
    ComparisonIR,
    ConstantExpressionIR,
    ScopeIR,
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
from toetra._compiler.semantic.types.enums import EnumDataType


def _task() -> VerificationTaskIR2:
    atom = ComparisonIR(
        left=AttributeExpressionIR(entity="x", feature="a"),
        op=EnumComparisonOperator.LTE,
        right=ConstantExpressionIR(value=1.0, dtype=EnumDataType.FLOAT),
    )
    formula = NNFFormulaIR2(expression=atom)
    return VerificationTaskIR2(
        property_type=EnumProperty.LOGIC,
        scope=ScopeIR(
            kind="pointwise",
            variables={"x": "anchor"},
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
            required_scalar_sorts=frozenset({EnumDataType.FLOAT}),
        ),
    )


def test_z3_result_records_the_backend_neutral_policy_and_duration() -> None:
    policy = BackendExecutionPolicy(
        timeout_ms=2_000,
        resources=BackendResourceLimits(
            max_backend_units=100_000,
            max_memory_mb=256,
        ),
        deterministic_seed=13,
    )

    result = Z3Runner().run(_task(), policy=policy)

    assert result.execution is not None
    assert result.execution.status is BackendExecutionStatus.SAT
    assert result.execution.duration_ms >= 0
    assert result.execution.policy.timeout_ms == 2_000
    assert result.execution.policy.max_backend_units == 100_000
    assert result.execution.policy.max_memory_mb == 256
    assert result.execution.policy.deterministic_seed == 13


def test_pre_cancelled_execution_never_enters_z3() -> None:
    token = BackendCancellationToken()
    token.cancel()

    result = Z3Runner().run(
        _task(),
        policy=BackendExecutionPolicy(cancellation_token=token),
    )

    assert result.status is VerificationStatus.UNKNOWN
    assert result.execution is not None
    assert result.execution.status is BackendExecutionStatus.CANCELLED
    assert result.diagnostics[0].code == BACKEND_CANCELLED
    assert result.execution.backend_reason == "pre_cancelled"


@pytest.mark.parametrize(
    ("native_reason", "expected_status", "diagnostic_code"),
    (
        ("timeout", BackendExecutionStatus.TIMEOUT, BACKEND_TIMEOUT),
        (
            "max. resource limit exceeded",
            BackendExecutionStatus.RESOURCE_LIMIT,
            BACKEND_RESOURCE_LIMIT,
        ),
    ),
)
def test_z3_unknown_reason_is_normalized_to_generic_execution_status(
    monkeypatch: pytest.MonkeyPatch,
    native_reason: str,
    expected_status: BackendExecutionStatus,
    diagnostic_code: str,
) -> None:
    import toetra._backends.z3_backend.runner as runner_module

    class UnknownSolver:
        def set(self, **_options: object) -> None:
            pass

        def add(self, _expression: object) -> None:
            pass

        def check(self):
            return runner_module.z3.unknown

        def reason_unknown(self) -> str:
            return native_reason

    monkeypatch.setattr(runner_module.z3, "Solver", UnknownSolver)

    result = Z3Runner().run(_task())

    assert result.status is VerificationStatus.UNKNOWN
    assert result.execution is not None
    assert result.execution.status is expected_status
    assert result.execution.backend_reason == native_reason
    assert result.diagnostics[0].code == diagnostic_code


def test_z3_maps_generic_policy_to_native_solver_options(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import toetra._backends.z3_backend.runner as runner_module

    configured: dict[str, object] = {}

    class RecordingSolver:
        def set(self, **options: object) -> None:
            configured.update(options)

        def add(self, _expression: object) -> None:
            pass

        def check(self):
            return runner_module.z3.unknown

        def reason_unknown(self) -> str:
            return "incomplete"

    monkeypatch.setattr(runner_module.z3, "Solver", RecordingSolver)
    policy = BackendExecutionPolicy(
        timeout_ms=1_200,
        resources=BackendResourceLimits(
            max_backend_units=321,
            max_memory_mb=64,
        ),
        deterministic_seed=9,
        backend_options={"phase_selection": 2},
    )

    Z3Runner().run(_task(), policy=policy)

    assert 1 <= cast(int, configured["timeout"]) <= 1_200
    assert configured["rlimit"] == 321
    assert configured["max_memory"] == 64
    assert configured["random_seed"] == 9
    assert configured["phase_selection"] == 2


def test_generic_policy_fields_cannot_be_overridden_by_z3_options() -> None:
    policy = BackendExecutionPolicy(backend_options={"timeout": 999})

    with pytest.raises(ValueError, match="must not override"):
        Z3Runner().run(_task(), policy=policy)


def test_translation_time_consumes_the_same_total_timeout_budget() -> None:
    class SlowTranslator(Z3Translator):
        def translate(self, task: VerificationTaskIR2):
            time.sleep(0.01)
            return super().translate(task)

    result = Z3Runner(SlowTranslator()).run(
        _task(),
        policy=BackendExecutionPolicy(timeout_ms=1),
    )

    assert result.status is VerificationStatus.UNKNOWN
    assert result.execution is not None
    assert result.execution.status is BackendExecutionStatus.TIMEOUT
    assert result.execution.backend_reason == "translation_deadline_exceeded"


def test_technical_backend_failure_raises_structured_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import toetra._backends.z3_backend.runner as runner_module
    from toetra._backends.errors import BackendExecutionError

    class FailingSolver:
        def set(self, **_options: object) -> None:
            pass

        def add(self, _expression: object) -> None:
            pass

        def check(self):
            raise RuntimeError("boom")

    monkeypatch.setattr(runner_module.z3, "Solver", FailingSolver)

    with pytest.raises(BackendExecutionError) as captured:
        Z3Runner().run(_task())

    error = captured.value
    assert error.backend == "Z3"
    assert error.evidence.status is BackendExecutionStatus.ERROR
    assert error.evidence.backend_reason == "RuntimeError"
