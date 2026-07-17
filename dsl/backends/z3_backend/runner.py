from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

import z3

from dsl.backends.diagnostics import (
    BackendDiagnosticSeverity,
    BackendResultDiagnostic,
)
from dsl.backends.results import VerificationResult, VerificationStatus
from dsl.backends.z3_backend.symbols import (
    Z3ModelOutputIdentity,
    compatibility_assignment_name,
    symbol_identity_metadata,
)
from dsl.backends.z3_backend.translator import Z3Translation, Z3Translator
from dsl.ir.ir2.enums import VerificationSemantics
from dsl.ir.ir2.nodes import VerificationTaskIR2
from dsl.language.vocabulary.backends import EnumBackend

Z3_VACUOUS_PROOF = "Z3_VACUOUS_PROOF"
Z3_INCONSISTENT_ASSUMPTIONS = "Z3_INCONSISTENT_ASSUMPTIONS"


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
    ) -> None:
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "backend", EnumBackend.Z3)
        object.__setattr__(self, "backend_status", solver_status)
        object.__setattr__(self, "assignments", model)
        object.__setattr__(self, "message", message)
        object.__setattr__(self, "diagnostics", diagnostics)
        object.__setattr__(self, "metadata", metadata or {})


class Z3Runner:
    """Execute a translated IR2 verification condition with Z3.

    The interpretation of SAT and UNSAT depends on the verification semantics:

    REFUTATION
        SAT     -> COUNTEREXAMPLE
        UNSAT   -> PROVED

    SATISFACTION
        SAT     -> WITNESS
        UNSAT   -> NO_WITNESS
    """

    def __init__(self, translator: Z3Translator | None = None) -> None:
        self.translator = translator or Z3Translator()

    def run(self, task: VerificationTaskIR2) -> Z3VerificationResult:
        translation = self.translator.translate(task)

        solver = z3.Solver()
        solver.add(translation.expression)

        solver_result = solver.check()

        if solver_result == z3.unknown:
            status = VerificationStatus.UNKNOWN
            return Z3VerificationResult(
                status=status,
                solver_status="unknown",
                model=None,
                message=self._message_for(status),
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
            )

        if solver_result == z3.unsat:
            status = self._status_for_unsat(task.semantics)
            diagnostics = self._unsat_diagnostics(task)
            return Z3VerificationResult(
                status=status,
                solver_status="unsat",
                model=None,
                message=self._message_for(status),
                diagnostics=diagnostics,
                metadata=self._translation_metadata(translation),
            )

        raise RuntimeError(f"Unsupported Z3 solver result: {solver_result}")

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
                raise RuntimeError(
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
    ) -> tuple[BackendResultDiagnostic, ...]:
        if not task.assumptions or self._assumptions_status(task) != z3.unsat:
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

    def _assumptions_status(self, task: VerificationTaskIR2) -> z3.CheckSatResult:
        translation = self.translator.translate_assumptions(task)
        solver = z3.Solver()
        solver.add(translation.expression)
        return solver.check()

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
                "Verification inconclusive: Z3 returned unknown."
            ),
        }
        return messages[status]

    def _status_for_sat(
        self,
        semantics: VerificationSemantics,
    ) -> VerificationStatus:
        if semantics is VerificationSemantics.REFUTATION:
            return VerificationStatus.COUNTEREXAMPLE

        if semantics is VerificationSemantics.SATISFACTION:
            return VerificationStatus.WITNESS

        raise ValueError(f"Unsupported verification semantics: {semantics}")

    def _status_for_unsat(
        self,
        semantics: VerificationSemantics,
    ) -> VerificationStatus:
        if semantics is VerificationSemantics.REFUTATION:
            return VerificationStatus.PROVED

        if semantics is VerificationSemantics.SATISFACTION:
            return VerificationStatus.NO_WITNESS

        raise ValueError(f"Unsupported verification semantics: {semantics}")
