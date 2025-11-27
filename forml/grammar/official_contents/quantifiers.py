# /forml/grammar/official_contents/quantifiers.py

from enum import Enum
from forml.grammar.official_contents.utils import EnumMixin

official_quantifiers = {
    "FORALL": '"∀"',
    "EXISTS": '"∃"',
    "forall": '"forall"',
    "exists": '"exists"',
}

class EnumQuantifier(EnumMixin, Enum):
    FORALL = "FORALL"
    EXISTS = "EXISTS"
    forall = "forall"
    exists = "exists"