from lark import Tree


def unwrap_logic(node: Tree) -> Tree:
    """
    Remove syntax-level wrappers specific to logic.
    """
    while node.data in {"assertion", "logic_group"}:
        node = node.children[0]

    return node