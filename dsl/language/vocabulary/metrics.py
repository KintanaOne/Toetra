# /formel/grammar/official_contents/sets.py

from enum import Enum
from dsl.language.vocabulary.utils import EnumMixin

official_metrics = {"L1": '"L1"', "L2": '"L2"', "LINF": '"Linf"'}


class EnumMetric(EnumMixin, Enum):
    L1 = '"L1"'
    L2 = '"L2"'
    LINF = '"Linf"'
