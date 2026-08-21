import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
MODEL_IR_ROOT = ROOT / "src" / "toetra" / "_models" / "ir"
MODEL_IR_BUILDER_ROOT = ROOT / "src" / "toetra" / "_models" / "ir_builder"
MODEL_LOWERING_ROOT = ROOT / "src" / "toetra" / "_compiler" / "model_lowering"
BACKENDS_ROOT = ROOT / "src" / "toetra" / "_backends"


def test_model_ir_is_framework_compiler_and_backend_independent() -> None:
    imports = _imports_under(MODEL_IR_ROOT)

    assert not _matching(
        imports,
        (
            "sklearn",
            "xgboost",
            "torch",
            "tensorflow",
            "z3",
            "toetra._compiler",
            "toetra._backends",
        ),
    )


def test_model_ir_builders_do_not_import_compiler_or_backends() -> None:
    imports = _imports_under(MODEL_IR_BUILDER_ROOT)

    assert not _matching(imports, ("toetra._compiler", "toetra._backends", "z3"))


def test_compiler_model_lowering_is_framework_and_backend_independent() -> None:
    imports = _imports_under(MODEL_LOWERING_ROOT)

    assert not _matching(
        imports,
        (
            "sklearn",
            "xgboost",
            "toetra._models.encoder",
            "toetra._backends",
            "z3",
        ),
    )


def test_backends_do_not_consume_model_ir_directly() -> None:
    imports = _imports_under(BACKENDS_ROOT)

    assert not _matching(imports, ("toetra._models.ir",))


def _imports_under(directory: Path) -> set[str]:
    imports: set[str] = set()
    for path in directory.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module is not None:
                imports.add(node.module)
    return imports


def _matching(imports: set[str], prefixes: tuple[str, ...]) -> set[str]:
    return {
        imported
        for imported in imports
        if any(
            imported == prefix or imported.startswith(f"{prefix}.")
            for prefix in prefixes
        )
    }
