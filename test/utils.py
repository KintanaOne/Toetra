from lark import Tree, Token
from typing import Optional, List, Union


AST = Tree
Node = Union[Tree, Token]


def find_child(tree: AST, name: str) -> Optional[AST]:
    """
    Return first direct child Tree matching name.
    """
    if not isinstance(tree, Tree):
        return None

    for child in tree.children:
        if isinstance(child, Tree) and child.data == name:
            return child

    return None

def find_node(tree: AST, name: str) -> Optional[AST]:
    """
    Depth-first search: first occurrence of node.
    """
    if not isinstance(tree, Tree):
        return None

    if tree.data == name:
        return tree

    for child in tree.children:
        if isinstance(child, Tree):
            found = find_node(child, name)
            if found:
                return found

    return None

def find_all_nodes(tree: AST, name: str) -> List[AST]:
    """
    Return all nodes matching name (DFS).
    """
    results = []

    if not isinstance(tree, Tree):
        return results

    if tree.data == name:
        results.append(tree)

    for child in tree.children:
        if isinstance(child, Tree):
            results.extend(find_all_nodes(child, name))

    return results

def get_token_value(node: Node):
    """
    Extract token value safely.
    """
    if isinstance(node, Token):
        return node.value

    if not isinstance(node, Tree):
        return None

    # 1. direct single-child case
    if len(node.children) == 1:
        child = node.children[0]
        if isinstance(child, Token):
            return child.value

    # 2. fallback scan
    for child in node.children:
        if isinstance(child, Token):
            return child.value

    return None

def get_assignment_value_node(decl_tree: AST):
    """
    Return RHS of assignment in a safe way.
    Assumes pattern: IDENT := VALUE
    """
    if not isinstance(decl_tree, Tree):
        return None

    children = decl_tree.children

    # find first Tree or Token after ':=' pattern
    seen_colon = False

    for child in children:
        if isinstance(child, Token) and child.value == ":=":
            seen_colon = True
            continue

        if seen_colon:
            return child

    return None


def debug_tree(tree: AST):
    if isinstance(tree, Tree):
        print(tree.pretty())
    else:
        print(tree)