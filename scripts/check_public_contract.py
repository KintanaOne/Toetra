"""Validate the public FORML V1 documentation and metadata contract."""

from __future__ import annotations

import ast
import re
import sys
import tomllib
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dsl.builder.program import parse_program  # noqa: E402
from dsl.parser.parser import parse_forml_code  # noqa: E402

EXPECTED_VERSION = "1.0.0rc1"
EXPECTED_LICENSE = "Apache-2.0"


class PublicContractError(RuntimeError):
    """Raised when public documentation and executable contracts diverge."""


def _project() -> dict[str, object]:
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return data["project"]


def _markdown_links(path: Path) -> tuple[str, ...]:
    source = path.read_text(encoding="utf-8")
    return tuple(re.findall(r"\[[^\]]+\]\(([^)]+)\)", source))


def _validate_local_links(path: Path) -> None:
    for raw_target in _markdown_links(path):
        target = unquote(raw_target.split("#", 1)[0]).strip()
        if not target or "://" in target or target.startswith("mailto:"):
            continue
        resolved = (path.parent / target).resolve()
        if not resolved.exists():
            raise PublicContractError(
                f"Broken local link in {path.relative_to(ROOT)}: {raw_target}"
            )


def _forml_blocks(path: Path) -> tuple[str, ...]:
    source = path.read_text(encoding="utf-8")
    return tuple(
        match.strip()
        for match in re.findall(r"```forml\s*\n(.*?)```", source, re.DOTALL)
    )


def _validate_forml_examples(path: Path) -> None:
    blocks = _forml_blocks(path)
    if not blocks:
        raise PublicContractError(
            f"No executable FORML example found in {path.relative_to(ROOT)}"
        )
    for index, source in enumerate(blocks, start=1):
        try:
            parse_program(parse_forml_code(source))
        except Exception as error:  # pragma: no cover - diagnostic boundary
            raise PublicContractError(
                f"Invalid FORML block {index} in {path.relative_to(ROOT)}: {error}"
            ) from error


def report_schema_version() -> int:
    source = (ROOT / "dsl" / "reporting" / "json.py").read_text(encoding="utf-8")
    module = ast.parse(source)
    for node in module.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if (
                    isinstance(target, ast.Name)
                    and target.id == "REPORT_SCHEMA_VERSION"
                ):
                    value = ast.literal_eval(node.value)
                    if isinstance(value, int):
                        return value
    raise PublicContractError("REPORT_SCHEMA_VERSION was not found")


def _validate_mkdocs_navigation() -> None:
    source = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    targets = re.findall(r":\s+([A-Za-z0-9_./-]+\.md)\s*$", source, re.MULTILINE)
    for target in targets:
        if not (ROOT / "docs" / target).is_file():
            raise PublicContractError(f"MkDocs navigation target is missing: {target}")


def check_public_contract() -> None:
    project = _project()
    if project.get("version") != EXPECTED_VERSION:
        raise PublicContractError(
            f"Expected project version {EXPECTED_VERSION}, got {project.get('version')!r}"
        )
    if project.get("license") != EXPECTED_LICENSE:
        raise PublicContractError(
            f"Expected SPDX license {EXPECTED_LICENSE}, got {project.get('license')!r}"
        )
    if report_schema_version() != 5:
        raise PublicContractError(
            "JSON report schema v5 is frozen for FORML 1.x; use a new schema "
            "version for incompatible changes."
        )

    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    if "Apache License" not in license_text or "Version 2.0" not in license_text:
        raise PublicContractError("LICENSE is not the Apache License 2.0 text")

    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    if f"[{EXPECTED_VERSION}]" not in changelog:
        raise PublicContractError("CHANGELOG does not contain the current release")

    public_documents = (
        ROOT / "README.md",
        ROOT / "ARCHITECTURE.md",
        ROOT / "docs" / "public-v1-profile.md",
        ROOT / "docs" / "getting-started" / "first-property.md",
        ROOT / "docs" / "contracts" / "public-v1-contract.md",
    )
    for document in public_documents:
        if not document.is_file():
            raise PublicContractError(
                f"Missing public contract document: {document.relative_to(ROOT)}"
            )
        _validate_local_links(document)

    for document in (
        ROOT / "README.md",
        ROOT / "docs" / "getting-started" / "first-property.md",
    ):
        _validate_forml_examples(document)

    _validate_mkdocs_navigation()

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    stale_markers = (
        "docs/scope.md",
        "docs/syntax.md",
        "docs/semantics.md",
        "Backend integrations are experimental",
        "Project licensed under MIT",
    )
    found = tuple(marker for marker in stale_markers if marker in readme)
    if found:
        raise PublicContractError(
            "README contains stale public-contract markers: " + ", ".join(found)
        )


def main() -> int:
    try:
        check_public_contract()
    except PublicContractError as error:
        print(f"Public V1 contract check failed: {error}", file=sys.stderr)
        return 1
    print("Public V1 contract: valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
