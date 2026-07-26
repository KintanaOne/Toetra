import pytest
from hypothesis import given
from tests.property_based.strategies.invalid.invalid_syntactic import invalid_cst_program

from tests.property_based.strategies.valid.valid_lexical import valid_lexical_program

pytestmark = pytest.mark.wip


@given(invalid_cst_program(valid_lexical_program()))
def test_parser_rejects_invalid_syntactic(cst):

    with pytest.raises(Exception):

        ast_builder.build(cst)
