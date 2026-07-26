from __future__ import annotations

from collections.abc import Sequence

from toetra._compiler.ast.nodes.header import (
    HeaderNode,
    SpecificationConstantDeclarationNode,
)
from toetra._compiler.semantic.context.context import SemanticContext
from toetra._compiler.semantic.errors.errors import InvalidPropertyError
from toetra._compiler.semantic.symbols.symbol import Symbol

SPECIFICATION_CONSTANT_KIND = "specification_constant"


def collect_specification_constants(
    header: HeaderNode,
) -> tuple[SpecificationConstantDeclarationNode, ...]:
    """Validate declaration uniqueness and freeze source order."""
    declarations = tuple(header.specification_constants)
    seen: set[str] = set()

    for declaration in declarations:
        if declaration.name in seen:
            raise InvalidPropertyError(
                f"Duplicate specification constant '{declaration.name}'"
            )

        seen.add(declaration.name)

    return declarations


def register_specification_constants(
    context: SemanticContext,
    declarations: Sequence[SpecificationConstantDeclarationNode],
) -> None:
    """Expose immutable declarations in one property semantic context."""
    for declaration in declarations:
        if context.symbol_table.exists(declaration.name):
            raise InvalidPropertyError(
                "Specification constant "
                f"'{declaration.name}' collides with a scope variable"
            )

        context.symbol_table.register(
            Symbol(
                name=declaration.name,
                kind=SPECIFICATION_CONSTANT_KIND,
                dtype=declaration.value.dtype,
                origin=declaration,
            )
        )
