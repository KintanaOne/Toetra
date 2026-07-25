# dsl/language/vocabulary/distances.py

from enum import Enum
from dsl.language.vocabulary.utils import EnumMixin

official_distances = {
    "hyperball": '"hyperball"',
    "levenshtein": '"levenshtein"',
    "euclidian": '"euclidian"',
}


class EnumDistance(EnumMixin, Enum):
    hyperball = "hyperball"
    levenshtein = "levenshtein"
    euclidian = "euclidian"
