# /forml/grammar/official_contents/distance.py

from enum import Enum
from forml.language.vocabulary.utils import EnumMixin


official_distances = {
    "hyperball" : '"hyperball"',
    "levenshtein" : '"levenshtein"',
    "euclidian" : '"euclidian"',
}

class EnumDistance(EnumMixin, Enum):
    hyperball = "hyperball"
    levenshtein = "levenshtein"
    euclidian = "euclidian"