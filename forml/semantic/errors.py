from forml.grammar.official_contents.problems import EnumProblem
from forml.grammar.official_contents.functions import EnumFunction

# This file contains the error classes for the validator. These errors are raised when the validator encounters an incompatible function or an invalid property in the program.

class SemanticError(Exception):
    pass

class IncompatibleFunctionError(SemanticError):
    pass

class InvalidPropertyError(SemanticError):
    pass