from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

import z3

from dsl.backends.z3_backend.translator import Z3Translator
from dsl.ir.ir2.enums import VerificationSemantics
from dsl.ir.ir2.nodes import VerificationTaskIR2


class VerificationStatus(str, Enum):
    PROVED = "proved"
    COUNTEREXAMPLE = "counterexample"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Z3VerificationResult:
    status: VerificationStatus
    solver_status: str
    model: dict[str, Any] | None = None


class Z3Runner:
    def __init__(self, translator: Z3Translator | None = None) -> None:
        self.translator = translator or Z3Translator()

    def run(self, task: VerificationTaskIR2) -> Z3VerificationResult:
        if task.semantics != VerificationSemantics.REFUTATION:
            raise NotImplementedError(
                "Minimal Z3Runner only supports refutation semantics."
            )

        translation = self.translator.translate(task)

        solver = z3.Solver()
        solver.add(translation.expression)

        result = solver.check()

        if result == z3.unsat:
            return Z3VerificationResult(
                status=VerificationStatus.PROVED,
                solver_status="unsat",
                model=None,
            )

        if result == z3.sat:
            model = solver.model()
            return Z3VerificationResult(
                status=VerificationStatus.COUNTEREXAMPLE,
                solver_status="sat",
                model={
                    name: model.eval(var, model_completion=True)
                    for name, var in translation.variables.items()
                },
            )

        return Z3VerificationResult(
            status=VerificationStatus.UNKNOWN,
            solver_status="unknown",
            model=None,
        )
