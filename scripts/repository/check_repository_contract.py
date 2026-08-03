"""Validate the frozen repository and its accepted P28.1 amendment."""

from __future__ import annotations

import argparse
import ast
import tomllib
from pathlib import Path
from typing import Iterable

EXPECTED_PUBLIC_API = (
    "CounterexampleReplay",
    "ReplayUnavailableError",
    "VerificationConfigurationError",
    "VerificationFinding",
    "VerificationReport",
    "VerificationRuntimeError",
    "VerificationSession",
    "VerificationStatus",
    "verify",
)
EXPECTED_SOURCE_DIRECTORIES = {
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
EXPECTED_TEST_DIRECTORIES = {
    "e2e",
    "fixtures",
    "golden",
    "integration",
    "property_based",
    "support",
    "unit",
}
EXPECTED_DEMO_DIRECTORIES = {
    "classification",
    "internals",
    "quickstart",
    "regression",
}
EXPECTED_SCRIPT_DIRECTORIES = {"ci", "docs", "release", "repository"}
EXPECTED_ACTIVE_ROADMAPS = {
    "implementation-roadmap.md",
    "open-questions.md",
}
EXPECTED_COMPLETED_ROADMAPS = {
    "binary-classification-implementation-roadmap.md",
    "documentation-roadmap.md",
    "point-binding-evaluation-implementation-roadmap.md",
    "repository-final-polish-roadmap.md",
    "toetra-identity-migration-roadmap.md",
    "v1-implementation-roadmap.md",
}
FORBIDDEN_ROOT_PATHS = {
    "dsl",
    "examples",
    "forml",
    "model",
    "test",
    "toetra",
}


class RepositoryContractError(RuntimeError):
    """Raised when the amended repository contract is violated."""


def _visible_directories(path: Path) -> set[str]:
    return {
        child.name
        for child in path.iterdir()
        if child.is_dir() and child.name != "__pycache__"
    }


def _literal_public_api(path: Path) -> tuple[str, ...]:
    module = ast.parse(path.read_text(encoding="utf-8"))
    for statement in module.body:
        if not isinstance(statement, ast.Assign):
            continue
        if not any(
            isinstance(target, ast.Name) and target.id == "__all__"
            for target in statement.targets
        ):
            continue
        value = ast.literal_eval(statement.value)
        if isinstance(value, tuple) and all(isinstance(name, str) for name in value):
            return value
    raise RepositoryContractError("src/toetra/__init__.py has no literal __all__.")


def _private_initializer_errors(source_root: Path) -> list[str]:
    errors: list[str] = []
    for directory in sorted(EXPECTED_SOURCE_DIRECTORIES):
        if not directory.startswith("_"):
            continue
        initializer = source_root / directory / "__init__.py"
        if not initializer.is_file():
            errors.append(f"Missing private package initializer: {initializer}")
            continue
        module = ast.parse(initializer.read_text(encoding="utf-8"))
        prohibited = tuple(
            statement
            for statement in module.body
            if isinstance(
                statement, (ast.Import, ast.ImportFrom, ast.Assign, ast.AnnAssign)
            )
        )
        if prohibited:
            errors.append(
                "Private package initializer must not re-export symbols: "
                f"{initializer}"
            )
    return errors


def _asset_role_errors(tests_root: Path) -> list[str]:
    errors: list[str] = []
    fixtures = tests_root / "fixtures"
    golden = tests_root / "golden"

    for name in ("golden", "expected"):
        for path in fixtures.rglob(name):
            if path.is_dir():
                errors.append(
                    "Fixture inputs must not contain expected-output directories: "
                    f"{path}"
                )
    for name in ("cases", "fixtures"):
        for path in golden.rglob(name):
            if path.is_dir():
                errors.append(
                    "Golden outputs must not contain input-fixture directories: "
                    f"{path}"
                )
    for path in golden.rglob("*.py"):
        errors.append(f"Golden output tree contains executable Python: {path}")
    return errors


def _require_exact_directories(
    root: Path,
    expected: set[str],
    *,
    label: str,
) -> list[str]:
    if not root.is_dir():
        return [f"Missing {label} root: {root}"]
    present = _visible_directories(root)
    if present == expected:
        return []
    missing = sorted(expected - present)
    unexpected = sorted(present - expected)
    return [
        f"Unexpected {label} layout at {root}: "
        f"missing={missing}, unexpected={unexpected}"
    ]


def repository_contract_errors(repository: Path) -> tuple[str, ...]:
    """Return every violation of the frozen amended repository contract."""

    repository = repository.resolve()
    source_root = repository / "src" / "toetra"
    tests_root = repository / "tests"
    errors: list[str] = []

    required_files = (
        repository / "ARCHITECTURE.md",
        repository / "CHANGELOG.md",
        repository / "COMMERCIAL_LICENSE.md",
        repository / "COPYRIGHT.md",
        repository / "LICENSE",
        repository / "Makefile",
        repository / "README.md",
        repository / "pyproject.toml",
        repository / "docs" / "contracts" / "repository-contract.md",
    )
    for path in required_files:
        if not path.is_file():
            errors.append(f"Missing repository contract file: {path}")

    for name in sorted(FORBIDDEN_ROOT_PATHS):
        path = repository / name
        if path.exists():
            errors.append(f"Obsolete repository root is present: {path}")

    errors.extend(
        _require_exact_directories(
            source_root,
            EXPECTED_SOURCE_DIRECTORIES,
            label="installable source",
        )
    )
    errors.extend(
        _require_exact_directories(
            tests_root,
            EXPECTED_TEST_DIRECTORIES,
            label="test",
        )
    )
    errors.extend(
        _require_exact_directories(
            repository / "demo",
            EXPECTED_DEMO_DIRECTORIES,
            label="demo",
        )
    )
    errors.extend(
        _require_exact_directories(
            repository / "scripts",
            EXPECTED_SCRIPT_DIRECTORIES,
            label="script",
        )
    )

    scripts_root_files = {
        path.name for path in (repository / "scripts").glob("*.py") if path.is_file()
    }
    if scripts_root_files != {"__init__.py"}:
        errors.append(
            "scripts/ must contain only __init__.py at its root: "
            f"found={sorted(scripts_root_files)}"
        )

    active = repository / "docs" / "roadmap"
    history = repository / "docs" / "history" / "roadmaps"
    active_pages = {path.name for path in active.glob("*.md")}
    completed_pages = {
        path.name for path in history.glob("*.md") if path.name != "index.md"
    }
    if active_pages != EXPECTED_ACTIVE_ROADMAPS:
        errors.append(
            "Active roadmap inventory differs from the post-P24 contract: "
            f"found={sorted(active_pages)}"
        )
    if not EXPECTED_COMPLETED_ROADMAPS.issubset(completed_pages):
        missing = sorted(EXPECTED_COMPLETED_ROADMAPS - completed_pages)
        errors.append(f"Completed roadmap history is missing: {missing}")

    project = tomllib.loads((repository / "pyproject.toml").read_text(encoding="utf-8"))
    discovery = project["tool"]["setuptools"]["packages"]["find"]
    if discovery != {"where": ["src"], "include": ["toetra*"]}:
        errors.append(f"Unexpected setuptools package discovery: {discovery!r}")

    package_data = project["tool"]["setuptools"]["package-data"]
    expected_package_data = {
        "toetra._language.grammar": ["*.lark", "*.ebnf"],
        "toetra.examples": ["*.toetra"],
    }
    if package_data != expected_package_data:
        errors.append(f"Unexpected setuptools package data: {package_data!r}")

    facade = source_root / "__init__.py"
    if facade.is_file():
        public_api = _literal_public_api(facade)
        if public_api != EXPECTED_PUBLIC_API:
            errors.append(
                "Public facade differs from the frozen V1 API: " f"found={public_api!r}"
            )

    errors.extend(_private_initializer_errors(source_root))
    errors.extend(_asset_role_errors(tests_root))

    forbidden_artifacts = tuple(repository.glob("P*_*.patch"))
    if forbidden_artifacts:
        errors.append(
            "Patch artifacts must remain outside the repository: "
            + ", ".join(str(path) for path in forbidden_artifacts)
        )

    return tuple(errors)


def validate_repository_contract(repository: Path) -> None:
    """Raise when the repository no longer matches the frozen P24 layout."""

    errors = repository_contract_errors(repository)
    if errors:
        details = "\n".join(f"- {error}" for error in errors)
        raise RepositoryContractError(
            "Toetra repository contract violations:\n" + details
        )


def _repository_from_script() -> Path:
    return Path(__file__).resolve().parents[2]


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "repository",
        nargs="?",
        type=Path,
        default=_repository_from_script(),
    )
    arguments = parser.parse_args(argv)
    validate_repository_contract(arguments.repository)
    print("Toetra repository contract: valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
