import json

from lark import Tree
from forml.core.utils import find_all_nodes
from test.fixtures.program_samples import VALID_PROGRAM_WITH_BODY_SIMPLE_ASSERTION
from forml.ast.header import parse_model, parse_target
from forml.ast.property import parse_property


# ============================================================================
# PROGRAM ENTRYPOINT
# ============================================================================

def parse_program(tree: Tree):
    return {
        "model": parse_model(tree),
        "target": parse_target(tree),
        "properties": [
            parse_property(p)
            for p in find_all_nodes(tree, "property_section")
        ]
    }


if __name__ == "__main__":
    from forml.parser.parser import parse_forml_code
    from pathlib import Path

    tree = parse_forml_code(VALID_PROGRAM_WITH_BODY_SIMPLE_ASSERTION)
    print(json.dumps(parse_program(tree), indent=4))
