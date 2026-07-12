from dsl.ir.ir1.run_ir1 import run_ir


def test_explicit_quantifier_identifier_reaches_semantic_binding_and_ir1():
    source = '''
    model := "model.onnx"
    target := MyTarget

    [LOGIC]:
    forall applicant => age <= 30
    '''

    task = run_ir(source)[0]
    comparison = task.query.expression

    assert task.scope.variables == {"applicant": "symbolic"}
    assert comparison.entity == "applicant"
    assert comparison.feature == "age"
