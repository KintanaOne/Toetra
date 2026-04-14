import pytest
from forml.parser.parser import parse_forml_code
from forml.core.utils import *


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
    [ROBUSTNESS]:
    forall => CLASSIFICATION.EQUAL();
    """

    result = parse_forml_code(code)
    pass

    #footer = find_node(result, "footer")
    # assert footer is None

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
    [ROBUSTNESS]:
    forall => CLASSIFICATION.EQUAL();

    # This is a simple footer comment
    """

    result = parse_forml_code(code)
    pass
    #  = find_node(result, "footer")
    #assert footer is None