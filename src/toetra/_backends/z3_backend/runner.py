from __future__ import annotations

import math
import threading
import time
from dataclasses import dataclass
from typing import Any, Mapping

import z3

from toetra._backends.diagnostics import (
    BackendDiagnosticSeverity,
    BackendResultDiagnostic,
)
from toetra._backends.errors import (
    BackendExecutionError,
    BackendExecutionPolicyError,
    BackendSymbolCollisionError,
    UnsupportedBackendRequirementsError,
)
from toetra._backends.execution import (
    BackendExecutionEvidence,
    BackendExecutionPolicy,
    BackendExecutionStatus,
)
from toetra._backends.results import VerificationResult, VerificationStatus
from toetra._backends.z3_backend.symbols import (
    Z3ModelOutputIdentity,
    compatibility_assignment_name,
    symbol_identity_metadata,
)
from toetra._backends.z3_backend.translator import Z3Translation, Z3Translator
from toetra._compiler.ir.ir2.enums import VerificationSemantics
from toetra._compiler.ir.ir2.dsl.nodes import VerificationTaskIR2
from toetra._language.vocabulary.backends import EnumBackend

Z3_VACUOUS_PROOF = "Z3_VACUOUS_PROOF"
Z3_INCONSISTENT_ASSUMPTIONS = "Z3_INCONSISTENT_ASSUMPTIONS"
BACKEND_TIMEOUT = "BACKEND_TIMEOUT"
BACKEND_RESOURCE_LIMIT = "BACKEND_RESOURCE_LIMIT"
BACKEND_CANCELLED = "BACKEND_CANCELLED"
BACKEND_UNKNOWN = "BACKEND_UNKNOWN"
BACKEND_DIAGNOSTIC_INCOMPLETE = "BACKEND_DIAGNOSTIC_INCOMPLETE"

_RESERVED_Z3_OPTIONS = frozenset({"timeout", "rlimit", "max_memory", "random_seed"})


@dataclass(frozen=True, init=False)
class Z3VerificationResult(VerificationResult):
    """Backward-compatible Z3 result built on the generic backend contract."""

    def __init__(
        self,
        *,
        status: VerificationStatus,
        solver_status: str,
        model: Mapping[str, Any] | None = None,
        message: str = "",
        diagnostics: tuple[BackendResultDiagnostic, ...] = (),
        metadata: Mapping[str, Any] | None = None,
        execution: BackendExecutionEvidence | None = None,
    ) -> None:
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "backend", EnumBackend.Z3)
        object.__setattr__(self, "backend_status", solver_status)
        object.__setattr__(self, "assignments", model)
        object.__setattr__(self, "message", message)
        object.__setattr__(self, "diagnostics", diagnostics)
        object.__setattr__(self, "metadata", metadata or {})
        object.__setattr__(self, "execution", execution)


@dataclass
class _ExecutionBudget:
    started_at: float
    deadline: float | None

    @classmethod
    def start(cls, policy: BackendExecutionPolicy) -> _ExecutionBudget:
        started_at = time.perf_counter()
        deadline = (
            started_at + policy.timeout_ms / 1000.0
            if policy.timeout_ms is not None
            else None
        )
        return cls(started_at=started_at, deadline=deadline)

    def duration_ms(self) -> float:
        return max(0.0, (time.perf_counter() - self.started_at) * 1000.0)

    def remaining_timeout_ms(self) -> int | None:
        if self.deadline is None:
            return None
        remaining = (self.deadline - time.perf_counter()) * 1000.0
        if remaining <= 0:
            return 0
        return max(1, math.ceil(remaining))


class _CancellationMonitor:
    def __init__(
        self,
        solver: z3.Solver,
        policy: BackendExecutionPolicy,
    ) -> None:
        self._solver = solver
        self._token = policy.cancellation_token
        self._stopped = threading.Event()
        self._thread: threading.Thread | None = None

    def __enter__(self) -> _CancellationMonitor:
        if self._token is not None:
            self._thread = threading.Thread(
                target=self._watch,
                name="toetra-backend-cancellation",
                daemon=True,
            )
            self._thread.start()
        return self

    def __exit__(self, *_args: object) -> None:
        self._stopped.set()
        if self._thread is not None:
            self._thread.join(timeout=0.1)

    def _watch(self) -> None:
        assert self._token is not None
        while not self._stopped.wait(0.01):
            if self._token.is_cancelled():
                self._solver.interrupt()
                return


class Z3Runner:
    """Execute an IR2 verification condition under the backend policy.

    The generic policy owns timeout, resource, cancellation and deterministic
    execution controls. Z3 only maps that contract to native solver options.
    """

    def __init__(self, translator: Z3Translator | None = None) -> None:
        self.translator = translator or Z3Translator()

    def translate(self, task: VerificationTaskIR2) -> Z3Translation:
        """Translate one task without creating or invoking a solver."""

        return self.translator.translate(task)

    def run(
        self,
        task: VerificationTaskIR2,
        *,
        policy: BackendExecutionPolicy | None = None,
    ) -> Z3VerificationResult:
        resolved_policy = policy or BackendExecutionPolicy()
        budget = _ExecutionBudget.start(resolved_policy)

        if resolved_policy.cancelled:
            return self._inconclusive_result(
                execution_status=BackendExecutionStatus.CANCELLED,
                backend_status="cancelled",
                reason="Execution was cancelled before backend translation.",
                backend_reason="pre_cancelled",
                policy=resolved_policy,
                budget=budget,
            )

        translation = self.translate(task)
        if budget.remaining_timeout_ms() == 0:
            return self._inconclusive_result(
                execution_status=BackendExecutionStatus.TIMEOUT,
                backend_status="timeout",
                reason="The backend execution budget expired during translation.",
                backend_reason="translation_deadline_exceeded",
                policy=resolved_policy,
                budget=budget,
                metadata=self._translation_metadata(translation),
            )

        solver = z3.Solver()
        self._configure_solver(solver, resolved_policy, budget)
        solver.add(translation.expression)

        try:
            with _CancellationMonitor(solver, resolved_policy):
                solver_result = solver.check()
        except Exception as error:
            raise BackendExecutionError(
                f"Z3 execution failed: {error}",
                backend=EnumBackend.Z3.value,
                evidence=self._execution_evidence(
                    BackendExecutionStatus.ERROR,
                    policy=resolved_policy,
                    budget=budget,
                    reason="The backend raised a technical execution error.",
                    backend_reason=type(error).__name__,
                ),
            ) from error

        if solver_result == z3.unknown:
            backend_reason = (
                solver.reason_unknown()
                if hasattr(solver, "reason_unknown")
                else "unknown"
            )
            execution_status = self._classify_unknown(
                backend_reason,
                policy=resolved_policy,
                budget=budget,
            )
            return self._inconclusive_result(
                execution_status=execution_status,
                backend_status="unknown",
                reason=self._reason_for_inconclusive(execution_status),
                backend_reason=backend_reason,
                policy=resolved_policy,
                budget=budget,
                metadata=self._translation_metadata(translation),
            )

        if solver_result == z3.sat:
            model = solver.model()
            status = self._status_for_sat(task.semantics)
            return Z3VerificationResult(
                status=status,
                solver_status="sat",
                model=self._assignments(translation, model),
                message=self._message_for(status),
                metadata=self._translation_metadata(translation),
                execution=self._execution_evidence(
                    BackendExecutionStatus.SAT,
                    policy=resolved_policy,
                    budget=budget,
                ),
            )

        if solver_result == z3.unsat:
            status = self._status_for_unsat(task.semantics)
            diagnostics = self._unsat_diagnostics(
                task,
                policy=resolved_policy,
                budget=budget,
            )
            return Z3VerificationResult(
                status=status,
                solver_status="unsat",
                model=None,
                message=self._message_for(status),
                diagnostics=diagnostics,
                metadata=self._translation_metadata(translation),
                execution=self._execution_evidence(
                    BackendExecutionStatus.UNSAT,
                    policy=resolved_policy,
                    budget=budget,
                ),
            )

        raise BackendExecutionError(
            f"Unsupported Z3 solver result: {solver_result}",
            backend=EnumBackend.Z3.value,
            evidence=self._execution_evidence(
                BackendExecutionStatus.ERROR,
                policy=resolved_policy,
                budget=budget,
                reason="The backend returned an unsupported native status.",
                backend_reason="unsupported_native_status",
            ),
        )

    @staticmethod
    def _configure_solver(
        solver: z3.Solver,
        policy: BackendExecutionPolicy,
        budget: _ExecutionBudget,
    ) -> None:
        if not hasattr(solver, "set"):
            return

        reserved = _RESERVED_Z3_OPTIONS.intersection(policy.backend_options)
        if reserved:
            names = ", ".join(sorted(reserved))
            raise BackendExecutionPolicyError(
                "Z3 backend options must not override generic execution policy "
                f"fields: {names}"
            )
        if hasattr(solver, "param_descrs"):
            descriptors = solver.param_descrs()
            supported_options = {
                str(descriptors.get_name(index)) for index in range(descriptors.size())
            }
            unsupported = set(policy.backend_options) - supported_options
            if unsupported:
                names = ", ".join(sorted(unsupported))
                raise BackendExecutionPolicyError(
                    f"Z3 does not recognize backend options: {names}"
                )
        try:
            remaining_timeout_ms = budget.remaining_timeout_ms()
            if remaining_timeout_ms is not None:
                solver.set(timeout=remaining_timeout_ms)
            if policy.resources.max_backend_units is not None:
                solver.set(rlimit=policy.resources.max_backend_units)
            if policy.resources.max_memory_mb is not None:
                solver.set(max_memory=policy.resources.max_memory_mb)
            if policy.deterministic_seed is not None:
                solver.set(random_seed=policy.deterministic_seed)
            if policy.backend_options:
                solver.set(**dict(policy.backend_options))
        except z3.Z3Exception as error:
            raise BackendExecutionPolicyError(
                f"Z3 rejected the backend execution policy: {error}"
            ) from error

    def _inconclusive_result(
        self,
        *,
        execution_status: BackendExecutionStatus,
        backend_status: str,
        reason: str,
        backend_reason: str | None,
        policy: BackendExecutionPolicy,
        budget: _ExecutionBudget,
        metadata: Mapping[str, Any] | None = None,
    ) -> Z3VerificationResult:
        diagnostic_codes = {
            BackendExecutionStatus.TIMEOUT: BACKEND_TIMEOUT,
            BackendExecutionStatus.RESOURCE_LIMIT: BACKEND_RESOURCE_LIMIT,
            BackendExecutionStatus.CANCELLED: BACKEND_CANCELLED,
            BackendExecutionStatus.UNKNOWN: BACKEND_UNKNOWN,
        }
        diagnostic = BackendResultDiagnostic(
            code=diagnostic_codes[execution_status],
            severity=BackendDiagnosticSeverity.WARNING,
            message=reason,
        )
        return Z3VerificationResult(
            status=VerificationStatus.UNKNOWN,
            solver_status=backend_status,
            model=None,
            message=reason,
            diagnostics=(diagnostic,),
            metadata=metadata,
            execution=self._execution_evidence(
                execution_status,
                policy=policy,
                budget=budget,
                reason=reason,
                backend_reason=backend_reason,
            ),
        )

    @staticmethod
    def _execution_evidence(
        status: BackendExecutionStatus,
        *,
        policy: BackendExecutionPolicy,
        budget: _ExecutionBudget,
        reason: str | None = None,
        backend_reason: str | None = None,
    ) -> BackendExecutionEvidence:
        return BackendExecutionEvidence(
            status=status,
            duration_ms=budget.duration_ms(),
            policy=policy.snapshot(),
            reason=reason,
            backend_reason=backend_reason,
        )

    @staticmethod
    def _classify_unknown(
        backend_reason: str,
        *,
        policy: BackendExecutionPolicy,
        budget: _ExecutionBudget,
    ) -> BackendExecutionStatus:
        normalized = backend_reason.lower()
        if policy.cancelled:
            return BackendExecutionStatus.CANCELLED
        if budget.remaining_timeout_ms() == 0 or "timeout" in normalized:
            return BackendExecutionStatus.TIMEOUT
        if any(
            token in normalized
            for token in ("rlimit", "resource", "memory", "max. memory")
        ):
            return BackendExecutionStatus.RESOURCE_LIMIT
        if "cancel" in normalized:
            return BackendExecutionStatus.CANCELLED
        return BackendExecutionStatus.UNKNOWN

    @staticmethod
    def _reason_for_inconclusive(status: BackendExecutionStatus) -> str:
        messages = {
            BackendExecutionStatus.TIMEOUT: (
                "Verification inconclusive: the backend execution timed out."
            ),
            BackendExecutionStatus.RESOURCE_LIMIT: (
                "Verification inconclusive: the backend resource limit was reached."
            ),
            BackendExecutionStatus.CANCELLED: (
                "Verification inconclusive: the backend execution was cancelled."
            ),
            BackendExecutionStatus.UNKNOWN: (
                "Verification inconclusive: Z3 returned unknown."
            ),
        }
        return messages[status]

    @staticmethod
    def _assignments(
        translation: Z3Translation,
        model: z3.ModelRef,
    ) -> dict[str, Any]:
        model_output_count = sum(
            isinstance(identity, Z3ModelOutputIdentity)
            for identity in translation.symbol_identities.values()
        )
        assignments: dict[str, Any] = {}
        for solver_name, variable in translation.variables.items():
            identity = translation.identity_for(solver_name)
            assignment_name = compatibility_assignment_name(
                identity,
                model_output_count=model_output_count,
            )
            if assignment_name in assignments:
                raise BackendSymbolCollisionError(
                    "Z3 assignment display-name collision for " f"{assignment_name!r}."
                )
            assignments[assignment_name] = model.eval(
                variable,
                model_completion=True,
            )
        return assignments

    @staticmethod
    def _translation_metadata(translation: Z3Translation) -> dict[str, Any]:
        model_output_count = sum(
            isinstance(identity, Z3ModelOutputIdentity)
            for identity in translation.symbol_identities.values()
        )
        assignment_symbols: dict[str, dict[str, Any]] = {}
        for solver_name, identity in translation.symbol_identities.items():
            assignment_name = compatibility_assignment_name(
                identity,
                model_output_count=model_output_count,
            )
            assignment_symbols[assignment_name] = {
                "solver_name": solver_name,
                "identity": symbol_identity_metadata(identity),
            }
        return {
            "z3_symbol_mapping": translation.serialized_symbol_mapping(),
            "assignment_symbol_mapping": assignment_symbols,
        }

    def _unsat_diagnostics(
        self,
        task: VerificationTaskIR2,
        *,
        policy: BackendExecutionPolicy,
        budget: _ExecutionBudget,
    ) -> tuple[BackendResultDiagnostic, ...]:
        if not task.assumptions:
            return ()

        assumptions_status = self._assumptions_status(
            task,
            policy=policy,
            budget=budget,
        )
        if assumptions_status is None:
            return (
                BackendResultDiagnostic(
                    code=BACKEND_DIAGNOSTIC_INCOMPLETE,
                    severity=BackendDiagnosticSeverity.INFO,
                    message=(
                        "The backend budget was exhausted before the optional "
                        "assumption-consistency diagnostic completed."
                    ),
                ),
            )
        if assumptions_status != z3.unsat:
            return ()

        if task.semantics is VerificationSemantics.REFUTATION:
            return (
                BackendResultDiagnostic(
                    code=Z3_VACUOUS_PROOF,
                    severity=BackendDiagnosticSeverity.WARNING,
                    message=(
                        "The property is proved only because the aggregated "
                        "assumptions are inconsistent; the admissible set is empty."
                    ),
                ),
            )

        return (
            BackendResultDiagnostic(
                code=Z3_INCONSISTENT_ASSUMPTIONS,
                severity=BackendDiagnosticSeverity.WARNING,
                message=(
                    "No witness can exist because the aggregated assumptions "
                    "are inconsistent."
                ),
            ),
        )

    def _assumptions_status(
        self,
        task: VerificationTaskIR2,
        *,
        policy: BackendExecutionPolicy,
        budget: _ExecutionBudget,
    ) -> z3.CheckSatResult | None:
        remaining_timeout_ms = budget.remaining_timeout_ms()
        if remaining_timeout_ms == 0 or policy.cancelled:
            return None
        translation = self.translator.translate_assumptions(task)
        solver = z3.Solver()
        self._configure_solver(solver, policy, budget)
        solver.add(translation.expression)
        with _CancellationMonitor(solver, policy):
            status = solver.check()
        return None if status == z3.unknown else status

    @staticmethod
    def _message_for(status: VerificationStatus) -> str:
        messages = {
            VerificationStatus.PROVED: (
                "Property proved: no counterexample exists under the encoded "
                "assumptions."
            ),
            VerificationStatus.COUNTEREXAMPLE: (
                "Property violated: Z3 found a counterexample under the encoded "
                "assumptions."
            ),
            VerificationStatus.WITNESS: (
                "Witness found: Z3 found an assignment satisfying the property "
                "and assumptions."
            ),
            VerificationStatus.NO_WITNESS: (
                "No witness exists under the encoded assumptions."
            ),
            VerificationStatus.UNKNOWN: (
                "Verification inconclusive: the backend returned unknown."
            ),
        }
        return messages[status]

    @staticmethod
    def _status_for_sat(
        semantics: VerificationSemantics,
    ) -> VerificationStatus:
        if semantics is VerificationSemantics.REFUTATION:
            return VerificationStatus.COUNTEREXAMPLE
        if semantics is VerificationSemantics.SATISFACTION:
            return VerificationStatus.WITNESS
        raise UnsupportedBackendRequirementsError(
            f"Unsupported verification semantics: {semantics}"
        )

    @staticmethod
    def _status_for_unsat(
        semantics: VerificationSemantics,
    ) -> VerificationStatus:
        if semantics is VerificationSemantics.REFUTATION:
            return VerificationStatus.PROVED
        if semantics is VerificationSemantics.SATISFACTION:
            return VerificationStatus.NO_WITNESS
        raise UnsupportedBackendRequirementsError(
            f"Unsupported verification semantics: {semantics}"
        )
