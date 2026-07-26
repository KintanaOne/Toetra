from __future__ import annotations

from toetra._compiler.ir.ir2.context import IR2BuildContext
from toetra._compiler.ir.ir2.enums import NormalFormKind
from toetra._compiler.ir.ir2.dsl.nodes import NNFFormulaIR2
from toetra._compiler.ir.ir2.normal_forms.cost import NormalFormCostEstimator


class NormalFormSelector:
    """Selects the IR2 verification-condition form.

    CNF/DNF are optimizations. NNF is the guaranteed fallback.
    """

    def __init__(self, cost_estimator: NormalFormCostEstimator | None = None):
        self.cost_estimator = cost_estimator or NormalFormCostEstimator()

    def select(
        self,
        verification_condition: NNFFormulaIR2,
        context: IR2BuildContext | None = None,
    ) -> NormalFormKind:
        context = context or IR2BuildContext()
        cost = self.cost_estimator.estimate(verification_condition.expression)

        if context.preferred_normal_form is not None:
            if self._is_reasonable(context.preferred_normal_form, cost, context):
                return context.preferred_normal_form
            if not context.allow_nnf_fallback:
                return context.preferred_normal_form
            return NormalFormKind.NNF

        # Refutation conditions often describe a candidate counterexample, so DNF
        # is useful for branch/scenario exploration when it is small enough.
        if cost.dnf_units <= context.max_distribution_size:
            return NormalFormKind.DNF

        if cost.cnf_units <= context.max_distribution_size:
            return NormalFormKind.CNF

        return NormalFormKind.NNF

    def _is_reasonable(
        self,
        form: NormalFormKind,
        cost,
        context: IR2BuildContext,
    ) -> bool:
        if form == NormalFormKind.NNF:
            return True
        if form == NormalFormKind.CNF:
            return cost.cnf_units <= context.max_distribution_size
        if form == NormalFormKind.DNF:
            return cost.dnf_units <= context.max_distribution_size
        return False
