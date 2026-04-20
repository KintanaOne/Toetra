from pathlib import Path

from forml.language.tools.lark_generator import ebnf_to_lark


def main():
    # Convert EBNF grammar to Lark format
    input_path = Path("forml/language/grammar/forml_grammar.ebnf")
    output_path = Path("forml/language/grammar/forml_grammar.")

    ebnf_text = input_path.read_text(encoding="utf-8")
    try:
        lark_text = ebnf_to_lark(ebnf_text)
        output_path.write_text(lark_text, encoding="utf-8")
        print(f"✅ Converted `{input_path.name}` → `{output_path.name}`")
    except KeyError as e:
        print(f"❌ EBNF to Lark Error: {e}")


if __name__ == "__main__":
    main()