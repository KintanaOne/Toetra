from __future__ import annotations

from dsl.ir.ir1.nodes import AndIR, NotIR, QueryIR
from dsl.ir.ir2.nodes import AssumptionIR2, NNFFormulaIR2
from dsl.ir.normalization.nnf import NNFNormalizer


class VerificationConditionBuilder:
    """Builds the backend-neutral verification condition Γ ∧ ¬P.

    The DSL property P remains the spec formula. The verification condition is
    derived internally using refutation semantics.
    """

    def __init__(self, normalizer: NNFNormalizer | None = None):
        self.normalizer = normalizer or NNFNormalizer()

    def build_refutation_condition(
        self,
        spec_formula: NNFFormulaIR2,
        assumptions: tuple[AssumptionIR2, ...] = (),
    ) -> NNFFormulaIR2:
        pieces = [assumption.formula.expression for assumption in assumptions]
        pieces.append(NotIR(spec_formula.expression))

        if len(pieces) == 1:
            raw_expr = pieces[0]
        else:
            raw_expr = AndIR(operands=pieces)

        normalized = self.normalizer.normalize_query(QueryIR(expression=raw_expr))
        return NNFFormulaIR2(expression=normalized.expression)
