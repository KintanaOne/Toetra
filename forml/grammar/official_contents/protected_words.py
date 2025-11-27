# /forml/grammar/official_contents/protected_words.py

from enum import Enum
from forml.grammar.official_contents.utils import EnumMixin


protected_words = {
    "_IN": "in",
    "_WITH": "with",
    "_AT": "at",
    "_CHECK_AT": "check_at",
    "_USING": "using",
    "_MODEL": "model",
    "_TARGET": "target",
    "_DISTANCE": "distance",
}

class EnumProtectedWord(EnumMixin, Enum):
    IN = "in"
    WITH = "with"
    AT = "at"
    CHECK_AT = "check_at"
    USING = "using"
    MODEL = "model"
    TARGET = "target"
    DISTANCE = "distance"