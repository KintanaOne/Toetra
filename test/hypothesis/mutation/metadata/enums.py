from enum import Enum, auto


class Layer(Enum):
    STRING = auto()
    CST = auto()
    AST = auto()
    IR = auto()


class Nature(Enum):
    INSERTION = auto()
    DELETION = auto()
    SUBSTITUTION = auto()
    REORDERING = auto()
    CORRUPTION = auto()


class Strategy(Enum):
    VALID = auto()
    MUTATED = auto()
    CORRUPTED = auto()


class Domain(Enum):
    STRUCTURAL = auto()
    SEMANTIC = auto()
    LOGICAL = auto()
    TYPING = auto()