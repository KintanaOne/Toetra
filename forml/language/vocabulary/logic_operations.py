# /forml/grammar/official_contents/quantifiers.py

from enum import Enum
from forml.language.vocabulary.utils import EnumMixin

official_logic_operations = {
    "EQ": '"=="',
    "NEQ": '"!="',
    "LT": '"<"',
    "LTE": '"<="',
    "GT": '">"',
    "GTE": '">="'
}

class EnumLogicOperation(EnumMixin, Enum):
    EQ = "=="
    NEQ = "!="
    LT = "<"
    LTE = "<="
    GT = ">"
    GTE = ">="
    