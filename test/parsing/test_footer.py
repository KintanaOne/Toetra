import pytest
from forml.parser.parser import parse_forml_code
from test.utils import *


def test_footer_empty():
    code = """
    '''
    Le header respecte l'ordre :
        - model_declaration
        - target_declaration
    '''
    model := "path/to/model.onnx"
    target := MyTargetColumn

    # 1 forall without using
    [ROBUTNESS]:
    forall in hyperball("L2", 0.01) -> CLASSIFICATION.EQUAL();
    """

    result = parse_forml_code(code)
    footer = find_node(result, "footer")
    assert len(footer.children) == 0

def test_footer_with_simple_comment():
    code = """
    '''
    Le header respecte l'ordre :
        - model_declaration
        - target_declaration
    '''
    model := "path/to/model.onnx"
    target := MyTargetColumn

    # 1 forall without using
    [ROBUTNESS]:
    forall in hyperball("L2", 0.01) -> CLASSIFICATION.EQUAL();

    # This is a simple footer comment
    """

    result = parse_forml_code(code)
    footer = find_node(result, "footer")
    print(result.pretty())
    assert footer is not None
    comments = find_all_nodes(footer, "comment")
    assert len(comments) == 1