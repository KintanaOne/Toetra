# /forml/grammar/official_contents/problems.py

from enum import Enum
from forml.grammar.official_contents.utils import EnumMixin


official_problems = {
    "CLASSIFICATION" : '"CLASSIFICATION"',
    "PREDICTION" : '"PREDICTION"',
    "REGRESSION" : '"REGRESSION"',
    "CLUSTERING" : '"CLUSTERING"',
    "ANOMALY_DETECTION" : '"ANOMALY_DETECTION"',
    "REINFORCEMENT_LEARNING" : '"REINFORCEMENT_LEARNING"',
}

class EnumProblem(EnumMixin, Enum):
    CLASSIFICATION = "CLASSIFICATION"
    PREDICTION = "PREDICTION"
    REGRESSION = "REGRESSION"
    CLUSTERING = "CLUSTERING"
    ANOMALY_DETECTION = "ANOMALY_DETECTION"
    REINFORCEMENT_LEARNING = "REINFORCEMENT_LEARNING"