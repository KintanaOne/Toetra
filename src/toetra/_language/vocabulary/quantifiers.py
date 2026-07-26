# src/toetra/_language/vocabulary/quantifiers.py

from enum import Enum
from toetra._language.vocabulary.utils import EnumMixin

official_quantifiers = {
    "FORALL": '"∀"',
    "EXIST": '"∃"',
    "FORALL_WORD ": '"forall"',
    "EXISTS_WORD ": '"exists"',
}


class EnumQuantifier(EnumMixin, Enum):
    FORALL = "FORALL"
    EXIST = "EXIST"
    forall = "forall"
    exists = "exists"
