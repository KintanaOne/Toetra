from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

from dsl.semantic.context.evaluations import ModelEvaluationRegistry
from dsl.semantic.context.points import LexicalPointFrame, PointEnvironment
from dsl.semantic.context.restrictions import (
    CanonicalRestrictionSemantics,
    RestrictionProvenance,
)
from dsl.semantic.context.scope import SemanticScope
from dsl.semantic.errors.errors import UnboundVariableError
from dsl.semantic.symbols.point import PointSymbol
from dsl.semantic.symbols.table import SymbolTable

if TYPE_CHECKING:
    from dsl.ast.nodes.assertion import LogicalNode
    from dsl.ast.nodes.domain import DomainNode
    from dsl.ast.nodes.expressions import RestrictionNode


@dataclass
class SemanticContext:
    """Semantic execution context produced by source-scope validation."""

    type: SemanticScope
    variables: dict[str, str]
    default_entity: Optional[str] = None
    domain: DomainNode | None = None
    neighborhood: Optional[object] = None
    quantifier: Optional[str] = None
    model_target: Optional[str] = None
    model_identity: Optional[str] = None
    symbol_table: SymbolTable = field(default_factory=SymbolTable)
    point_environment: PointEnvironment = field(default_factory=PointEnvironment)

    # Point-aware additions. ``default_entity`` remains a compatibility view.
    selected_default_point: PointSymbol | None = None
    binder_frames: tuple[LexicalPointFrame, ...] = ()
    quantifier_chain: tuple[str, ...] = ()
    restriction: RestrictionNode | None = None
    canonical_restriction: LogicalNode | None = None
    restriction_provenance: RestrictionProvenance | None = None
    restriction_semantics: CanonicalRestrictionSemantics | None = None
    source_scope_kind: str | None = None
    legacy_scope_compatibility: bool = False
    evaluation_registry: ModelEvaluationRegistry = field(
        default_factory=ModelEvaluationRegistry
    )

    def eligible_default_points(self) -> tuple[PointSymbol, ...]:
        """Return every visible model-input point eligible for short references."""
        return self.point_environment.all()

    def resolve_default_point(self, *, reference_kind: str) -> PointSymbol:
        """Apply the normative no-fallback default-point algorithm."""
        if self.selected_default_point is not None:
            return self.selected_default_point

        eligible = self.eligible_default_points()
        if len(eligible) == 1:
            return eligible[0]

        if not eligible:
            raise UnboundVariableError(
                f"Cannot resolve implicit {reference_kind}: no visible point"
            )

        names = ", ".join(point.name for point in eligible)
        raise UnboundVariableError(
            f"Ambiguous implicit {reference_kind}: visible points are [{names}]"
        )
