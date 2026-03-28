from pathlib import Path

import pytest
from forml.parser.parser import parse_forml_code
from test.utils import *


def test_pairwise_parsing():
    test_path = Path(__file__).parent.parent / "/mnt/c/Users/tinar/KintanaOne/FORML/forml/example/robustness/robustness_check_at.forml"
    with open(test_path, "r", encoding="utf-8") as f:
        code = f.read()
        tree = parse_forml_code(code)
        print(tree.pretty())

