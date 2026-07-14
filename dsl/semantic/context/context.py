from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

from dsl.semantic.context.scope import SemanticScope
from dsl.semantic.symbols.table import SymbolTable

if TYPE_CHECKING:
    from dsl.ast.nodes.domain import DomainNode


@dataclass
class SemanticContext:
    """
    Semantic execution context produced by LHS validation.

    Responsibilities:
    - define semantic scope
    - store variable bindings
    - define implicit entity resolution
    - expose SymbolTable to downstream semantic passes
    """

    # ---------------------------------------------
    # Semantic scope type
    # ---------------------------------------------

    type: SemanticScope

    # ---------------------------------------------
    # Variable roles
    # Example:
    # {
    #     "x": "anchor",
    #     "x'": "perturbation"
    # }
    # ---------------------------------------------

    variables: dict

    # ---------------------------------------------
    # Default implicit entity
    # Example:
    #     a <= 1
    #
    # becomes:
    #     x'.a <= 1
    # ---------------------------------------------

    default_entity: Optional[str] = None

    # ---------------------------------------------
    # Optional semantic metadata
    # ---------------------------------------------

    domain: DomainNode | None = None
    neighborhood: Optional[object] = None
    quantifier: Optional[str] = None
    model_target: Optional[str] = None

    # ---------------------------------------------
    # NEW:
    # Symbol table for semantic lookup
    # ---------------------------------------------

    symbol_table: SymbolTable = field(default_factory=SymbolTable)
