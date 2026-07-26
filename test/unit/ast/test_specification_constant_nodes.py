from toetra._compiler.ast.nodes.base import ASTNode
from toetra._compiler.ast.nodes.header import (
    HeaderNode,
    SpecificationConstantDeclarationNode,
)
from toetra._compiler.ast.nodes.primitives import ConstantNode
from toetra._compiler.semantic.types.enums import EnumDataType


def test_specification_constant_declaration_preserves_name_and_typed_value() -> None:
    value = ConstantNode(
        value=0.2,
        dtype=EnumDataType.FLOAT,
    )

    declaration = SpecificationConstantDeclarationNode(
        name="max_risk",
        value=value,
    )

    assert isinstance(declaration, ASTNode)
    assert declaration.name == "max_risk"
    assert declaration.value is value
    assert declaration.semantic is None


def test_header_preserves_specification_constant_source_order() -> None:
    first = SpecificationConstantDeclarationNode(
        name="minimum_income",
        value=ConstantNode(
            value=25_000.0,
            dtype=EnumDataType.FLOAT,
        ),
    )
    second = SpecificationConstantDeclarationNode(
        name="strict_mode",
        value=ConstantNode(
            value=True,
            dtype=EnumDataType.BOOL,
        ),
    )

    header = HeaderNode(
        model="credit-risk.joblib",
        target="default_risk",
        specification_constants=[first, second],
    )

    assert header.specification_constants == [first, second]


def test_header_defaults_to_an_independent_empty_declaration_list() -> None:
    first = HeaderNode(model="first.onnx", target="FirstTarget")
    second = HeaderNode(model="second.onnx", target="SecondTarget")

    first.specification_constants.append(
        SpecificationConstantDeclarationNode(
            name="threshold",
            value=ConstantNode(
                value=1,
                dtype=EnumDataType.INT,
            ),
        )
    )

    assert len(first.specification_constants) == 1
    assert second.specification_constants == []
