# dsl/language/vocabulary/operators.py

from enum import Enum
from dsl.language.vocabulary.utils import EnumMixin

official_logic_operators = {
    "AND": '"and"',
    "OR": '"or"',
    "NOT": '"not"',
    "XOR": '"xor"',
    "IMPLY": '"->"',
}


official_arithmetic_operators = {
    "PLUS": '"+"',
    "MINUS": '"-"',
    "STAR": '"*"',
    "SLASH": '"/"',
}

official_comparaison_operations = {
    "EQ": '"=="',
    "NEQ": '"!="',
    "LT": '"<"',
    "LTE": '"<="',
    "GT": '">"',
    "GTE": '">="',
}


class EnumComparisonOperator(EnumMixin, Enum):
    EQ = "=="
    NEQ = "!="
    LT = "<"
    LTE = "<="
    GT = ">"
    GTE = ">="


class EnumLogicalOperator(EnumMixin, Enum):
    AND = "and"
    OR = "or"
    NOT = "not"
    IMPLY = "->"


class EnumArithmeticOperator(EnumMixin, Enum):
    ADD = "+"
    SUB = "-"
    MUL = "*"
    DIV = "/"


class EnumUnaryOperator(EnumMixin, Enum):
    PLUS = "+"
    MINUS = "-"
