# /formel/grammar/official_contents/sets.py

from enum import Enum
from forml.grammar.official_contents.utils import EnumMixin

official_sets = {
    "ball" : '"ball"',
    "hyperball" : '"hyperball"',
    "noise" : '"noise"'
}

class EnumSet(EnumMixin, Enum):
    ball = "ball"
    hyperball = "hyparball"
    noise = "noise"
