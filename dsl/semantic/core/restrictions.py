from __future__ import annotations

from typing import TYPE_CHECKING

from dsl.ast.nodes.assertion import (
    AndNode,
    ComparisonNode,
    ImplicationNode,
    LogicalNode,
    NotNode,
)
from dsl.ast.nodes.neighborhood import NeighborhoodMembershipNode
from dsl.ast.nodes.primitives import AttributeNode, BinaryArithmeticNode
from dsl.language.vocabulary.operators import (
    EnumArithmeticOperator,
    EnumComparisonOperator,
)
from dsl.semantic.context.restrictions import (
    CanonicalRestrictionSemantics,
    VerificationSemantics,
)
from dsl.semantic.errors.errors import InvalidPropertyError
from dsl.semantic.runtime.annotations import SemanticAnnotations
from dsl.semantic.core.scalar_typing import ScalarTypeAnalyzer
from dsl.semantic.types.enums import EnumDataType

if TYPE_CHECKING:
    from dsl.ast.nodes.source import SourceSpan
    from dsl.semantic.context.context import SemanticContext
    from model.schema.model_schema import ModelSchema


_NUMERIC_DTYPES = frozenset({EnumDataType.INT, EnumDataType.FLOAT})


class NeighborhoodLowerer:
    """Validate and lower one structured neighborhood into logical constraints."""

    def __init__(self, model_schema: ModelSchema | None = None):
        self.model_schema = model_schema
        self.scalar_analyzer = ScalarTypeAnalyzer(model_schema=model_schema)

    def lower(
        self,
        membership: NeighborhoodMembershipNode,
        context: SemanticContext,
    ) -> LogicalNode:
        candidate = context.point_environment.resolve(membership.candidate)
        if candidate is None:
            raise InvalidPropertyError(
                f"Unknown neighborhood candidate '{membership.candidate}'"
            )

        anchor = context.point_environment.resolve(membership.anchor)
        if anchor is None:
            raise InvalidPropertyError(
                f"Unknown neighborhood anchor '{membership.anchor}'"
            )

        if candidate is anchor or candidate.name == anchor.name:
            raise InvalidPropertyError(
                "Neighborhood candidate and anchor must be distinct points"
            )

        metric = membership.metric.strip()
        if metric.lower() != "linf":
            raise InvalidPropertyError(
                f"Neighborhood metric '{metric}' is not executable in the initial "
                "profile; supported metric: Linf"
            )

        epsilon_analysis = self.scalar_analyzer.analyze(membership.epsilon)
        if not epsilon_analysis.is_numeric_constant:
            dtype = epsilon_analysis.dtype
            dtype_label = dtype.value if dtype is not None else "unknown"
            raise InvalidPropertyError(
                "Neighborhood epsilon must be a numeric constant expression, "
                f"got {dtype_label}"
            )

        epsilon_value = epsilon_analysis.constant_value
        if epsilon_value < 0:
            raise InvalidPropertyError(
                f"Neighborhood epsilon must be non-negative, got {epsilon_value}"
            )

        feature_names = self._validate_feature_schemas(candidate, anchor)
        comparisons: list[LogicalNode] = []
        for feature_name in feature_names:
            comparisons.extend(
                self._feature_constraints(
                    candidate=candidate.name,
                    anchor=anchor.name,
                    feature=feature_name,
                    epsilon=membership.epsilon,
                    source_span=membership.source_span,
                )
            )

        if not comparisons:
            raise InvalidPropertyError(
                "Neighborhood lowering requires at least one numeric model feature"
            )

        relation = AndNode(operands=comparisons)
        relation.source_span = membership.source_span

        if membership.semantic is None:
            membership.semantic = SemanticAnnotations()
        membership.semantic.resolved_candidate_point = candidate
        membership.semantic.resolved_anchor_point = anchor
        membership.semantic.lowered_expression = relation

        return relation

    def _validate_feature_schemas(self, candidate, anchor) -> tuple[str, ...]:
        candidate_schema = candidate.feature_schema
        anchor_schema = anchor.feature_schema

        if candidate_schema is None or anchor_schema is None:
            raise InvalidPropertyError(
                "Neighborhood lowering requires a model feature schema"
            )

        candidate_names = tuple(candidate_schema)
        anchor_names = tuple(anchor_schema)
        if set(candidate_names) != set(anchor_names):
            raise InvalidPropertyError(
                "Neighborhood points have incompatible feature schemas: "
                f"candidate={list(candidate_names)}, anchor={list(anchor_names)}"
            )

        for name in candidate_names:
            candidate_feature = candidate_schema[name]
            anchor_feature = anchor_schema[name]
            if (
                candidate_feature.dtype is not anchor_feature.dtype
                or candidate_feature.nullable != anchor_feature.nullable
            ):
                raise InvalidPropertyError(
                    f"Neighborhood feature schema mismatch for '{name}'"
                )
            if candidate_feature.dtype not in _NUMERIC_DTYPES:
                raise InvalidPropertyError(
                    "Linf neighborhood supports numeric model features only; "
                    f"feature '{name}' has type {candidate_feature.dtype.value}"
                )

        return candidate_names

    def _feature_constraints(
        self,
        *,
        candidate: str,
        anchor: str,
        feature: str,
        epsilon,
        source_span: SourceSpan | None,
    ) -> tuple[ComparisonNode, ComparisonNode]:
        forward = ComparisonNode(
            left=BinaryArithmeticNode(
                left=_attribute(candidate, feature, source_span),
                operator=EnumArithmeticOperator.SUB,
                right=_attribute(anchor, feature, source_span),
            ),
            op=EnumComparisonOperator.LTE,
            right=epsilon,
        )
        backward = ComparisonNode(
            left=BinaryArithmeticNode(
                left=_attribute(anchor, feature, source_span),
                operator=EnumArithmeticOperator.SUB,
                right=_attribute(candidate, feature, source_span),
            ),
            op=EnumComparisonOperator.LTE,
            right=epsilon,
        )
        _set_span(forward.left, source_span)
        _set_span(backward.left, source_span)
        _set_span(forward, source_span)
        _set_span(backward, source_span)
        return forward, backward


class RestrictionSemanticsBuilder:
    """Build language and verification formulas from a bound restriction."""

    def build(
        self,
        *,
        context: SemanticContext,
        assertion: LogicalNode,
    ) -> CanonicalRestrictionSemantics | None:
        restriction = context.canonical_restriction
        if restriction is None:
            return None
        if not isinstance(restriction, LogicalNode):
            raise InvalidPropertyError(
                "Canonical restriction is not a logical expression"
            )
        if not context.quantifier_chain:
            raise InvalidPropertyError(
                "A restricted property requires at least one quantifier"
            )
        if context.restriction_provenance is None:
            raise InvalidPropertyError(
                "Restricted property is missing source provenance"
            )

        quantifier = context.quantifier_chain[-1]
        source_span = context.restriction_provenance.source_span

        if quantifier == "forall":
            language_formula = ImplicationNode(
                left=restriction,
                right=assertion,
            )
            verification_body = AndNode(
                operands=[
                    restriction,
                    NotNode(operand=assertion),
                ]
            )
            semantics = VerificationSemantics.REFUTATION
        elif quantifier == "exists":
            language_formula = AndNode(operands=[restriction, assertion])
            verification_body = language_formula
            semantics = VerificationSemantics.SATISFACTION
        else:
            raise InvalidPropertyError(
                f"Unsupported restriction quantifier '{quantifier}'"
            )

        _set_span(language_formula, source_span)
        _set_span(verification_body, source_span)

        return CanonicalRestrictionSemantics(
            quantifier=quantifier,
            restriction=restriction,
            assertion=assertion,
            language_formula=language_formula,
            verification_body=verification_body,
            verification_semantics=semantics,
            provenance=context.restriction_provenance,
        )


def _attribute(entity: str, feature: str, source_span: SourceSpan | None):
    node = AttributeNode(
        entity=entity,
        feature=feature,
        path=[entity, feature],
    )
    node.source_span = source_span
    return node


def _set_span(node, source_span: SourceSpan | None) -> None:
    if hasattr(node, "source_span"):
        node.source_span = source_span
