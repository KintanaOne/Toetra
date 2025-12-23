import unittest
from forml.parser.parser import parse_forml_code

class TestParseProgram(unittest.TestCase):
    def test_parse_program(self):

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
        print(result)
        assert result is not None
        assert result.header is not None
        assert result.body is not None
        assert len(result.body.sections) == 1