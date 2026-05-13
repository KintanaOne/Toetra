from enum import Enum


class EnumModelFramework(Enum):
    """
    A class representing the supported machine learning frameworks.
    """
    
    SKLEARN = "sklearn"
    TENSORFLOW = "tensorflow"
    PYTORCH = "pytorch"
    XGBOOST = "xgboost"