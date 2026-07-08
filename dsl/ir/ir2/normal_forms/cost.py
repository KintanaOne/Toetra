from __future__ import annotations

from dataclasses import dataclass

from dsl.ir.ir1.nodes import AndIR, ComparisonIR, LogicalIR, NotIR, OrIR, ProblemIR
from dsl.ir.ir2.nodes import ModelConstraintIR2


@dataclass(frozen=True)
class NormalFormCost:
    cnf_units: int
    dnf_units: int


class NormalFormCostEstimator:
    """Cheap structural estimates for CNF/DNF distribution size.

    The estimates are intentionally conservative and backend-neutral. They are
    used by the selector to avoid exponential blowups before conversion.
    """

    def estimate(self, expr: LogicalIR) -> NormalFormCost:
        return NormalFormCost(
            cnf_units=self.estimate_cnf_units(expr),
            dnf_units=self.estimate_dnf_units(expr),
        )

    def estimate_cnf_units(self, expr: LogicalIR) -> int:
        if isinstance(expr, (ComparisonIR, ProblemIR, ModelConstraintIR2)):
            return 1
        if isinstance(expr, NotIR):
            return 1
        if isinstance(expr, AndIR):
            return sum(self.estimate_cnf_units(op) for op in expr.operands)
        if isinstance(expr, OrIR):
            product = 1
            for op in expr.operands:
                product *= self.estimate_cnf_units(op)
            return product
        return 1

    def estimate_dnf_units(self, expr: LogicalIR) -> int:
        if isinstance(expr, (ComparisonIR, ProblemIR, ModelConstraintIR2)):
            return 1
        if isinstance(expr, NotIR):
            return 1
        if isinstance(expr, OrIR):
            return sum(self.estimate_dnf_units(op) for op in expr.operands)
        if isinstance(expr, AndIR):
            product = 1
            for op in expr.operands:
                product *= self.estimate_dnf_units(op)
            return product
        return 1
