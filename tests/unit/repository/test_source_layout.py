from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).parents[3]
SOURCE_ROOT = ROOT / "src" / "toetra"


def test_installable_code_uses_one_src_based_top_level_package() -> None:
    assert SOURCE_ROOT.is_dir()
    assert (SOURCE_ROOT / "__init__.py").is_file()
    assert not (ROOT / "toetra").exists()
    assert not (ROOT / "dsl").exists()
    assert not (ROOT / "model").exists()


def test_setuptools_discovers_only_toetra_from_src() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    discovery = project["tool"]["setuptools"]["packages"]["find"]

    assert discovery["where"] == ["src"]
    assert discovery["include"] == ["toetra*"]


def test_private_subsystems_match_the_accepted_layout() -> None:
    expected = {
        "_backends",
        "_cli",
        "_compatibility",
        "_compiler",
        "_language",
        "_models",
        "_provenance",
        "_reporting",
        "_runtime",
        "examples",
    }
    present = {
        path.name
        for path in SOURCE_ROOT.iterdir()
        if path.is_dir() and path.name != "__pycache__"
    }

    assert present == expected
