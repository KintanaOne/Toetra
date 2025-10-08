# forml/parser/forml_transformer.py

from lark import Transformer
from forml.parser import forml_parser


class FORMLTransformer(Transformer):
    def program(self, items):
        return {
            "type": "program",
            "elements": items
        }

    def comment(self, items):
        return {"type": "comment", "value": "".join(items)}

    def inline_comment(self, items):
        return {"type": "inline_comment", "value": "".join(items)}

    def target_declaration(self, items):
        return {"type": "target_declaration", "target": items[0]}

    def declaration_section(self, items):
        return {"type": "declaration", "key": items[0], "value": items[1]}

    def property_block(self, items):
        return {
            "type": "property_block",
            "comment": items[0],
            "property": items[1],
            "backend": items[2]
        }

    def property(self, items):
        return {
            "type": "property",
            "property_type": items[0],
            "quantified_expr": items[1],
            "assertion": items[2]
        }

    def property_type(self, items):
        return str(items[0])

    def quantifier_expr(self, items):
        return {
            "type": "quantifier_expr",
            "var": items[0],
            "set": items[1]
        }

    def anchor_expr(self, items):
        return {
            "type": "anchor_expr",
            "instance": items[0],
            "condition": items[1]
        }

    def attribute_filter(self, items):
        return {
            "type": "attribute_filter",
            "attribute": items[0],
            "values": items[1:]
        }

    def pairwise_expr(self, items):
        return {
            "type": "pairwise_expr",
            "left": items[0],
            "right": items[1],
            "distance": items[2]
        }

    def symbolic_distance(self, items):
        return {
            "type": "symbolic_distance",
            "name": items[0],
            "column": items[1],
            "threshold": items[2]
        }

    def quantifier_set(self, items):
        return {"func": items[0], "args": items[1]}

    def quantifier_set_args(self, items):
        return {
            "L_type": items[0],
            "value": items[1]
        }

    def logic_expr(self, items):
        return {
            "type": "logic_expr",
            "problem": items[0],
            "function": items[1]
        }

    def logic_assertion(self, items):
        return {
            "type": "logic_assertion",
            "condition": items[0],
            "conclusion": {
                "left": items[1],
                "value": items[2]
            }
        }

    def logic_condition(self, items):
        return {
            "object": items[0],
            "attribute": items[1],
            "op": items[2],
            "value": items[3]
        }

    def function(self, items):
        return {
            "name": items[0],
            "args": items[1] if len(items) > 1 else {}
        }

    def named_args(self, items):
        return dict(items)

    def named_arg(self, items):
        return (items[0], items[1])

    def abstractor(self, items):
        backend = items[0]
        params = dict(items[1:]) if len(items) > 1 else {}
        return {"backend": backend, "params": params}

    def identifier(self, items):
        return str(items[0])

    def string(self, items):
        return str(items[0])[1:-1]

    def number(self, items):
        return int(items[0])

    def boolean(self, items):
        return str(items[0]).lower() == "true"

    def comparison_op(self, items):
        return str(items[0])


# === Main interface ===

def parse_and_transform(code: str):
    tree = forml_parser.parse(code)
    transformer = FORMLTransformer()
    return transformer.transform(tree)

if __name__ == "__main__":
    from pathlib import Path

    test_path = Path(__file__).parent / "example.forml"
    if test_path.exists():
        with open(test_path, "r", encoding="utf-8") as f:
            code = f.read()
        result = parse_and_transform(code)
        import json
        print(json.dumps(result, indent=2))
    else:
        print("No example.forml file found.")
