# /forml/grammar/official_contents/quantifiers.py

from enum import Enum
from forml.grammar.official_contents.utils import EnumMixin

official_quantifiers = {
    "FORALL": '"∀"',
    "EXIST": '"∃"',
    "forall": '"forall"',
    "exist": '"exist"',
    "forall x" : "forall",
    "exist x" : "exist",
    "check_at" : "check_at",
    "at" : "at"
}

class EnumQuantifier(EnumMixin, Enum):
    FORALL = "FORALL"
    EXIST = "EXIST"
    forall = "forall"
    exist = "exist"
    forall_x = "forall x"
    exist_x = "exist x"
    check_at = "check_at"
    at = "at"