# src/toetra/_language/vocabulary/properties.py

from enum import Enum
from toetra._language.vocabulary.utils import EnumMixin

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
