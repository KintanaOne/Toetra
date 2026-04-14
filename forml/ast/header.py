from lark import Tree
from forml.core.utils import find_child
from forml.core.ast_utils import node_value, clean_string


# ============================================================================
# HEADER PARSING
# ============================================================================

def get_header(tree: Tree) -> Tree:
    return find_child(tree, "header")


def parse_model(tree: Tree) -> str:
    """
    model := "path"
    """
    return clean_string(node_value(find_child(get_header(tree), "model_declaration")))


def parse_target(tree: Tree) -> str:
    """
    target := Column
    """
    return clean_string(node_value(find_child(get_header(tree), "target_declaration")))