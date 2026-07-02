from __future__ import annotations

from lark import Tree, Token

from dsl.builder.core.lark_types import LarkNode, LarkTree

# ============================================================================
# TREE NAVIGATION HELPERS
# ============================================================================
# These functions provide safe and reusable traversal utilities over Lark trees.
# They are intentionally generic and contain NO DSL-specific logic.


def find_child(tree: LarkTree, name: str) -> LarkTree | None:
    """
    Return the first direct child Tree matching a given rule name.

    This is a shallow search (1 level only).
    """
    for child in tree.children:
        if isinstance(child, Tree) and child.data == name:
            return child
    return None


def find_node(tree: LarkTree, name: str) -> LarkTree | None:
    """
    Depth-first search (DFS) to find the first occurrence of a node.

    Stops at the first match.
    """
    if tree.data == name:
        return tree

    for child in tree.children:
        if isinstance(child, Tree):
            found = find_node(child, name)
            if found:
                return found

    return None


def find_all_nodes(tree: LarkTree, name: str) -> list[LarkTree]:
    """
    Return ALL nodes matching a given rule name using DFS.
    """
    results: list[LarkTree] = []

    if tree.data == name:
        results.append(tree)

    for child in tree.children:
        if isinstance(child, Tree):
            results.extend(find_all_nodes(child, name))

    return results


# ============================================================================
# TOKEN EXTRACTION
# ============================================================================
# Centralized logic to safely extract values from mixed Tree/Token structures.


def get_token_value(node: LarkNode) -> str | None:
    """
    Extract a string value from a Lark node.

    Strategy:
    - If Token -> return value directly
    - If Tree -> recursively scan children until a Token is found

    This avoids positional assumptions in the grammar.
    """
    if isinstance(node, Token):
        return node.value

    if isinstance(node, Tree):
        for child in node.children:
            val = get_token_value(child)
            if val is not None:
                return val

    return None


def extract_direct_token(node: Tree) -> str | None:
    """
    Extract token only from immediate children (no deep recursion).
    More stable for grammar nodes like quantifier.
    """
    for child in node.children:
        if isinstance(child, Token):
            return child.value
        if isinstance(child, Tree):
            # only go one level deeper for wrapper nodes
            for sub in child.children:
                if isinstance(sub, Token):
                    return sub.value
    return None


def get_node_name_or_value(node: Tree) -> str | None:
    """
    Extract semantic value from a node:
    - Token -> value
    - Tree with no children -> data (rule name)
    - Tree with children -> recurse
    """

    from lark import Token, Tree

    if node is None:
        return None

    if isinstance(node, Token):
        return node.value

    if isinstance(node, Tree):
        # ✔ leaf rule (comme "exists")
        if len(node.children) == 0:
            return node.data

        for child in node.children:
            v = get_node_name_or_value(child)
            if v is not None:
                return v

    return None


# ============================================================================
# ASSIGNMENT EXTRACTION
# ============================================================================


def get_assignment_value_node(decl_tree: LarkTree) -> LarkNode | None:
    """
    Extract the RHS (right-hand side) of an assignment.

    Expected pattern:
        IDENT := VALUE

    The function scans for ':=' and returns the first node after it.

    This is syntax-driven and does NOT interpret semantics.
    """
    seen_assign = False

    for child in decl_tree.children:
        if isinstance(child, Token) and child.value == ":=":
            seen_assign = True
            continue

        if seen_assign:
            return child

    return None


# ============================================================================
# DEBUG UTILITIES
# ============================================================================


def debug_tree(tree: LarkTree) -> None:
    """
    Pretty-print a Lark tree for debugging purposes.
    """
    print(tree.pretty())
