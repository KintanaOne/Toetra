from __future__ import annotations


class BuilderError(Exception):
    """Structured CST-to-AST construction failure."""

    default_code = "BUILDER_INVALID_STRUCTURE"

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        hint: str | None = None,
        line: int | None = None,
        column: int | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code or self.default_code
        self.hint = hint
        self.line = line
        self.column = column
