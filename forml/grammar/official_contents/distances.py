# /forml/grammar/official_contents/distance.py

from enum import Enum
from forml.grammar.official_contents.utils import EnumMixin


official_distances = {
    "levenshtein" : '"levenshtein"',
    "euclidian" : '"euclidian"',
}

class EnumDistance(EnumMixin, Enum):
    levenshtein = "levenshtein"
    euclidian = "euclidian"