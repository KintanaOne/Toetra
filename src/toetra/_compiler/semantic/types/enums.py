from enum import Enum


class EnumDataType(Enum):
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    STRING = "string"
    NoneType = "none"


class EnumArithmeticClass(Enum):
    """Backend-independent structural classification of scalar arithmetic."""

    AFFINE = "affine"
    NONLINEAR = "nonlinear"
    SYMBOLIC_DIVISION = "symbolic_division"
