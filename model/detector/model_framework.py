from enum import Enum


class EnumModelFramework(Enum):
    SKLEARN = "sklearn"
    XGBOOST = "xgboost"
    UNKNOWN = "unknown"