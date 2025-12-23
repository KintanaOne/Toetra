from lark import Tree, Token


def find_child(tree: Tree, name: str):
    """
    Return the first direct child Tree whose .data equals the given name.
    Returns None if not found.
    """
    if not isinstance(tree, Tree):
        return None
    for child in tree.children:
        if isinstance(child, Tree) and child.data == name:
            return child
    return None


def find_all(tree: Tree, name: str):
    """
    Return all subtrees in the AST whose .data equals the given name.
    """
    if not isinstance(tree, Tree):
        return []

    result = []
    for subtree in tree.iter_subtrees():
        if subtree.data == name:
            result.append(subtree)
    return result


def get_token_value(node):
    """
    Extract the Token value inside a Tree node.
    Works whether the node is:
    - a Token directly
    - a Tree containing exactly one Token
    - a Tree whose last child is a Token
    Returns None if no Token is found.
    """
    if isinstance(node, Token):
        return node.value

    if isinstance(node, Tree):
        # If the node wraps one child that is a token
        if len(node.children) == 1 and isinstance(node.children[0], Token):
            return node.children[0].value

        # Try scanning children from the end
        for child in reversed(node.children):
            if isinstance(child, Token):
                return child.value
            if isinstance(child, Tree) and len(child.children) == 1 and isinstance(child.children[0], Token):
                return child.children[0].value

    return None


def get_assignment_value_node(decl_tree: Tree):
    """
    Exemples : si model_declaration est un Tree contenant children
    [Token('IDENT', 'model'), Token(':=', ':='), Token('STRING', '"path"')]
    on retourne le dernier enfant (ou adapter selon ta grammaire).
    """
    if not isinstance(decl_tree, Tree):
        return None
    # Cherche le premier Token non-Tree dans children (ex: value)
    for c in decl_tree.children[::-2]:
        if isinstance(c, Token):
            return c
        if isinstance(c, Tree) and len(c.children) == 1 and isinstance(c.children[0], Token):
            return c.children[0]
    return None


def debug_tree(tree: Tree):
    """
    Convenience helper for debugging:
    Prints a pretty representation of the AST Tree.
    """
    if isinstance(tree, Tree):
        print(tree.pretty())
    else:
        print(tree)


def find_node(tree: Tree, name: str):
    """
    Depth-first search.
    Return the first Tree whose .data == name.
    """
    if not isinstance(tree, Tree):
        return None

    if tree.data == name:
        return tree

    for child in tree.children:
        if isinstance(child, Tree):
            found = find_node(child, name)
            if found is not None:
                return found

    return None


def find_all_nodes(tree: Tree, name: str):
    """
    Depth-first search.
    Return a list of all Tree nodes whose .data == name.
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
