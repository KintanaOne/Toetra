from pathlib import Path

from forml.parser.parser import parse_forml_code
from script.lark_generator import ebnf_to_lark


def main():
    # Convert EBNF grammar to Lark format
    input_path = Path("forml/grammar/forml_grammar.ebnf")
    output_path = Path("forml/grammar/forml_grammar.lark")

    ebnf_text = input_path.read_text(encoding="utf-8")
    try:
        lark_text = ebnf_to_lark(ebnf_text)
        output_path.write_text(lark_text, encoding="utf-8")
        print(f"✅ Converted `{input_path.name}` → `{output_path.name}`")
    except KeyError as e:
        print(f"❌ EBNF to Lark Error: {e}")

    # Test parsing an example .forml file
    test_path = Path(__file__).parent.parent / "example/00_simple_correct_example_multi_comment.forml"
    print(test_path)
    if test_path.exists():
        with open(test_path, "r", encoding="utf-8") as f:
            code = f.read()
        tree = parse_forml_code(code)
        print(tree.pretty())
    else:
        print("No example.forml file found.")

if __name__ == "__main__":
    main()