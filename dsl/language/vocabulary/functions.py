# /forml/grammar/official_contents/functions.py

from enum import Enum
from dsl.language.vocabulary.utils import EnumMixin


official_functions = {
    "EQUAL" : '"EQUAL"',
    "EQUITY" : '"EQUITY"',
    "BETWEEN" : '"BETWEEN"',
    "INCREASING" : '"INCREASING"',
    "DECREASING" : '"DECREASING"'
}

class EnumFunction(EnumMixin, Enum):
    EQUAL = "EQUAL"
    EQUITY = "EQUITY"
    BETWEEN = "BETWEEN"
    INCREASING = "INCREASING"
    DECREASING = "DECREASING"