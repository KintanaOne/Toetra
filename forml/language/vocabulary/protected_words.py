# /forml/grammar/official_contents/protected_words.py

from enum import Enum
from forml.language.vocabulary.utils import EnumMixin


protected_words = {
    "IN":           '"in"',
    "WITH":         '''"with"''',
    "AT":           '"at"',
    "CHECK_AT":     '"check_at"',
    "USING":        '"using"',
    "MODEL":        '"model"',
    "TARGET":       '"target"',
    "NEIGHBORHOOD": '"neighborhood"',
}

class EnumProtectedWord(EnumMixin, Enum):
    IN = '"in"'
    WITH = '''"with"'''
    AT = '"at"'
    CHECK_AT = '"check_at"'
    USING = '"using"'
    MODEL = '"model"'
    TARGET = '"target"'
    NEIGHBORHOOD = '"neighborhood"'