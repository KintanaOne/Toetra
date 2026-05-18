# /forml/grammar/official_contents/properties.py

from enum import Enum
from dsl.language.vocabulary.utils import EnumMixin

official_properties = {
    "ROBUSTNESS": '"ROBUSTNESS"',
    "STABILITY": '"STABILITY"',
    "FAIRNESS": '"FAIRNESS"',
    "MONOTONICITY": '"MONOTONICITY"',
    "BOUND": '"BOUND"',
    "LOGIC": '"LOGIC"',
}


class EnumProperty(EnumMixin, Enum):
    ROBUSTNESS = "ROBUSTNESS"
    STABILITY = "STABILITY"
    FAIRNESS = "FAIRNESS"
    MONOTONICITY = "MONOTONICITY"
    BOUND = "BOUND"
    LOGIC = "LOGIC"
