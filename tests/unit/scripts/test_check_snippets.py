from __future__ import annotations

from pathlib import Path

from scripts.docs.check_snippets import snippet_errors

ROOT = Path(__file__).parents[3]


def test_repository_documentation_snippets_are_current() -> None:
    assert snippet_errors(ROOT) == ()


def test_checked_copy_drift_names_the_snippet_and_owner(tmp_path: Path) -> None:
    snippet_root = tmp_path / "docs" / "snippets"
    snippet_root.mkdir(parents=True)
    (tmp_path / "README.md").write_text(
        "<!-- toetra-doc-snippet: public-call -->\n"
        "```python\n"
        "print('drifted')\n"
        "```\n",
        encoding="utf-8",
    )
    (snippet_root / "public-call.py").write_text(
        "print('canonical')\n",
        encoding="utf-8",
    )
    (snippet_root / "manifest.toml").write_text(
        "schema_version = 1\n\n"
        "[[snippet]]\n"
        'id = "public-call"\n'
        'path = "docs/snippets/public-call.py"\n'
        'language = "python"\n'
        'check = "python-compile"\n'
        "include_in = []\n"
        'copy_in = ["README.md"]\n',
        encoding="utf-8",
    )

    errors = snippet_errors(tmp_path)

    assert len(errors) == 1
    assert "public-call" in errors[0]
    assert "README.md" in errors[0]
    assert "docs/snippets/public-call.py" in errors[0]
