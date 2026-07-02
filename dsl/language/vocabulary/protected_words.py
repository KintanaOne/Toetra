# /forml/grammar/official_contents/protected_words.py

from enum import Enum
from dsl.language.vocabulary.utils import EnumMixin

protected_words = {
    "IN.10": '"in"',
    "WITH.10": '"with"',
    "AT.10": '"at"',
    "CHECK_AT.10": '"check_at"',
    "USING.10": '"using"',
    "MODEL.10": '"model"',
    "TARGET.10": '"target"',
    "NEIGHBORHOOD.10": '"neighborhood"',
    "DATASET.10": '"dataset"',
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
    DATASET = '"dataset"'
