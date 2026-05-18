from __future__ import annotations

from lark import Tree, Token
from typing import Union

# ============================================================================
# LARK TYPE ALIASES
# ============================================================================
# These aliases centralize Lark typing across the builder.
# This avoids repetition and improves readability + maintainability.

LarkNode = Union[Tree, Token]
LarkTree = Tree
