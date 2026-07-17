from __future__ import annotations

from typing import TYPE_CHECKING

from dsl.ast.nodes.expressions import (
    AtExprNode,
    CheckAtExprNode,
    DirectExprNode,
    PairwiseExprNode,
    QuantifierBinderNode,
    QuantifierExprNode,
    RestrictionNode,
)
from dsl.semantic.context.context import SemanticContext
from dsl.semantic.context.points import PointEnvironment
from dsl.semantic.context.restrictions import (
    RestrictionOrigin,
    RestrictionProvenance,
)
from dsl.semantic.context.scope import SemanticScope
from dsl.semantic.errors.errors import InvalidPropertyError
from dsl.semantic.runtime.tracer import ValidationTracer
from dsl.semantic.rules.migration import (
    LEGACY_AT_MESSAGE,
    LEGACY_CHECK_AT_MESSAGE,
    LEGACY_PAIRWISE_MESSAGE,
)
from dsl.semantic.symbols.point import (
    PointBindingKind,
    PointFeatureSchema,
    PointSymbol,
    frozen_mapping,
)

if TYPE_CHECKING:
    from model.schema.model_schema import ModelSchema


class LHSValidator:
    """Build one composed point-aware semantic context for a property."""

    def __init__(self, tracer=None, model_schema: ModelSchema | None = None):
        self.tracer = tracer or ValidationTracer()
        self.model_schema = model_schema

    def validate(
        self,
        lhs,
        point_environment: PointEnvironment | None = None,
    ) -> SemanticContext:
        self.tracer.log(f"Validating LHS: {lhs}")
        environment = point_environment or PointEnvironment()

        if isinstance(lhs, DirectExprNode):
            return self._validate_direct(environment)
        if isinstance(lhs, CheckAtExprNode):
            return self._validate_check_at(lhs, environment)
        if isinstance(lhs, AtExprNode):
            return self._validate_at(lhs, environment)
        if isinstance(lhs, PairwiseExprNode):
            return self._validate_pairwise(lhs, environment)
        if isinstance(lhs, QuantifierExprNode):
            return self._validate_quantifier(lhs, environment)

        raise InvalidPropertyError(f"Unknown LHS type: {type(lhs)}")

    def _validate_direct(self, environment: PointEnvironment) -> SemanticContext:
        return self._new_context(
            type=SemanticScope.POINTWISE,
            environment=environment,
            source_scope_kind="direct",
        )

    def _validate_check_at(
        self,
        lhs: CheckAtExprNode,
        environment: PointEnvironment,
    ) -> SemanticContext:
        if not lhs.variable:
            raise InvalidPropertyError("Missing variable in check_at")

        selected = environment.resolve(lhs.variable)
        if selected is None:
            if environment.global_anchors():
                raise InvalidPropertyError(
                    f"check_at selects unknown anchor '{lhs.variable}'"
                )
            raise InvalidPropertyError(
                LEGACY_CHECK_AT_MESSAGE.format(name=lhs.variable)
            )
        if not selected.is_anchor:
            raise InvalidPropertyError(
                f"check_at point '{lhs.variable}' is not an anchor"
            )

        return self._new_context(
            type=SemanticScope.POINTWISE,
            environment=environment,
            selected_default_point=selected,
            source_scope_kind="check_at",
            legacy_scope_compatibility=False,
        )

    def _validate_at(
        self,
        lhs: AtExprNode,
        environment: PointEnvironment,
    ) -> SemanticContext:
        if not lhs.variable:
            raise InvalidPropertyError("Missing variable in at")

        if lhs.local_membership is not None:
            anchor = environment.resolve(lhs.variable)
            if anchor is None:
                raise InvalidPropertyError(
                    f"at selects undeclared anchor '{lhs.variable}'"
                )
            if not anchor.is_anchor or (
                anchor.binding_kind is PointBindingKind.LEGACY_ANCHOR
            ):
                raise InvalidPropertyError(
                    f"at point '{lhs.variable}' is not a declared concrete anchor"
                )

            membership = lhs.local_membership
            candidate_name = membership.candidate
            if candidate_name == anchor.name:
                raise InvalidPropertyError(
                    "Neighborhood candidate and anchor must be distinct points"
                )
            if environment.exists(candidate_name):
                raise InvalidPropertyError(
                    f"Scope variable '{candidate_name}' collides with a visible point"
                )

            generated_binder = QuantifierBinderNode(
                quantifier="forall",
                variables=[candidate_name],
            )
            generated_binder.source_span = lhs.source_span
            candidate = PointSymbol(
                name=candidate_name,
                binding_kind=PointBindingKind.UNIVERSAL,
                declaration=generated_binder,
                lexical_depth=1,
                feature_schema=self._point_schema(),
            )
            environment.register_lexical(
                candidate,
                quantifier="forall",
                source_span=lhs.source_span,
                generated=True,
            )

            restriction = RestrictionNode(expression=membership)
            restriction.source_span = lhs.source_span
            provenance = RestrictionProvenance(
                origin=RestrictionOrigin.AT_SUGAR,
                source_span=lhs.source_span,
            )

            return self._new_context(
                type=SemanticScope.QUANTIFIER,
                environment=environment,
                quantifier="forall",
                quantifier_chain=("forall",),
                restriction=restriction,
                restriction_provenance=provenance,
                source_scope_kind="at_sugar",
            )

        raise InvalidPropertyError(LEGACY_AT_MESSAGE.format(name=lhs.variable))

    def _validate_pairwise(
        self,
        lhs: PairwiseExprNode,
        environment: PointEnvironment,
    ) -> SemanticContext:
        del environment
        raise InvalidPropertyError(LEGACY_PAIRWISE_MESSAGE.format(pair=lhs.pair))

    def _validate_quantifier(
        self,
        lhs: QuantifierExprNode,
        environment: PointEnvironment,
    ) -> SemanticContext:
        if not lhs.binders:
            raise InvalidPropertyError("Missing quantifier binder")

        canonical_quantifiers: list[str] = []
        bound_names: set[str] = set()

        for binder in lhs.binders:
            quantifier = self._normalize_quantifier(binder)
            if not binder.variables:
                raise InvalidPropertyError("Missing quantified identifier")

            clause_names: set[str] = set()
            for variable in binder.variables:
                if variable in clause_names:
                    raise InvalidPropertyError(
                        f"Duplicate quantified point '{variable}' in binder list"
                    )
                clause_names.add(variable)

                if variable in bound_names:
                    raise InvalidPropertyError(
                        f"Quantified point '{variable}' shadows an outer binder"
                    )

                existing = environment.resolve(variable)
                if existing is not None:
                    if existing.is_anchor:
                        raise InvalidPropertyError(
                            f"Quantified point '{variable}' collides with a global anchor"
                        )
                    raise InvalidPropertyError(f"Point '{variable}' is already visible")

                depth = len(environment.lexical_frames()) + 1
                binding_kind = (
                    PointBindingKind.UNIVERSAL
                    if quantifier == "forall"
                    else PointBindingKind.EXISTENTIAL
                )
                point = PointSymbol(
                    name=variable,
                    binding_kind=binding_kind,
                    declaration=binder,
                    lexical_depth=depth,
                    feature_schema=self._point_schema(),
                )
                environment.register_lexical(
                    point,
                    quantifier=quantifier,
                    source_span=binder.source_span,
                )
                canonical_quantifiers.append(quantifier)
                bound_names.add(variable)

        compatibility_quantifier = (
            canonical_quantifiers[0] if len(canonical_quantifiers) == 1 else None
        )

        provenance = (
            RestrictionProvenance(
                origin=RestrictionOrigin.WHERE,
                source_span=lhs.restriction.source_span,
            )
            if lhs.restriction is not None
            else None
        )

        return self._new_context(
            type=SemanticScope.QUANTIFIER,
            environment=environment,
            domain=lhs.domain,
            quantifier=compatibility_quantifier,
            quantifier_chain=tuple(canonical_quantifiers),
            restriction=lhs.restriction,
            restriction_provenance=provenance,
            source_scope_kind="quantifier",
        )

    def _new_context(
        self,
        *,
        type: SemanticScope,
        environment: PointEnvironment,
        selected_default_point: PointSymbol | None = None,
        domain=None,
        neighborhood=None,
        quantifier: str | None = None,
        quantifier_chain: tuple[str, ...] = (),
        restriction=None,
        restriction_provenance=None,
        source_scope_kind: str | None = None,
        legacy_scope_compatibility: bool = False,
    ) -> SemanticContext:
        eligible = environment.all()
        default_point = selected_default_point
        if default_point is None and len(eligible) == 1:
            default_point = eligible[0]

        context = SemanticContext(
            type=type,
            variables=environment.compatibility_variables(),
            default_entity=default_point.name if default_point is not None else None,
            domain=domain,
            neighborhood=neighborhood,
            quantifier=quantifier,
            point_environment=environment,
            selected_default_point=selected_default_point,
            binder_frames=environment.lexical_frames(),
            quantifier_chain=quantifier_chain,
            restriction=restriction,
            restriction_provenance=restriction_provenance,
            source_scope_kind=source_scope_kind,
            legacy_scope_compatibility=legacy_scope_compatibility,
        )

        for point in environment.all():
            context.symbol_table.register(point)

        return context

    def _normalize_quantifier(self, binder: QuantifierBinderNode) -> str:
        quantifier = binder.quantifier.strip()
        quantifier = {"∀": "forall", "∃": "exists"}.get(quantifier, quantifier)
        if quantifier not in {"forall", "exists"}:
            raise InvalidPropertyError(f"Unknown quantifier '{quantifier}'")
        return quantifier

    def _point_schema(self):
        if self.model_schema is None:
            return None
        return frozen_mapping(
            {
                name: PointFeatureSchema(
                    name=feature.name,
                    dtype=feature.dtype,
                    nullable=feature.nullable,
                )
                for name, feature in self.model_schema.features.items()
            }
        )
