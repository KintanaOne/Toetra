import unittest
from forml.parser.errors import ParserHeaderError
from forml.parser.parser import parse_forml_code
from forml.parser.nodes import Header, TargetDeclaration, ModelDeclaration, Comment

class TestHeader(unittest.TestCase):

    def test_header_correct_order(self):
        code = '''
        model := "path/to/model.onnx"
        target := MyTargetColumn
        '''
        result = parse_forml_code(code)
        self.assertIsInstance(result.header, Header)
        self.assertIsInstance(result.header.model, ModelDeclaration)
        self.assertIsInstance(result.header.target, TargetDeclaration)

    def test_header_with_comments(self):
        code = '''
        # This is a comment
        # Another comment
        model := "path/to/model.onnx"
        target := MyTargetColumn
        '''
        result = parse_forml_code(code)
        self.assertEqual(len(result.header.comments), 2)
        for c in result.header.comments:
            self.assertIsInstance(c, Comment)

    def test_header_missing_model(self):
        code = '''
        target := MyTargetColumn
        '''
        result = parse_forml_code(code)
        self.assertIsNone(result.header.model)
        self.assertIsInstance(result.header.target, TargetDeclaration)

    def test_header_missing_target(self):
        code = '''
        model := "path/to/model.onnx"
        '''
        result = parse_forml_code(code)
        self.assertIsNone(result.header.target)
        self.assertIsInstance(result.header.model, ModelDeclaration)

    def test_header_incorrect_order(self):
        code = '''
        target := MyTargetColumn
        model := "path/to/model.onnx"
        '''
        with self.assertRaises(ParserHeaderError):
            parse_forml_code(code)

    def test_header_invalid_model_type(self):
        code = '''
        model := 123
        target := MyTargetColumn
        '''
        with self.assertRaises(ParserHeaderError):
            parse_forml_code(code)

    def test_header_invalid_target_type(self):
        code = '''
        model := "path/to/model.onnx"
        target := 123
        '''
        with self.assertRaises(ParserHeaderError):
            parse_forml_code(code)
