# /forml/grammar/official_contents/protected_words.py

from enum import Enum
from dsl.language.vocabulary.utils import EnumMixin

protected_words = {
    "IN.10": r"/in(?![A-Za-z0-9_])/",
    "WITH.10": r"/with(?![A-Za-z0-9_])/",
    "DOMAIN.10": r"/domain(?![A-Za-z0-9_])/",
    "AT.10": r"/at(?![A-Za-z0-9_])/",
    "CHECK_AT.10": r"/check_at(?![A-Za-z0-9_])/",
    "USING.10": r"/using(?![A-Za-z0-9_])/",
    "MODEL.10": r"/model(?![A-Za-z0-9_])/",
    "TARGET.10": r"/target(?![A-Za-z0-9_])/",
    "NEIGHBORHOOD.10": r"/neighborhood(?![A-Za-z0-9_])/",
    "DATASET.10": r"/dataset(?![A-Za-z0-9_])/",
    "TRUE.10": r"/(?:True|true)(?![A-Za-z0-9_])/",
    "FALSE.10": r"/(?:False|false)(?![A-Za-z0-9_])/",
}


class EnumProtectedWord(EnumMixin, Enum):
    IN = "in"
    WITH = "with"
    DOMAIN = "domain"
    AT = "at"
    CHECK_AT = "check_at"
    USING = "using"
    MODEL = "model"
    TARGET = "target"
    NEIGHBORHOOD = "neighborhood"
    DATASET = "dataset"
    TRUE = "true"
    FALSE = "false"
