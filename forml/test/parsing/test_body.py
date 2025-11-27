import unittest
from forml.parser.errors import ParserBodyError
from forml.parser.parser import parse_forml_code

class TestBody(unittest.TestCase):

    def test_body_with_property_section(self):
        code = '''
        model := "path/to/model.onnx"
        target := MyTargetColumn

        [ROBUSTNESS]:
        forall x in hyperball("L2", 0.01) -> CLASSIFICATION.EQUAL();
        '''
        result = parse_forml_code(code)
        self.assertIsNotNone(result.body)
        self.assertGreater(len(result.body.sections), 0)

    def test_body_missing_section(self):
        code = '''
        model := "path/to/model.onnx"
        target := MyTargetColumn
        '''
        with self.assertRaises(ParserBodyError):
            parse_forml_code(code)
