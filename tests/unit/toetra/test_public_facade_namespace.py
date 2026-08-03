from __future__ import annotations

import ast
from pathlib import Path

import toetra as toetra_module


def test_lazy_facade_declares_only_private_helper_imports() -> None:
    source = Path(toetra_module.__file__).read_text(encoding="utf-8")
    module = ast.parse(source)

    imported_names: set[str] = set()
    for statement in module.body:
        if isinstance(statement, ast.Import):
            imported_names.update(
                alias.asname or alias.name.split(".", maxsplit=1)[0]
                for alias in statement.names
            )
        elif isinstance(statement, ast.ImportFrom):
            imported_names.update(
                alias.asname or alias.name for alias in statement.names
            )

    assert all(name.startswith("_") for name in imported_names)


def test_lazy_facade_initial_namespace_has_no_public_helpers() -> None:
    public_names = {name for name in vars(toetra_module) if not name.startswith("_")}

    assert public_names <= set(toetra_module.__all__) | {"examples"}
