# /forml/grammar/official_contents/quantifiers.py

from enum import Enum
from forml.language.vocabulary.utils import EnumMixin

official_quantifiers = {
    "FORALL": '"∀"',
    "EXIST": '"∃"',
    "forall": '"forall"',
    "exists": '"exists"'
}

class EnumQuantifier(EnumMixin, Enum):
    FORALL = "FORALL"
    EXIST = "EXIST"
    forall = "forall"
    exists = "exists"