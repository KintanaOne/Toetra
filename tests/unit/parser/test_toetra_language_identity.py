from __future__ import annotations

from pathlib import Path

import toetra._compiler.parser.parser as parser_module

PROJECT_ROOT = Path(__file__).resolve().parents[3]
GRAMMAR_ROOT = PROJECT_ROOT / "src" / "toetra" / "_language" / "grammar"


def test_parser_exposes_only_toetra_named_entry_point() -> None:
    assert callable(parser_module.parse_toetra_code)
    assert not hasattr(parser_module, "parse_forml_code")


def test_canonical_grammar_files_use_toetra_identity() -> None:
    assert (GRAMMAR_ROOT / "toetra_grammar.ebnf").is_file()
    assert (GRAMMAR_ROOT / "toetra_grammar.lark").is_file()
    assert not (GRAMMAR_ROOT / "forml_grammar.ebnf").exists()
    assert not (GRAMMAR_ROOT / "forml_grammar.lark").exists()


def test_repository_contains_no_legacy_specification_files() -> None:
    source_roots = ("demo", "docs", "src", "test")
    legacy_files = tuple(
        path.relative_to(PROJECT_ROOT)
        for root_name in source_roots
        for path in (PROJECT_ROOT / root_name).rglob("*.forml")
    )
    assert legacy_files == ()
