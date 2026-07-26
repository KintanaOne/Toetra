from __future__ import annotations

from pathlib import Path

from toetra._language.tools.generator import ebnf_to_lark

PROJECT_ROOT = Path(__file__).resolve().parents[3]
EBNF_PATH = (
    PROJECT_ROOT / "src" / "toetra" / "_language" / "grammar" / "toetra_grammar.ebnf"
)
LARK_PATH = (
    PROJECT_ROOT / "src" / "toetra" / "_language" / "grammar" / "toetra_grammar.lark"
)


def test_committed_lark_grammar_matches_ebnf_generation() -> None:
    generated = ebnf_to_lark(EBNF_PATH.read_text(encoding="utf-8"))
    committed = LARK_PATH.read_text(encoding="utf-8")

    assert committed == generated
