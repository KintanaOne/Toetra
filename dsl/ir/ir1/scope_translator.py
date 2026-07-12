
from __future__ import annotations

from typing import Any

from dsl.ast.nodes.domain import (
    FiniteSetDomainNode,
    IntervalDomainNode,
    SymbolLiteralNode,
)
from dsl.ast.nodes.expressions import (
    AtExprNode,
    CheckAtExprNode,
    PairwiseExprNode,
    QuantifierExprNode,
)
from dsl.ast.nodes.primitives import AttributeNode, ConstantNode, TargetRefNode

from dsl.ir.ir1.nodes import (
    AttributeExpressionIR,
    ConstantExpressionIR,
    DomainEntryIR,
    DomainIR,
    FiniteSetDomainIR,
    IntervalDomainIR,
    NeighborhoodIR,
    ScopeIR,
    SymbolLiteralIR,
    TargetExpressionIR,
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
            variables={scope.variable: "symbolic"},
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
            entries=tuple(
                DomainEntryIR(
                    entity=entry.subject.entity,
                    feature=entry.subject.feature,
                    constraint=self._translate_domain_constraint(entry.constraint),
                )
                for entry in domain.entries
            )
        )

    def _translate_domain_constraint(self, constraint):
        if isinstance(constraint, IntervalDomainNode):
            return IntervalDomainIR(
                lower=self._translate_scalar_leaf(constraint.lower),
                upper=self._translate_scalar_leaf(constraint.upper),
                lower_boundary=constraint.lower_boundary,
                upper_boundary=constraint.upper_boundary,
            )

        if isinstance(constraint, FiniteSetDomainNode):
            return FiniteSetDomainIR(
                values=tuple(
                    SymbolLiteralIR(value.name)
                    if isinstance(value, SymbolLiteralNode)
                    else self._translate_scalar_leaf(value)
                    for value in constraint.values
                )
            )

        raise TypeError(
            f"Unsupported domain constraint: {type(constraint).__name__}"
        )

    def _translate_scalar_leaf(self, node):
        if isinstance(node, ConstantNode):
            return ConstantExpressionIR(value=node.value, dtype=node.dtype)

        if isinstance(node, AttributeNode):
            entity = node.entity
            if node.semantic is not None and node.semantic.resolved_entity is not None:
                entity = node.semantic.resolved_entity
            return AttributeExpressionIR(entity=entity, feature=node.feature)

        if isinstance(node, TargetRefNode):
            return TargetExpressionIR(name=node.name)

        raise TypeError(f"Unsupported scalar domain leaf: {type(node).__name__}")


