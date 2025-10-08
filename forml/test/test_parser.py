from pathlib import Path
from lark import Lark

test_path = Path(__file__).parent.parent / "example/robutness_example.forml"
print(test_path)

grammar = open(test_path).read()
parser = Lark(grammar, parser="lalr", cache=False)

code = """# 1 forall without using
[ROBUTNESS]:
forall x in hyperball("L2", 0.01) -> CLASSIFICATION.EQUAL()
"""

tree = parser.parse(code)
print(tree.pretty())
