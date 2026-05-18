from dataclasses import dataclass
from typing import Optional

from dsl.semantic.types.enums import EnumDataType


@dataclass
class Symbol:
    """
    Semantic variable representation.

    Example:
        x     -> anchor
        x'    -> perturbation
        _x    -> symbolic variable
    """

    # ---------------------------------------------
    # Public symbol name
    # ---------------------------------------------

    name: str

    # ---------------------------------------------
    # Semantic role
    #
    # Examples:
    # - anchor
    # - perturbation
    # - symbolic
    # ---------------------------------------------

    kind: str

    # ---------------------------------------------
    # Optional semantic type
    # (future typing system)
    # ---------------------------------------------

    dtype: EnumDataType | None = None

    # ---------------------------------------------
    # Optional origin AST node
    # ---------------------------------------------

    origin: Optional[object] = None
