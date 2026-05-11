from dataclasses import dataclass


@dataclass
class ModelSchema:
    """
    A dataclass representing the schema of a machine learning model, including its name and features.
    """
    name: str
    features: dict[str, str]