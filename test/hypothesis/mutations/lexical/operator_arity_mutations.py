"""
Operator arity violation mutations.

Goal:
- break binary operator structure
- create valid-looking but invalid AST shapes
"""

import random
import re

OPS = ["==", "!=", "~", "->", "<=", ">="]

def remove_operand(text: str) -> str:
    return re.sub(r"(==|!=|<=|>=|->|~)\s*\w+", r"\1", text)


def duplicate_operator(text: str) -> str:
    return re.sub(r"(==|!=|<=|>=|->|~)", r"\1\1", text)


def operator_shuffle(text: str) -> str:
    return re.sub(r"(==|!=|<=|>=|->|~)", lambda _: random.choice(OPS), text)


def break_infix(text: str) -> str:
    return re.sub(r"(==|!=|<=|>=|->|~)\s*\w+", r"\1", text)

OPERATOR_ARITY_MUTATIONS = [
    remove_operand,
    duplicate_operator,
    operator_shuffle,
    break_infix,
]