from toetra._compiler.builder.program import parse_program
from toetra._compiler.parser.parser import parse_toetra_code

if __name__ == "__main__":
    """This script is for quick testing of the builder. It parses a sample property and prints the resulting AST"""

    sample = """
    model := "model.onnx"
    target := MyTargetColumn

    [ROBUSTNESS]:
    x ~ x' in neighborhood(L2, eps=0.01) => CLASSIFICATION.EQUAL() using eran(param1="a")
    """

    # LARK
    CST = parse_toetra_code(sample)
    print(CST.pretty())

    # BUILDER
    AST = parse_program(CST)
    print((AST))
