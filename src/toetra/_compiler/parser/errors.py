class ParserError(Exception):
    """Structured syntax failure owned by the source-to-CST boundary."""

    default_code = "PARSER_INVALID_SYNTAX"

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


class ParserHeaderError(ParserError):
    """Error in the header"""

    pass


class ParserBodyError(ParserError):
    """Error in the body"""

    pass


class ParserFooterError(ParserError):
    """Error in the footer"""

    pass


class ParserSectionError(ParserError):
    """Error in a section"""

    pass


# ───────────────────────────────
# Header Errors
# ───────────────────────────────


class ParserHeaderDeclarationError(ParserHeaderError):
    """Error in a header declaration"""

    pass


class ParserHeaderModelError(ParserHeaderDeclarationError):
    """Error in the model declaration"""

    pass


class ParserHeaderTargetError(ParserHeaderDeclarationError):
    """Error in the target declaration"""

    pass


# ───────────────────────────────
# Section Errors
# ───────────────────────────────


class ParserDeclarationError(ParserSectionError):
    """Error in a declaration"""

    pass


class ParserPropertyError(ParserSectionError):
    """Error in a property"""

    pass


class ParserAbstractorError(ParserSectionError):
    """Error in an abstractor"""

    pass


# ───────────────────────────────
# Property Errors
# ───────────────────────────────


class ParserQuantifierError(ParserPropertyError):
    """Error in a quantifier"""

    pass


class ParserUniversalError(ParserPropertyError):
    """Error in a universal expression"""

    pass


class ParserDomainError(ParserPropertyError):
    """Error in a domain expression"""

    pass


class ParserAnchorError(ParserPropertyError):
    """Error in an anchor expression"""

    pass


class ParserAttributeFilterError(ParserPropertyError):
    """Error in an attribute filter"""

    pass


class ParserBackendError(ParserAbstractorError):
    """Error in a backend"""

    pass


class ParserProblemError(ParserPropertyError):
    """Error in problem"""

    pass


class ParserFunctionError(ParserPropertyError):
    """Error in a function"""

    pass


class ParserUniversalSetError(ParserPropertyError):
    """Error in a universal set"""

    pass


class ParserLogicError(ParserPropertyError):
    """Error in logic expressions"""

    pass


# ───────────────────────────────
# Logic Errors
# ───────────────────────────────


class ParserLogicExprError(ParserLogicError):
    """Error in logic expressions"""

    pass


class ParserLogicConnectionError(ParserLogicError):
    """Error in logic connections"""

    pass


class ParserLogicAssertionError(ParserLogicError):
    """Error in logic assertions"""

    pass


class ParserAssertionError(ParserLogicError):
    """Error in assertions"""

    pass


class ParserImplicationError(ParserLogicError):
    """Error in logic implications"""

    pass
