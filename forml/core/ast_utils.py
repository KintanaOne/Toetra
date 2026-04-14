from typing import Optional, Union
from lark import Tree, Token

from forml.core.utils import get_token_value

# ============================================================================
# AST CORE HELPERS
# ============================================================================

def node_value(node: Union[Tree, Token, None]) -> Optional[str]:
    """

    Goal :
    - uniform AST Lark reading
    - éviter toute logique positionnelle ailleurs

    Règle :
    - Token => value
    - Tree => descend récursivement jusqu'à trouver une valeur exploitable
    """
    if node is None:
        return None

    if isinstance(node, Token):
        return node.value

    if isinstance(node, Tree):
        if not node.children:
            return str(node.data)

        for c in node.children:
            v = node_value(c)
            if v is not None:
                return v

    return None


def clean_string(v: Optional[str]) -> Optional[str]:
    """
    remove quotes "..." ou '...'
    """
    if v is None:
        return None

    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
        return v[1:-1]

    return v


def extract_attribute(node: Tree) -> Optional[dict]:
    """
    Generic attribute extraction (future-proof).

    Supports:
    - age
    - x0.age
    - user.age
    - xyz.feature
    - a.b.c.d

    Design:
    - last element = feature
    - preceding = entity (or namespace)
    """

    if node is None:
        return None

    identifiers = [
        get_token_value(child)
        for child in node.children
        if isinstance(child, Tree) and child.data == "identifier"
    ]

    if not identifiers:
        return None

    return {
        "kind": "attribute",
        "entity": identifiers[0] if len(identifiers) > 1 else None,
        "feature": identifiers[-1] if len(identifiers) > 1 else identifiers[0],
        "path": identifiers
    }

def parse_value(node: Tree) -> dict:
    raw = get_token_value(node)
    cleaned = clean_string(raw)

    # int
    try:
        value = int(cleaned)
        return {
            "kind": "constant", 
            "value": value, 
            "dtype": "int"
            }
    except ValueError:
        pass

    # float
    try:
        value = float(cleaned)
        return {
            "kind": "constant", 
            "value": value, 
            "dtype": "float"
            }
    except ValueError:
        pass

    # fallback string
    return {
        "kind": "constant",
        "value": cleaned,
        "dtype": "string"
    }

def parse_attribute(node: Tree) -> dict:
    attr = extract_attribute(node)

    if attr is None:
        return {
            "kind": "attribute",
            "entity": None,
            "feature": None
        }

    return extract_attribute(node)


def unwrap_single_child(node: Tree) -> Tree:
    """
    Remove structural wrappers with a single child.

    Purely syntactic:
    - no domain assumption
    - safe everywhere
    """
    while (
        isinstance(node, Tree)
        and len(node.children) == 1
        and isinstance(node.children[0], Tree)
    ):
        node = node.children[0]

    return node