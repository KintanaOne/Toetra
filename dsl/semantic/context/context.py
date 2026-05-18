from dataclasses import dataclass, field
from typing import Optional

from dsl.semantic.context.scope import SemanticScope
from dsl.semantic.symbols.table import SymbolTable


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

    domain: Optional[object] = None
    neighborhood: Optional[object] = None
    quantifier: Optional[str] = None

    # ---------------------------------------------
    # NEW:
    # Symbol table for semantic lookup
    # ---------------------------------------------

    symbol_table: SymbolTable = field(default_factory=SymbolTable)
