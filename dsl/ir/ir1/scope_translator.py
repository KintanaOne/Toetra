from __future__ import annotations

from typing import Any

from dsl.ast.nodes.domain import (
    DomainFiniteValueNode,
    FiniteSetDomainNode,
    IntervalDomainNode,
    SymbolLiteralNode,
)
from dsl.ast.nodes.expressions import (
    AtExprNode,
    CheckAtExprNode,
    DirectExprNode,
    PairwiseExprNode,
    QuantifierExprNode,
)
from dsl.ast.nodes.primitives import ConstantNode, NameRefNode

from dsl.ir.ir1.nodes import (
    AttributeExpressionIR,
    ConstantExpressionIR,
    DomainEntryIR,
    DomainFiniteValueIR,
    DomainIR,
    FiniteSetDomainIR,
    IntervalDomainIR,
    NeighborhoodIR,
    PointBindingIR,
    QuantifierBinderIR,
    RestrictionIR,
    ScopeProvenanceIR,
    ScopeIR,
    SymbolLiteralIR,
)
from dsl.ir.ir1.points import PointIRRegistry, copy_source_span
from dsl.ir.ir1.scalar_translator import ScalarExpressionTranslator
from dsl.semantic.context.context import SemanticContext
from dsl.semantic.symbols.point import PointBindingKind, PointSymbol


class ScopeTranslator:
    """
    Translate AST scope expressions into IR scope representation.

    Responsibility:
        ExpressionNode -> ScopeIR

    This class does not translate logical assertions.
    """

    def __init__(
        self,
        scalar_translator: ScalarExpressionTranslator | None = None,
        point_registry: PointIRRegistry | None = None,
    ) -> None:
        self.point_registry = point_registry or PointIRRegistry()
        self.scalar_translator = scalar_translator or ScalarExpressionTranslator(
            self.point_registry
        )

    def translate(
        self,
        scope,
        *,
        context: SemanticContext | None = None,
        restriction: RestrictionIR | None = None,
    ) -> ScopeIR:
        if context is not None:
            return self._translate_semantic_context(
                scope,
                context=context,
                restriction=restriction,
            )

        if isinstance(scope, DirectExprNode):
            return ScopeIR(
                kind="pointwise",
                variables={},
                neighborhood=None,
                domain=None,
            )

        if isinstance(scope, AtExprNode):
            return self._translate_at(scope)

        if isinstance(scope, PairwiseExprNode):
            return self._translate_pairwise(scope)

        if isinstance(scope, CheckAtExprNode):
            return self._translate_check_at(scope)

        if isinstance(scope, QuantifierExprNode):
            return self._translate_quantifier(scope)

        raise ValueError(f"Unsupported scope node type: {type(scope)}")

    def _translate_semantic_context(
        self,
        scope,
        *,
        context: SemanticContext,
        restriction: RestrictionIR | None,
    ) -> ScopeIR:
        for frame in context.binder_frames:
            self.point_registry.register_frame(frame)

        points = tuple(
            self.point_registry.point(point)
            for point in context.point_environment.all()
        )
        binders = tuple(
            QuantifierBinderIR(
                quantifier=frame.quantifier,
                point=self.point_registry.point(frame.point),
                source_span=copy_source_span(frame.source_span),
                generated=frame.generated,
            )
            for frame in context.binder_frames
        )

        default_point: PointBindingIR | None = None
        if context.default_entity is not None:
            semantic_default = context.point_environment.resolve(context.default_entity)
            if semantic_default is not None:
                default_point = self.point_registry.point(semantic_default)

        quantifier = self._compatibility_quantifier(context)

        return ScopeIR(
            kind=context.type.value,
            variables={
                point.name: self._compatibility_role(point)
                for point in context.point_environment.all()
            },
            neighborhood=self._translate_neighborhood(context.neighborhood),
            domain=self._translate_domain(context.domain),
            quantifier=quantifier,
            points=points,
            binders=binders,
            restriction=restriction,
            default_point=default_point,
            provenance=ScopeProvenanceIR(
                source_kind=context.source_scope_kind,
                source_span=copy_source_span(getattr(scope, "source_span", None)),
                legacy_compatibility=context.legacy_scope_compatibility,
            ),
        )

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
        quantifier = self._normalize_quantifier(scope.quantifier)

        return ScopeIR(
            kind="quantifier",
            variables={scope.variable: "symbolic"},
            neighborhood=None,
            domain=self._translate_domain(scope.domain),
            quantifier=quantifier,
        )

    @staticmethod
    def _compatibility_quantifier(context: SemanticContext) -> str | None:
        """Project homogeneous chains to the legacy single quantifier field."""
        chain = context.quantifier_chain
        if not chain:
            return context.quantifier
        first = chain[0]
        if all(quantifier == first for quantifier in chain):
            return first
        return None

    @staticmethod
    def _compatibility_role(point: PointSymbol) -> str:
        if point.binding_kind is PointBindingKind.PERTURBATION:
            return "perturbation"
        return point.kind

    # ------------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_quantifier(quantifier: str) -> str:
        """Normalize a source quantifier to its canonical IR representation."""

        raw_quantifier = quantifier.strip()

        normalized = {
            "∀": "forall",
            "∃": "exists",
        }.get(
            raw_quantifier,
            raw_quantifier.lower(),
        )

        if normalized not in {"forall", "exists"}:
            raise ValueError(
                f"Unsupported quantifier during IR1 translation: " f"{quantifier!r}"
            )

        return normalized

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

        entries: list[DomainEntryIR] = []

        for entry in domain.entries:
            subject = self.scalar_translator.translate(entry.subject)
            if not isinstance(subject, AttributeExpressionIR):
                raise TypeError("Domain subject did not lower to an attribute IR")

            entries.append(
                DomainEntryIR(
                    entity=subject.entity,
                    feature=subject.feature,
                    constraint=self._translate_domain_constraint(entry.constraint),
                    dtype=subject.dtype,
                    point=subject.point,
                )
            )

        return DomainIR(entries=tuple(entries))

    def _translate_domain_constraint(self, constraint):
        if isinstance(constraint, IntervalDomainNode):
            return IntervalDomainIR(
                lower=self.scalar_translator.translate(constraint.lower),
                upper=self.scalar_translator.translate(constraint.upper),
                lower_boundary=constraint.lower_boundary,
                upper_boundary=constraint.upper_boundary,
            )

        if isinstance(constraint, FiniteSetDomainNode):
            return FiniteSetDomainIR(
                values=tuple(
                    self._translate_finite_value(value) for value in constraint.values
                )
            )

        raise TypeError(f"Unsupported domain constraint: {type(constraint).__name__}")

    def _translate_finite_value(
        self,
        node: DomainFiniteValueNode,
    ) -> DomainFiniteValueIR:
        """Translate one finite-set value to its restricted IR representation.

        Finite sets intentionally accept only:

            - scalar constants;
            - unquoted symbolic category literals.

        Attribute and target expressions are valid scalar expressions for other
        constructs, such as interval bounds, but are not finite-set values.
        """

        if isinstance(node, SymbolLiteralNode):
            return SymbolLiteralIR(name=node.name)

        if isinstance(node, ConstantNode):
            translated = self.scalar_translator.translate(node)
            if not isinstance(translated, ConstantExpressionIR):
                raise TypeError("Finite-set constant did not lower to a constant IR")
            return translated

        if isinstance(node, NameRefNode):
            raise TypeError(
                f"Unresolved finite-set name reached IR1 translation: {node.name!r}"
            )

        raise TypeError(f"Unsupported finite-set value: {type(node).__name__}")
