from dsl.parser.parser import parse_forml_code
from dsl.builder.program import parse_program
from dsl.language.vocabulary.backends import EnumBackend

sample = """
model := "model.onnx"
target := MyTarget

[ROBUSTNESS]:
at x0 in neighborhood(L2, eps=0.01) => CLASSIFICATION.EQUAL() using Z3
"""

tree = parse_forml_code(sample)
ast = parse_program(tree)

print(ast.body[0].backend)
assert ast.body[0].backend is not None
assert ast.body[0].backend.name is EnumBackend.Z3
