from dataclasses import dataclass, field
from typing import Any

from dsl.semantic.context.context import SemanticContext
from dsl.semantic.symbols.symbol import Symbol
from dsl.semantic.symbols.table import SymbolTable


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

    logical_root: Any | None = None
    """
    Root validated logical expression.
    """

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
    Semantic role/type inferred during resolution.

    Examples:
        anchor
        perturbation
        symbolic
    """

    resolved_symbol: Symbol | None = None
    """
    Reference to SymbolTable Symbol object.
    """

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
