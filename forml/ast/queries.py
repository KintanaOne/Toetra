import json
from lark import Token, Tree
from typing import Optional, List, Union

from forml.core.utils import find_child, find_all_nodes, find_node


# ----------------------------------------------------------------------------------------------------------------------
# HELPERS
# ----------------------------------------------------------------------------------------------------------------------

def clean_string(value: str) -> Optional[str]:
    if value is None:
        return None

    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]

    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]

    return value


def get_token_value(node: Union[Tree, Token]) -> Optional[str]:
    if node is None:
        return None

    if isinstance(node, Token):
        return node.value

    if isinstance(node, Tree):
        if not node.children:
            return str(node.data)

        for child in node.children:
            value = get_token_value(child)
            if value is not None:
                return value

    return None


# ----------------------------------------------------------------------------------------------------------------------
# HEADER
# ----------------------------------------------------------------------------------------------------------------------

def get_header(tree: Tree) -> Optional[Tree]:
    return find_child(tree, "header")


def get_model_declaration(tree: Tree) -> Optional[Tree]:
    return find_child(get_header(tree), "model_declaration")


def get_target_declaration(tree: Tree) -> Optional[Tree]:
    return find_child(get_header(tree), "target_declaration")


# ----------------------------------------------------------------------------------------------------------------------
# IDENTIFIERS
# ----------------------------------------------------------------------------------------------------------------------

def get_identifier_value(node: Tree) -> Optional[str]:
    return get_token_value(node)


# ----------------------------------------------------------------------------------------------------------------------
# PROPERTIES
# ----------------------------------------------------------------------------------------------------------------------

def get_all_properties(tree: Tree) -> List[Tree]:
    return find_all_nodes(tree, "property_section")


def get_property_type(prop: Tree) -> Optional[str]:
    return get_token_value(find_node(prop, "property_type"))


def get_property_mode(prop: Tree) -> Optional[str]:
    if find_node(prop, "quantifier_expr"):
        return "quantifier"
    if find_node(prop, "at_expr"):
        return "at"
    if find_node(prop, "check_expr"):
        return "check_at"
    if find_node(prop, "pairwise_expr"):
        return "pairwise"
    return None


# ----------------------------------------------------------------------------------------------------------------------
# DOMAIN
# ----------------------------------------------------------------------------------------------------------------------

def get_domain_dict(tree: Tree) -> Optional[dict]:
    domain = find_node(tree, "domain")
    if not domain:
        return None

    name = get_token_value(find_child(domain, "identifier"))
    values = [
        clean_string(get_token_value(v))
        for v in find_all_nodes(domain, "value")
    ]

    return {"name": name, "values": values}


# ----------------------------------------------------------------------------------------------------------------------
# NEIGHBORHOOD
# ----------------------------------------------------------------------------------------------------------------------

def get_neighborhood_dict(tree: Tree) -> Optional[dict]:
    neighborhood = find_node(tree, "neighborhood")
    if not neighborhood:
        return None

    metric = None
    for child in neighborhood.children:
        if isinstance(child, Token):
            metric = child.value

    args = {}
    args_node = find_child(neighborhood, "args")

    if args_node:
        for arg in find_all_nodes(args_node, "arg"):
            eq = find_child(arg, "arg_identifier_eq")

            if eq:
                key = get_token_value(find_child(eq, "quoted_identifier"))
                value = clean_string(get_token_value(find_child(eq, "value")))
                if key:
                    args[key] = value
            else:
                val = get_token_value(arg)
                if val:
                    args[val] = True

    return {"metric": metric, "args": args}


# ----------------------------------------------------------------------------------------------------------------------
# EXPRESSIONS
# ----------------------------------------------------------------------------------------------------------------------

def get_at_dict(prop: Tree) -> dict:
    node = find_node(prop, "at_expr")

    return {
        "variable": get_identifier_value(find_child(node, "identifier")),
        "neighborhood": get_neighborhood_dict(node),
        "domain": get_domain_dict(node),
    }


def get_pairwise_dict(prop: Tree) -> dict:
    node = find_node(prop, "pairwise_expr")

    return {
        "pair": get_token_value(find_child(node, "pairwise_token")),
        "neighborhood": get_neighborhood_dict(node),
        "domain": get_domain_dict(node),
    }


def get_check_at_dict(prop: Tree) -> dict:
    node = find_node(prop, "check_expr")

    return {
        "variable": get_identifier_value(find_child(node, "identifier"))
    }


def get_quantifier_dict(prop: Tree) -> dict:
    q = find_node(prop, "quantifier_expr")

    return {
        "quantifier": get_token_value(q),
        "domain": get_domain_dict(prop),
    }


# ----------------------------------------------------------------------------------------------------------------------
# ASSERTION
# ----------------------------------------------------------------------------------------------------------------------

def get_assertion_dict(tree: Tree) -> dict:
    return build_assertion(find_node(tree, "assertion"))


def build_assertion(node: Tree) -> dict:
    if node is None:
        return {}

    # -------------------------
    # assertion (implication)
    # -------------------------
    if node.data == "assertion":
        if len(node.children) == 1:
            return build_assertion(node.children[0])

        return {
            "type": "implication",
            "left": build_assertion(node.children[0]),
            "right": build_assertion(node.children[2]),
        }

    # -------------------------
    # OR
    # -------------------------
    if node.data == "logic_or":
        ops = [build_assertion(c) for c in node.children if isinstance(c, Tree)]
        return ops[0] if len(ops) == 1 else {"type": "or", "operands": ops}

    # -------------------------
    # AND
    # -------------------------
    if node.data == "logic_and":
        ops = [build_assertion(c) for c in node.children if isinstance(c, Tree)]
        return ops[0] if len(ops) == 1 else {"type": "and", "operands": ops}

    # -------------------------
    # NOT
    # -------------------------
    if node.data == "logic_not":
        if len(node.children) == 1:
            return build_assertion(node.children[0])

        return {
            "type": "not",
            "operand": build_assertion(node.children[1]),
        }

    # -------------------------
    # atom
    # -------------------------
    if node.data == "atom":
        return build_assertion(node.children[0])

    # -------------------------
    # logic_expr
    # -------------------------
    if node.data == "logic_expr":
        return {
            "type": "comparison",
            "left": get_token_value(find_child(node, "attribute")),
            "op": get_token_value(find_child(node, "logic_operation")),
            "right": clean_string(get_token_value(find_child(node, "value"))),
        }

    # -------------------------
    # problem_expr
    # -------------------------
    if node.data == "problem_expr":
        problem = None
        function = None

        for child in node.children:
            if isinstance(child, Token):
                problem = child.value
            elif isinstance(child, Tree) and child.data == "function_expr":
                function = get_token_value(child)

        return {
            "type": "problem",
            "problem": problem,
            "function": function,
        }

    return {"type": "unknown", "raw": str(node)}


# ----------------------------------------------------------------------------------------------------------------------
# ABSTRACTOR
# ----------------------------------------------------------------------------------------------------------------------

def get_abstractor_dict(tree: Tree) -> Optional[dict]:
    node = find_node(tree, "abstractor")
    if not node:
        return None

    args = {}
    args_node = find_child(node, "args")

    if args_node:
        for arg in find_all_nodes(args_node, "arg_identifier_eq"):
            key = get_token_value(find_child(arg, "quoted_identifier"))
            value = clean_string(get_token_value(find_child(arg, "value")))
            if key:
                args[key] = value

    return {
        "name": get_token_value(node),
        "args": args
    }


# ----------------------------------------------------------------------------------------------------------------------
# PROPERTY
# ----------------------------------------------------------------------------------------------------------------------

def get_property_expr_dict(prop: Tree) -> dict:
    mode = get_property_mode(prop)

    if mode == "quantifier":
        return {"mode": mode, **get_quantifier_dict(prop)}

    if mode == "at":
        return {"mode": mode, "at": get_at_dict(prop)}

    if mode == "pairwise":
        return {"mode": mode, "pairwise": get_pairwise_dict(prop)}

    if mode == "check_at":
        return {"mode": mode, "check_at": get_check_at_dict(prop)}

    return {"mode": "unknown"}


def get_property_dict(prop: Tree) -> dict:
    return {
        "type": get_property_type(prop),
        "expr": get_property_expr_dict(prop),
        "assertion": get_assertion_dict(prop),
        "abstractor": get_abstractor_dict(prop),
    }


# ----------------------------------------------------------------------------------------------------------------------
# PROGRAM
# ----------------------------------------------------------------------------------------------------------------------

def get_program_dict(tree: Tree) -> dict:
    return {
        "model": clean_string(get_token_value(get_model_declaration(tree))),
        "target": clean_string(get_token_value(get_target_declaration(tree))),
        "properties": [get_property_dict(p) for p in get_all_properties(tree)],
    }


# ----------------------------------------------------------------------------------------------------------------------
# DEBUG
# ----------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    from forml.parser.parser import parse_forml_code
    from pathlib import Path

    path = Path(__file__).parent.parent / "/mnt/c<LOCAL_USER_HOME>/KintanaOne/FORML/forml/example/robustness/robustness_check_at.forml"


    if path.exists():
        tree = parse_forml_code(path.read_text())
        print(json.dumps(get_program_dict(tree), indent=4))