"""
Structural mutations on AST (parser output).

Goal:
    Break syntax structure before semantic construction.
"""

from copy import deepcopy
import random

from dsl.ast.nodes.program import ProgramNode
from dsl.parser.parser import parse_forml_code
from test.hypothesis.utils.serialize import serialize


# =========================================================
# AST MUTATIONS
# =========================================================

def remove_model(ast):
    """
    Remove model declaration node from AST.
    """

    if hasattr(ast, "header"):
        ast.header.model = None

    return ast


def remove_target(ast):
    """
    Remove target declaration node from AST.
    """

    if hasattr(ast, "header"):
        ast.header.target = None

    return ast


def remove_body(ast):
    """
    Remove entire body section.
    """

    if hasattr(ast, "body"):
        ast.body = []

    return ast


def reorder_sections(ast):
    """
    Shuffle high-level AST sections if possible.
    """

    if not hasattr(ast, "__dict__"):
        return ast

    # naive structural perturbation
    items = list(vars(ast).items())
    random.shuffle(items)

    for k, v in items:
        setattr(ast, k, v)

    return ast


STRUCTURAL_MUTATIONS = [
    remove_model,
    remove_target,
    remove_body,
    reorder_sections,
]


# =========================================================
# ENGINE
# =========================================================

def apply_structural_mutations(ast: ProgramNode, n: int) -> ProgramNode:
    for _ in range(n):
        ast = random.choice(STRUCTURAL_MUTATIONS)(ast)
    return ast