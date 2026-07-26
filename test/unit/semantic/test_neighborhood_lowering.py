from __future__ import annotations

from types import MappingProxyType

import pytest

from toetra._compiler.ast.nodes.assertion import AndNode, ComparisonNode
from toetra._compiler.ast.nodes.neighborhood import NeighborhoodMembershipNode
from toetra._compiler.ast.nodes.primitives import ConstantNode
from toetra._compiler.parser.errors import ParserError
from toetra._compiler.semantic.context.context import SemanticContext
from toetra._compiler.semantic.context.points import PointEnvironment
from toetra._compiler.semantic.context.scope import SemanticScope
from toetra._compiler.semantic.core.restrictions import NeighborhoodLowerer
from toetra._compiler.semantic.symbols.point import (
    PointBindingKind,
    PointFeatureSchema,
    PointSymbol,
)
from toetra._compiler.semantic.types.enums import EnumDataType
from test.unit.semantic.restriction_helpers import (
    inline_anchor,
    parse_and_validate,
)


def _source(*, metric: str = "Linf", eps: str = "0.1", candidate: str = "x1"):
    return f"""
        model := "model.joblib"
        target := score
        {inline_anchor()}

        [ROBUSTNESS]:
        forall {candidate}
        where {candidate} in neighborhood(
            of = x0,
            metric = {metric},
            eps = {eps}
        )
        => target[{candidate}] >= target[x0]
        """


def test_low_nbh_001_linf_expands_over_every_matching_feature() -> None:
    program = parse_and_validate(_source())
    semantic = program.body[0].semantic
    assert semantic is not None
    assert isinstance(semantic.restriction_root, AndNode)
    # Two inequalities per feature: candidate-anchor <= eps and reverse.
    assert len(semantic.restriction_root.operands) == 4
    assert all(
        isinstance(operand, ComparisonNode)
        for operand in semantic.restriction_root.operands
    )


def test_low_nbh_002_negative_epsilon_is_rejected() -> None:
    with pytest.raises(ParserError, match="epsilon must be non-negative"):
        parse_and_validate(_source(eps="-0.1"))


def test_low_nbh_003_non_numeric_epsilon_is_rejected() -> None:
    with pytest.raises(ParserError, match="epsilon must be a numeric constant"):
        parse_and_validate(_source(eps='"small"'))


def test_low_nbh_004_unsupported_metric_is_rejected() -> None:
    with pytest.raises(ParserError, match="supported metric: Linf"):
        parse_and_validate(_source(metric="L2"))


def test_low_nbh_005_candidate_and_anchor_must_be_distinct() -> None:
    point = PointSymbol(
        name="x0",
        binding_kind=PointBindingKind.UNIVERSAL,
        declaration=object(),
        feature_schema=MappingProxyType(
            {
                "a": PointFeatureSchema(
                    name="a",
                    dtype=EnumDataType.FLOAT,
                    nullable=False,
                )
            }
        ),
    )
    environment = PointEnvironment()
    environment.register_lexical(point, quantifier="forall")
    context = SemanticContext(
        type=SemanticScope.QUANTIFIER,
        variables=environment.compatibility_variables(),
        point_environment=environment,
        quantifier_chain=("forall",),
    )
    membership = NeighborhoodMembershipNode(
        candidate="x0",
        anchor="x0",
        metric="Linf",
        epsilon=ConstantNode(value=0.1, dtype=EnumDataType.FLOAT),
    )

    with pytest.raises(Exception, match="must be distinct points"):
        NeighborhoodLowerer().lower(membership, context)


def test_low_nbh_006_incompatible_feature_schemas_fail_structurally() -> None:
    anchor = PointSymbol(
        name="x0",
        binding_kind=PointBindingKind.INLINE_ANCHOR,
        declaration=object(),
        feature_schema=MappingProxyType(
            {
                "a": PointFeatureSchema(
                    name="a",
                    dtype=EnumDataType.FLOAT,
                    nullable=False,
                )
            }
        ),
    )
    candidate = PointSymbol(
        name="x1",
        binding_kind=PointBindingKind.UNIVERSAL,
        declaration=object(),
        feature_schema=MappingProxyType(
            {
                "other": PointFeatureSchema(
                    name="other",
                    dtype=EnumDataType.FLOAT,
                    nullable=False,
                )
            }
        ),
    )
    environment = PointEnvironment()
    environment.register(anchor)
    environment.register_lexical(candidate, quantifier="forall")
    context = SemanticContext(
        type=SemanticScope.QUANTIFIER,
        variables=environment.compatibility_variables(),
        point_environment=environment,
        quantifier_chain=("forall",),
    )
    membership = NeighborhoodMembershipNode(
        candidate="x1",
        anchor="x0",
        metric="Linf",
        epsilon=ConstantNode(value=0.1, dtype=EnumDataType.FLOAT),
    )

    with pytest.raises(Exception, match="incompatible feature schemas"):
        NeighborhoodLowerer().lower(membership, context)


def test_neighborhood_accepts_equivalent_schema_with_different_mapping_order() -> None:
    anchor = PointSymbol(
        name="x0",
        binding_kind=PointBindingKind.INLINE_ANCHOR,
        declaration=object(),
        feature_schema=MappingProxyType(
            {
                "b": PointFeatureSchema(
                    name="b",
                    dtype=EnumDataType.FLOAT,
                    nullable=False,
                ),
                "a": PointFeatureSchema(
                    name="a",
                    dtype=EnumDataType.FLOAT,
                    nullable=False,
                ),
            }
        ),
    )
    candidate = PointSymbol(
        name="x1",
        binding_kind=PointBindingKind.UNIVERSAL,
        declaration=object(),
        feature_schema=MappingProxyType(
            {
                "a": PointFeatureSchema(
                    name="a",
                    dtype=EnumDataType.FLOAT,
                    nullable=False,
                ),
                "b": PointFeatureSchema(
                    name="b",
                    dtype=EnumDataType.FLOAT,
                    nullable=False,
                ),
            }
        ),
    )
    environment = PointEnvironment()
    environment.register(anchor)
    environment.register_lexical(candidate, quantifier="forall")
    context = SemanticContext(
        type=SemanticScope.QUANTIFIER,
        variables=environment.compatibility_variables(),
        point_environment=environment,
        quantifier_chain=("forall",),
    )
    membership = NeighborhoodMembershipNode(
        candidate="x1",
        anchor="x0",
        metric="Linf",
        epsilon=ConstantNode(value=0.1, dtype=EnumDataType.FLOAT),
    )

    relation = NeighborhoodLowerer().lower(membership, context)

    assert isinstance(relation, AndNode)
    assert len(relation.operands) == 4
