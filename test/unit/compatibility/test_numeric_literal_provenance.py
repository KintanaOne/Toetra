from __future__ import annotations

from toetra._compiler.builder.core.ast_utils import parse_literal_value
from toetra._compiler.ir.ir1.nodes import ConstantExpressionIR
from toetra._compiler.ir.ir1.scalar_translator import ScalarExpressionTranslator
from toetra._compiler.semantic.types.enums import EnumDataType


def test_decimal_literal_spelling_survives_ast_to_ir1_translation() -> None:
    literal = parse_literal_value("0.10")

    assert literal.value == 0.1
    assert literal.dtype is EnumDataType.FLOAT
    assert literal.source_lexeme == "0.10"

    translated = ScalarExpressionTranslator().translate(literal)

    assert isinstance(translated, ConstantExpressionIR)
    assert translated.value == 0.1
    assert translated.source_lexeme == "0.10"
