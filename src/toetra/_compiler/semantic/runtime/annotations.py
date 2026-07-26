from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from toetra._compiler.semantic.context.context import SemanticContext
from toetra._compiler.semantic.symbols.table import SemanticSymbol, SymbolTable
from toetra._compiler.semantic.types.enums import EnumArithmeticClass, EnumDataType

if TYPE_CHECKING:
    from toetra._compiler.semantic.context.evaluations import ModelEvaluationIdentity
    from toetra._compiler.semantic.symbols.point import PointSymbol
    from toetra._models.schema.output_schema import EnumOutputObservable, ModelLabel


@dataclass
class SemanticAnnotations:
    """
    SemanticAnnotations

    Purpose:
    --------
    Runtime semantic cache attached to AST nodes.

    IMPORTANT:
    ----------
    This structure is:
    - NOT the source of truth
    - NOT an IR layer
    - NOT a semantic graph

    It is ONLY a semantic cache used to:
    - avoid recomputation
    - propagate semantic resolution
    - expose normalized semantic metadata
    - support later IR lowering phases

    Notes:
    ------
    The same structure may be attached to:
    - PropertyNode
    - AttributeNode
    - future semantic-capable AST nodes
    """

    # ─────────────────────────────────────────────
    # Global semantic artifacts
    # ─────────────────────────────────────────────

    context: SemanticContext | None = None
    """
    Root semantic execution context produced by LHSValidator.
    """

    symbol_table: SymbolTable | None = None
    """
    Symbol registry available in the semantic scope.
    """

    assertion_root: Any | None = None
    """Bound source assertion before restriction semantics are applied."""

    restriction_root: Any | None = None
    """Canonical bound restriction, when the source contains one."""

    logical_root: Any | None = None
    """
    Root validated logical expression.
    """

    verification_root: Any | None = None
    """Canonical query body selected from source quantifier semantics."""

    verification_semantics: str | None = None
    """Either ``refutation`` or ``satisfaction`` for restricted properties."""

    # ─────────────────────────────────────────────
    # Local resolution results
    # ─────────────────────────────────────────────

    resolved_entity: str | None = None
    """
    Final resolved entity.

    Examples:
        x
        x'
        _x
    """

    resolved_path: list[str] | None = None
    """
    Fully resolved attribute path.

    Example:
        ["x'", "target", "score"]
    """

    resolved_type: str | None = None
    """
    Backward-compatible normalized semantic type label.

    New code should prefer ``inferred_dtype`` for scalar typing. The string
    field remains available because existing IR1 and diagnostics consume it.
    """

    inferred_dtype: EnumDataType | None = None
    """Scalar data type inferred during semantic validation, when known."""

    arithmetic_class: EnumArithmeticClass | None = None
    """Structural arithmetic family required by this scalar expression."""

    resolved_symbol: SemanticSymbol | None = None
    """
    Reference to a symbol-table entry.
    """

    resolved_point: PointSymbol | None = None
    """Exact input point selected for an indexed or short model reference."""

    resolved_evaluation: ModelEvaluationIdentity | None = None
    """Interned ``(model, point, output)`` evaluation identity, when applicable."""

    resolved_evaluations: tuple[ModelEvaluationIdentity, ...] = ()
    """Ordered model evaluations resolved for one multi-point semantic sugar."""

    resolved_output_observable: EnumOutputObservable | None = None
    """Framework-neutral public observable selected from a model output."""

    resolved_label: ModelLabel | None = None
    """Canonical user-facing class label selected by an observable, if any."""

    arithmetic_allowed: bool | None = None
    """Whether this scalar observable may participate in arithmetic."""

    ordering_allowed: bool | None = None
    """Whether this scalar observable may participate in ordered comparison."""

    resolved_candidate_point: PointSymbol | None = None
    """Resolved neighborhood candidate point, when applicable."""

    resolved_anchor_point: PointSymbol | None = None
    """Resolved neighborhood anchor point, when applicable."""

    lowered_expression: Any | None = None
    """Canonical expression generated from one source-level sugar node."""

    # ─────────────────────────────────────────────
    # Scope metadata
    # ─────────────────────────────────────────────

    scope_type: str | None = None
    """
    Scope classification.

    Examples:
        pointwise
        local
        pairwise
        quantifier
    """

    constraints: list[Any] = field(default_factory=list)
    """
    Additional semantic constraints collected during validation.
    """

    # ─────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────

    def is_resolved(self) -> bool:
        """
        Returns True if semantic resolution occurred.
        """

        return self.resolved_entity is not None or self.resolved_symbol is not None
