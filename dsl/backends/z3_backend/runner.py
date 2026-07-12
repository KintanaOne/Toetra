from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

import z3

from dsl.backends.z3_backend.translator import Z3Translator
from dsl.ir.ir2.enums import VerificationSemantics
from dsl.ir.ir2.nodes import VerificationTaskIR2


class VerificationStatus(str, Enum):
    """Interpreted result of a FORML verification task."""

    PROVED = "proved"
    COUNTEREXAMPLE = "counterexample"
    WITNESS = "witness"
    NO_WITNESS = "no_witness"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Z3VerificationResult:
    """Normalized result returned by the Z3 backend."""

    status: VerificationStatus
    solver_status: str
    model: dict[str, Any] | None = None


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
            return Z3VerificationResult(
                status=VerificationStatus.UNKNOWN,
                solver_status="unknown",
                model=None,
            )

        if solver_result == z3.sat:
            model = solver.model()

            return Z3VerificationResult(
                status=self._status_for_sat(task.semantics),
                solver_status="sat",
                model={
                    name: model.eval(
                        variable,
                        model_completion=True,
                    )
                    for name, variable in translation.variables.items()
                },
            )

        if solver_result == z3.unsat:
            return Z3VerificationResult(
                status=self._status_for_unsat(task.semantics),
                solver_status="unsat",
                model=None,
            )

        raise RuntimeError(f"Unsupported Z3 solver result: {solver_result}")

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
