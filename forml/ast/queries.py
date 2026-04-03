from lark import Token, Tree
from typing import Optional, List, Union

from test.utils import find_child, find_all_nodes, find_node


def clean_string(value: str) -> str:
    if value is None:
        return None

    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]

    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]

    return value

# ----------------------------------------------------------------------------------------------------------------------
#                                             TOKEN EXTRACTION
# ----------------------------------------------------------------------------------------------------------------------

def get_token_value(node: Union[Tree, Token]) -> Optional[str]:
    """
    Robust extraction of a semantic value from a Lark node.
    Handles:
    - Token
    - Tree with Token children
    - Leaf Tree (like 'forall')
    """
    if node is None:
        return None

    # Case 1: direct Token
    if isinstance(node, Token):
        return node.value

    # Case 2: Tree
    if isinstance(node, Tree):

        # 🔥 IMPORTANT: leaf node (like "forall")
        if not node.children:
            return str(node.data)

        # Recursive search
        for child in node.children:
            value = get_token_value(child)
            if value is not None:
                return value

    return None


# ----------------------------------------------------------------------------------------------------------------------
#                                             HEADER QUERIES
# ----------------------------------------------------------------------------------------------------------------------

def get_header(tree: Tree) -> Optional[Tree]:
    """Return the header node."""
    return find_child(tree, "header")


def get_model_declaration(tree: Tree) -> Optional[Tree]:
    """Return model declaration node."""
    header = get_header(tree)
    return find_child(header, "model_declaration") if header else None


def get_target_declaration(tree: Tree) -> Optional[Tree]:
    """Return target declaration node."""
    header = get_header(tree)
    return find_child(header, "target_declaration") if header else None


# ----------------------------------------------------------------------------------------------------------------------
#                                             PROPERTY QUERIES
# ----------------------------------------------------------------------------------------------------------------------

def get_all_properties(tree: Tree) -> List[Tree]:
    """
    Return all property nodes.

    IMPORTANT:
    A FORML program can contain multiple properties.
    """
    return find_all_nodes(tree, "property_section")


def get_property_type(prop: Tree) -> Optional[str]:
    """Extract property type (e.g., ROBUSTNESS, SAFETY)."""
    return get_token_value(find_node(prop, "property_type"))


def get_property_expression(prop: Tree) -> Optional[Tree]:
    """Return property expression node (forall / at / check_at / pairwise)."""
    return find_node(prop, "property_expr")


def get_property_mode(prop: Tree) -> Optional[str]:
    """
    Identify the type of property expression.

    Returns:
        - "forall"
        - "exists"
        - "at"
        - "check_at"
        - "pairwise"
    """
    if get_quantifier_expression(prop):
        return "quantifier"
    if get_at_expression(prop):
        return "at"
    if get_check_at_expression(prop):
        return "check_at"
    if get_pairwise_expression(prop):
        return "pairwise"
    return None


# ----------------------------------------------------------------------------------------------------------------------
#                                             QUANTIFIER
# ----------------------------------------------------------------------------------------------------------------------

def get_quantifier_expression(tree: Tree) -> Optional[Tree]:
    """Return quantifier node."""
    return find_node(tree, "quantifier_expr")


def get_quantifier_value(tree: Tree) -> Optional[str]:
    quant_expr = get_quantifier_expression(tree)
    return get_token_value(quant_expr)


# ----------------------------------------------------------------------------------------------------------------------
#                                             CORE EXPRESSIONS
# ----------------------------------------------------------------------------------------------------------------------

def get_at_expression(tree: Tree) -> Optional[Tree]:
    return find_node(tree, "at_expr")


def get_check_at_expression(tree: Tree) -> Optional[Tree]:
    return find_node(tree, "check_expr")


def get_pairwise_expression(tree: Tree) -> Optional[Tree]:
    return find_node(tree, "pairwise_expr")


def get_using_expression(tree: Tree) -> Optional[Tree]:
    return find_node(tree, "abstractor")


# ----------------------------------------------------------------------------------------------------------------------
#                                             IDENTIFIERS
# ----------------------------------------------------------------------------------------------------------------------

def get_identifiers(tree: Tree) -> List[Tree]:
    """Return all identifier nodes."""
    return find_all_nodes(tree, "identifier")


def get_identifier_value(node: Tree) -> Optional[str]:
    """Extract identifier value."""
    return get_token_value(node)


# ----------------------------------------------------------------------------------------------------------------------
#                                             DOMAIN
# ----------------------------------------------------------------------------------------------------------------------

def get_domain_expression(tree: Tree) -> Optional[Tree]:
    return find_node(tree, "domain")


def get_domain_dict(tree: Tree) -> Optional[dict]:
    """
    Extract domain as a structured dictionary.

    Example:
        with gender("male", "female")

    Returns:
        {
            "name": "gender",
            "values": ["male", "female"]
        }
    """
    domain = get_domain_expression(tree)
    if not domain:
        return None

    name = get_token_value(find_child(domain, "identifier"))

    values = [
        clean_string(get_token_value(v))
        for v in find_all_nodes(domain, "value")
    ]

    return {
        "name": name,
        "values": values
    }


# ----------------------------------------------------------------------------------------------------------------------
#                                             LOGIC
# ----------------------------------------------------------------------------------------------------------------------

def get_logic_expression(tree: Tree) -> Optional[Tree]:
    return find_node(tree, "logic_expr")


def get_logic_expressions(tree: Tree) -> List[Tree]:
    return find_all_nodes(tree, "logic_expr")


# ----------------------------------------------------------------------------------------------------------------------
#                                             NEIGHBORHOOD
# ----------------------------------------------------------------------------------------------------------------------

def get_neighborhood_expression(tree: Tree) -> Optional[Tree]:
    return find_node(tree, "neighborhood")


def get_neighborhood_metric(neighborhood: Tree) -> Optional[str]:
    """
    Extract metric (e.g., L2).
    """
    if not neighborhood or not neighborhood.children:
        return None

    first = neighborhood.children[0]

    if isinstance(first, Token):
        return first.value

    return get_token_value(first)


def get_neighborhood_args(neighborhood: Tree) -> dict:
    """
    Extract neighborhood arguments.

    Example:
        eps=0.01 -> {"eps": "0.01"}
    """
    args_node = find_child(neighborhood, "args")
    if not args_node:
        return {}

    result = {}

    for arg in find_all_nodes(args_node, "arg"):

        eq = find_child(arg, "arg_identifier_eq")

        if eq:
            key = get_token_value(find_child(eq, "quoted_identifier"))
            value = clean_string(get_token_value(find_child(eq, "value")))

            if key:
                result[key] = value
            continue

        # fallback case (flag-like argument)
        val = get_token_value(arg)
        if val:
            result[val] = True

    return result


def get_neighborhood_dict(tree: Tree) -> Optional[dict]:
    """
    Structured neighborhood representation.
    """
    neighborhood = get_neighborhood_expression(tree)
    if not neighborhood:
        return None

    return {
        "metric": get_neighborhood_metric(neighborhood),
        "args": get_neighborhood_args(neighborhood)
    }


# ----------------------------------------------------------------------------------------------------------------------
#                                             ASSERTION / PROBLEM
# ----------------------------------------------------------------------------------------------------------------------

def get_assertion_expression(tree: Tree) -> Optional[Tree]:
    return find_node(tree, "assertion")

    # ----------------------------------------------------------------------------------------------------------------------
    #                                             ASSERTION STRUCTURE
    # ----------------------------------------------------------------------------------------------------------------------

def is_implication(assertion: Tree) -> bool:
    return assertion is not None and len(assertion.children) == 2


def get_implication_left(assertion: Tree) -> Optional[Tree]:
    if is_implication(assertion):
        return assertion.children[0]
    return None


def get_implication_right(assertion: Tree) -> Optional[Tree]:
    if is_implication(assertion):
        return assertion.children[1]
    return None


    # ----------------------------------------------------------------------------------------------------------------------
    #                                             LOGIC STRUCTURE
    # ----------------------------------------------------------------------------------------------------------------------

def get_logic_or(assertion: Tree) -> Optional[Tree]:
    if not assertion:
        return None
    return find_node(assertion, "logic_or")


def get_logic_and(assertion: Tree) -> Optional[Tree]:
    return find_node(assertion, "logic_and")


def get_logic_not(assertion: Tree) -> Optional[Tree]:
    return find_node(assertion, "logic_not")


    # ----------------------------------------------------------------------------------------------------------------------
    #                                            OPERATORS
    # ----------------------------------------------------------------------------------------------------------------------


def get_or_operands(node: Tree) -> List[Tree]:
    if node and node.data == "logic_or":
        return node.children
    return []


def get_and_operands(node: Tree) -> List[Tree]:
    if node and node.data == "logic_and":
        return node.children
    return []



    # ----------------------------------------------------------------------------------------------------------------------
    #                                            ATOM UNWRAP
    # ----------------------------------------------------------------------------------------------------------------------


def unwrap_atom(node: Tree) -> Tree:
    """
    Remove layers: logic_not → atom → assertion
    """
    current = node

    while isinstance(current, Tree):
        if current.data in ("logic_not", "atom") and current.children:
            current = current.children[0]
        else:
            break

    return current

# ----------------------------------------------------------------------------------------------------------------------
#                                             PROBLEM
# ----------------------------------------------------------------------------------------------------------------------


def get_problem_expression(tree: Tree) -> Optional[Tree]:
    return find_node(tree, "problem_expr")


def get_problem_name(tree: Tree) -> Optional[str]:
    return get_token_value(get_problem_expression(tree))


# ----------------------------------------------------------------------------------------------------------------------
#                                             ABSTRACTOR
# ----------------------------------------------------------------------------------------------------------------------

def get_abstractor(tree: Tree) -> Optional[Tree]:
    return find_node(tree, "abstractor")


def get_abstractor_dict(tree: Tree) -> Optional[dict]:
    """
    Extract abstractor (backend) as structured dict.

    Example:
        using eran(eps=0.1)

    Returns:
        {
            "name": "eran",
            "args": {"eps": "0.1"}
        }
    """
    abstractor = get_abstractor(tree)
    if not abstractor:
        return None

    name = get_token_value(abstractor)

    args_node = find_child(abstractor, "args")
    args = {}

    if args_node:
        for arg in find_all_nodes(args_node, "arg_identifier_eq"):
            key = get_token_value(find_child(arg, "quoted_identifier"))
            value = clean_string(get_token_value(find_child(arg, "value")))

            if key:
                args[key] = value

    return {
        "name": name,
        "args": args
    }


# ----------------------------------------------------------------------------------------------------------------------
#                                             HIGH LEVEL (IMPORTANT)
# ----------------------------------------------------------------------------------------------------------------------

def get_property_dict(prop: Tree) -> dict:
    """
    Convert a single property into a structured semantic representation.

    NOTE:
    This function operates at PROPERTY level (not program level).
    """

    return {
        "type": get_property_type(prop),
        "mode": get_property_mode(prop),
        "quantifier": get_quantifier_value(prop),
        "domain": get_domain_dict(prop),
        "neighborhood": get_neighborhood_dict(prop),
        "abstractor": get_abstractor_dict(prop),
    }


def get_program_dict(tree: Tree) -> dict:
    """
    Convert a full FORML program into a structured representation.

    IMPORTANT:
    - A program may contain multiple properties
    - Each property is processed independently

    Returns:
        {
            "model": "...",
            "target": "...",
            "properties": [ ... ]
        }
    """

    properties = get_all_properties(tree)

    return {
        "model": clean_string(get_token_value(get_model_declaration(tree))),
        "target": clean_string(get_token_value(get_target_declaration(tree))),
        "properties": [get_property_dict(p) for p in properties],
    }