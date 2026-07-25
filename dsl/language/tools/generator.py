# dsl/language/tools/generator.py

"""
Main EBNF → Lark compiler pipeline.
"""

import re
from pathlib import Path

from dsl.language.tools.constants import build_header
from dsl.language.tools.formatter import format_lark_output
from dsl.language.tools.transforms import (
    protect_brackets,
    remove_ebnf_commas,
    unprotect_brackets,
    transform_ebnf_brackets,
    replace_all_sequences,
    normalize_whitespace,
    convert_assignment,
)
from dsl.language.tools.registry import GRAMMAR_REGISTRY


def is_advanced_rule(line: str) -> bool:
    return "->" in line or line.strip().startswith("?")


def ebnf_to_lark(ebnf_text: str) -> str:
    lines = ebnf_text.splitlines()
    lark_lines = build_header()

    for raw in lines:
        if not raw.strip():
            continue

        line = raw.strip()

        # comment
        if line.startswith("(*") and line.endswith("*)"):
            lark_lines.append("# " + line[2:-2].strip())
            continue

        # inline comments
        line = re.sub(r"\(\*(.*?)\*\)", r"# \1", line)

        # 🔥 STEP 1: convert assignment FIRST
        line = convert_assignment(line)

        # protect
        line = protect_brackets(line)

        # transform EBNF
        if not is_advanced_rule(line):
            line = transform_ebnf_brackets(line)

        line = unprotect_brackets(line)

        # line = group_or_blocks(line)

        # line = fix_neighborhood_precedence(line)

        # remove EBNF commas (CRITICAL FIX)
        line = remove_ebnf_commas(line)

        # cleanup
        line = line.rstrip(";")
        line = normalize_whitespace(line)

        # 🔥 STEP 2: replace AFTER assignment
        line = replace_all_sequences(line, GRAMMAR_REGISTRY)

        lark_lines.append(line)

    return format_lark_output(lark_lines)


def main():
    input_path = Path("dsl/language/grammar/toetra_grammar.ebnf")
    output_path = Path("dsl/language/grammar/toetra_grammar.lark")

    ebnf_text = input_path.read_text(encoding="utf-8")

    try:
        lark_text = ebnf_to_lark(ebnf_text)
        output_path.write_text(lark_text, encoding="utf-8")
        print("✅ Conversion successful")
    except KeyError as e:
        print(f"❌ Grammar error: {e}")


if __name__ == "__main__":
    main()
