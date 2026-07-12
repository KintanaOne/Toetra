from __future__ import annotations

from dsl.ir.ir1.nodes import AndIR, LogicalIR, NotIR, QueryIR
from dsl.ir.ir2.enums import VerificationSemantics
from dsl.ir.ir2.nodes import AssumptionIR2, NNFFormulaIR2
from dsl.ir.normalization.nnf import NNFNormalizer


class VerificationConditionBuilder:
    """Build backend-neutral verification conditions.

    The DSL property remains stored unchanged in ``spec_formula``.

    The verification condition depends on the selected semantics:

    REFUTATION
        Search for a violation of P:

            Gamma AND NOT P

    SATISFACTION
        Search for a value satisfying P:

            Gamma AND P
    """

    def __init__(self, normalizer: NNFNormalizer | None = None):
        self.normalizer = normalizer or NNFNormalizer()

    def build_condition(
        self,
        spec_formula: NNFFormulaIR2,
        assumptions: tuple[AssumptionIR2, ...] = (),
        *,
        semantics: VerificationSemantics,
    ) -> NNFFormulaIR2:
        """Build and normalize the verification condition."""

        property_expression = self._property_expression(
            spec_formula,
            semantics,
        )

        pieces: list[LogicalIR] = [
            assumption.formula.expression for assumption in assumptions
        ]
        pieces.append(property_expression)

        if len(pieces) == 1:
            raw_expression = pieces[0]
        else:
            raw_expression = AndIR(operands=pieces)

        normalized = self.normalizer.normalize_query(QueryIR(expression=raw_expression))

        return NNFFormulaIR2(
            expression=normalized.expression,
        )

    def build_refutation_condition(
        self,
        spec_formula: NNFFormulaIR2,
        assumptions: tuple[AssumptionIR2, ...] = (),
    ) -> NNFFormulaIR2:
        """Build Gamma AND NOT P.

        Retained as a compatibility entry point for existing callers.
        """

        return self.build_condition(
            spec_formula,
            assumptions,
            semantics=VerificationSemantics.REFUTATION,
        )

    def build_satisfaction_condition(
        self,
        spec_formula: NNFFormulaIR2,
        assumptions: tuple[AssumptionIR2, ...] = (),
    ) -> NNFFormulaIR2:
        """Build Gamma AND P."""

        return self.build_condition(
            spec_formula,
            assumptions,
            semantics=VerificationSemantics.SATISFACTION,
        )

    def _property_expression(
        self,
        spec_formula: NNFFormulaIR2,
        semantics: VerificationSemantics,
    ) -> LogicalIR:
        if semantics is VerificationSemantics.REFUTATION:
            return NotIR(spec_formula.expression)

        if semantics is VerificationSemantics.SATISFACTION:
            return spec_formula.expression

        raise ValueError(f"Unsupported verification semantics: {semantics}")
