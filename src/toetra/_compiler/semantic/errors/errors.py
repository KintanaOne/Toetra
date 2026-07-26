class SemanticError(Exception):
    def __init__(self, message, node=None, context=None):
        self.message = message
        self.node = node
        self.context = context
        super().__init__(self.__str__())

    def __str__(self):
        location = f"[{self.context}]" if self.context else ""
        node_info = f" Node={type(self.node).__name__}" if self.node else ""
        return f"{location} {self.message}{node_info}"


class InvalidPropertyError(SemanticError):
    pass


class UnboundVariableError(SemanticError):
    pass


class TypeMismatchError(SemanticError):
    pass


class InvalidOperatorError(SemanticError):
    pass


class IncompatibleFunctionError(SemanticError):
    pass


class InvalidArithmeticError(TypeMismatchError):
    """Raised when a scalar arithmetic expression is not semantically valid."""


class InvalidDomainError(SemanticError):
    """Raised when a typed domain violates its semantic contract."""


class InvalidOutputObservableError(InvalidPropertyError):
    """Raised when a public model-output observable violates its schema."""
