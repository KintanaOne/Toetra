from __future__ import annotations

from typing import Any

from dsl.ast.nodes.expressions import (
    AtExprNode,
    CheckAtExprNode,
    PairwiseExprNode,
    QuantifierExprNode,
)

from dsl.ir.ir1.nodes import (
    ScopeIR,
    NeighborhoodIR,
    DomainIR,
)


class ScopeTranslator:
    """
    Translate AST scope expressions into IR scope representation.

    Responsibility:
        ExpressionNode -> ScopeIR

    This class does not translate logical assertions.
    """

    def translate(self, scope) -> ScopeIR:
        if isinstance(scope, AtExprNode):
            return self._translate_at(scope)

        if isinstance(scope, PairwiseExprNode):
            return self._translate_pairwise(scope)

        if isinstance(scope, CheckAtExprNode):
            return self._translate_check_at(scope)

        if isinstance(scope, QuantifierExprNode):
            return self._translate_quantifier(scope)

        raise ValueError(f"Unsupported scope node type: {type(scope)}")

    # ------------------------------------------------------------------
    # AT
    # ------------------------------------------------------------------

    def _translate_at(self, scope: AtExprNode) -> ScopeIR:
        return ScopeIR(
            kind="local",
            variables={
                scope.variable: "anchor",
                f"{scope.variable}'": "perturbation",
            },
            neighborhood=self._translate_neighborhood(scope.neighborhood),
            domain=self._translate_domain(scope.domain),
        )

    # ------------------------------------------------------------------
    # PAIRWISE
    # ------------------------------------------------------------------

    def _translate_pairwise(self, scope: PairwiseExprNode) -> ScopeIR:
        return ScopeIR(
            kind="pairwise",
            variables={
                scope.left: "anchor",
                scope.right: "perturbation",
            },
            neighborhood=self._translate_neighborhood(scope.neighborhood),
            domain=self._translate_domain(scope.domain),
        )

    # ------------------------------------------------------------------
    # CHECK_AT
    # ------------------------------------------------------------------

    def _translate_check_at(self, scope: CheckAtExprNode) -> ScopeIR:
        return ScopeIR(
            kind="pointwise",
            variables={
                scope.variable: "anchor",
            },
            neighborhood=None,
            domain=None,
        )

    # ------------------------------------------------------------------
    # QUANTIFIER
    # ------------------------------------------------------------------

    def _translate_quantifier(self, scope: QuantifierExprNode) -> ScopeIR:
        return ScopeIR(
            kind="quantifier",
            # Keep the semantic binding introduced by LHSValidator.
            # Quantified formulas bind implicit feature access such as `a <= 1`
            # to `_x.a`, so IR must declare the `_x` symbolic variable.
            variables={"_x": "symbolic"},
            neighborhood=None,
            domain=self._translate_domain(scope.domain),
        )

    # ------------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------------

    def _translate_neighborhood(self, neighborhood) -> NeighborhoodIR | None:
        if neighborhood is None:
            return None

        args_dict: dict[str, Any] = {arg.key: arg.value for arg in neighborhood.args}

        eps = args_dict.get("eps")

        if eps is None:
            raise ValueError("Neighborhood must specify 'eps' parameter")

        try:
            eps = float(eps)
        except (TypeError, ValueError) as e:
            raise ValueError(f"Invalid neighborhood eps value: {eps}") from e

        return NeighborhoodIR(
            metric=neighborhood.metric,
            eps=eps,
            args=args_dict,
        )

    def _translate_domain(self, domain) -> DomainIR | None:
        if domain is None:
            return None

        return DomainIR(
            name=domain.name,
            args={"values": domain.values},
        )
