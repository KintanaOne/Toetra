from __future__ import annotations

from typing import Any


class SemanticError(Exception):
    """Structured AST semantic-validation failure."""

    default_code = "SEMANTIC_INVALID"

    def __init__(
        self,
        message: str,
        node: Any = None,
        context: str | None = None,
        *,
        code: str | None = None,
        hint: str | None = None,
    ) -> None:
        self.message = message
        self.node = node
        self.context = context
        self.code = code or self.default_code
        self.hint = hint
        source_span = getattr(node, "source_span", None)
        self.line = getattr(source_span, "line", None)
        self.column = getattr(source_span, "column", None)
        super().__init__(self.__str__())

    def __str__(self) -> str:
        location = f"[{self.context}] " if self.context else ""
        node_info = f" Node={type(self.node).__name__}" if self.node else ""
        return f"{location}{self.message}{node_info}"


class InvalidPropertyError(SemanticError):
    default_code = "SEMANTIC_INVALID_PROPERTY"


class UnboundVariableError(SemanticError):
    default_code = "SEMANTIC_UNBOUND_VARIABLE"


class TypeMismatchError(SemanticError):
    default_code = "SEMANTIC_TYPE_MISMATCH"


class InvalidOperatorError(SemanticError):
    default_code = "SEMANTIC_INVALID_OPERATOR"


class IncompatibleFunctionError(SemanticError):
    default_code = "SEMANTIC_INCOMPATIBLE_FUNCTION"


class InvalidArithmeticError(TypeMismatchError):
    """Raised when a scalar arithmetic expression is not semantically valid."""

    default_code = "SEMANTIC_INVALID_ARITHMETIC"


class InvalidDomainError(SemanticError):
    """Raised when a typed domain violates its semantic contract."""

    default_code = "SEMANTIC_INVALID_DOMAIN"


class InvalidOutputObservableError(InvalidPropertyError):
    """Raised when a public model-output observable violates its schema."""

    default_code = "SEMANTIC_INVALID_OUTPUT_OBSERVABLE"
