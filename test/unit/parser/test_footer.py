from dsl.parser.parser import parse_forml_code


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
    forall x0 => CLASSIFICATION.EQUAL()
    """

    result = parse_forml_code(code)

    assert not hasattr(result, "footer")


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
    forall x0 => CLASSIFICATION.EQUAL()

    # This is a simple footer comment
    """

    result = parse_forml_code(code)

    assert not hasattr(result, "footer")
