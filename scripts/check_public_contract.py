"""Validate the public Toetra V1 documentation and metadata contract."""

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
from dsl.parser.parser import parse_toetra_code  # noqa: E402

EXPECTED_PROJECT_NAME = "toetra"
EXPECTED_VERSION = "1.0.0rc3"
EXPECTED_LICENSE = "Apache-2.0"

CLASSIFICATION_TARGET_DOCUMENTS = (
    ROOT / "docs" / "adr" / "ADR-0023-typed-model-outputs-and-observables.md",
    ROOT / "docs" / "adr" / "ADR-0024-model-semantic-lowering.md",
    ROOT / "docs" / "adr" / "ADR-0025-binary-classification-profile.md",
    ROOT / "docs" / "contracts" / "model-output-observables.md",
    ROOT / "docs" / "contracts" / "model-semantic-lowering.md",
    ROOT / "docs" / "contracts" / "binary-classification-profile.md",
    ROOT / "docs" / "language" / "model-output-observables.md",
    ROOT / "docs" / "testing" / "binary-classification-test-matrix.md",
    ROOT / "docs" / "roadmap" / "binary-classification-implementation-roadmap.md",
)

CLASSIFICATION_AMENDED_DOCUMENTS = (
    ROOT / "docs" / "adr" / "ADR-0008-modelschema-as-bridge.md",
    ROOT / "docs" / "adr" / "ADR-0014-scalar-expression-comparisons.md",
    ROOT
    / "docs"
    / "adr"
    / "ADR-0017-first-class-points-and-indexed-model-evaluations.md",
    ROOT / "docs" / "adr" / "ADR-0018-numeric-semantics-and-backend-compatibility.md",
    ROOT / "docs" / "adr" / "ADR-0020-verification-provenance.md",
    ROOT / "docs" / "contracts" / "model-to-schema.md",
    ROOT / "docs" / "contracts" / "schema-to-semantic.md",
    ROOT / "docs" / "contracts" / "semantic-to-ir1.md",
    ROOT / "docs" / "contracts" / "ir1-to-ir2.md",
    ROOT / "docs" / "contracts" / "model-constraints.md",
)


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


def _toetra_blocks(path: Path) -> tuple[str, ...]:
    source = path.read_text(encoding="utf-8")
    return tuple(
        match.strip()
        for match in re.findall(r"```toetra\s*\n(.*?)```", source, re.DOTALL)
    )


def _validate_toetra_examples(path: Path) -> None:
    blocks = _toetra_blocks(path)
    if not blocks:
        raise PublicContractError(
            f"No executable Toetra example found in {path.relative_to(ROOT)}"
        )
    for index, source in enumerate(blocks, start=1):
        try:
            parse_program(parse_toetra_code(source))
        except Exception as error:  # pragma: no cover - diagnostic boundary
            raise PublicContractError(
                f"Invalid Toetra block {index} in {path.relative_to(ROOT)}: {error}"
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


def report_schema_identities() -> tuple[str, str]:
    source = (ROOT / "dsl" / "reporting" / "json.py").read_text(encoding="utf-8")
    module = ast.parse(source)
    values: dict[str, str] = {}
    for node in module.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if not isinstance(target, ast.Name):
                continue
            if target.id not in {"REPORT_SCHEMA", "REPORT_COLLECTION_SCHEMA"}:
                continue
            value = ast.literal_eval(node.value)
            if isinstance(value, str):
                values[target.id] = value
    try:
        return values["REPORT_SCHEMA"], values["REPORT_COLLECTION_SCHEMA"]
    except KeyError as error:
        raise PublicContractError("Report schema identifiers were not found") from error


def _validate_mkdocs_navigation() -> None:
    source = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    targets = re.findall(r":\s+([A-Za-z0-9_./-]+\.md)\s*$", source, re.MULTILINE)
    for target in targets:
        if not (ROOT / "docs" / target).is_file():
            raise PublicContractError(f"MkDocs navigation target is missing: {target}")


def _validate_classification_target_contract() -> None:
    """Validate the public Patch 21 binary-classification contract."""

    for document in (
        *CLASSIFICATION_TARGET_DOCUMENTS,
        *CLASSIFICATION_AMENDED_DOCUMENTS,
    ):
        if not document.is_file():
            raise PublicContractError(
                "Missing Patch 21 target document: " f"{document.relative_to(ROOT)}"
            )
        _validate_local_links(document)

    for document in CLASSIFICATION_TARGET_DOCUMENTS[:6]:
        source = document.read_text(encoding="utf-8")
        if "1.0.0rc2" not in source:
            raise PublicContractError(
                "Patch 21 normative document is not marked public for rc2: "
                f"{document.relative_to(ROOT)}"
            )
        if "public adoption pending" in source:
            raise PublicContractError(
                "Patch 21 normative document still declares pending adoption: "
                f"{document.relative_to(ROOT)}"
            )

    language = (ROOT / "docs" / "language" / "model-output-observables.md").read_text(
        encoding="utf-8"
    )
    required_language_markers = (
        'target[x0].label == "approved"',
        'target[x0].probability("approved") >= 0.80',
        "intentionally not DSL observables",
        "positive-class probability > 0.5",
        "positive-class probability <= 0.5",
    )
    missing_language = tuple(
        marker for marker in required_language_markers if marker not in language
    )
    if missing_language:
        raise PublicContractError(
            "Patch 21 language contract is missing markers: "
            + ", ".join(missing_language)
        )

    profile = (
        ROOT / "docs" / "contracts" / "binary-classification-profile.md"
    ).read_text(encoding="utf-8")
    required_profile_markers = (
        "direct fitted `sklearn.linear_model.LogisticRegression`",
        "`FixedThresholdClassifier`",
        "`TunedThresholdClassifierCV`",
        "`CalibratedClassifierCV`",
        "negative label",
        "property threshold",
    )
    missing_profile = tuple(
        marker for marker in required_profile_markers if marker not in profile
    )
    if missing_profile:
        raise PublicContractError(
            "Patch 21 binary profile is missing markers: " + ", ".join(missing_profile)
        )

    amended_markers = {
        "ADR-0008-modelschema-as-bridge.md": "Patch 21 target amendment",
        "ADR-0014-scalar-expression-comparisons.md": ("Patch 21 target amendment"),
        "ADR-0017-first-class-points-and-indexed-model-evaluations.md": (
            "Patch 21 target amendment"
        ),
        "ADR-0018-numeric-semantics-and-backend-compatibility.md": (
            "Patch 21 application"
        ),
        "ADR-0020-verification-provenance.md": "Patch 21 application",
        "model-to-schema.md": "Patch 21 Typed Output Addendum",
        "schema-to-semantic.md": "Patch 21 Output-Observable Addendum",
        "semantic-to-ir1.md": "Patch 21 Output-Observable Addendum",
        "ir1-to-ir2.md": "Patch 21 Model-Semantic Lowering Addendum",
        "model-constraints.md": ("Patch 21 Model Quantities and Observable Lowering"),
    }
    for document in CLASSIFICATION_AMENDED_DOCUMENTS:
        required_marker = amended_markers[document.name]
        if required_marker not in document.read_text(encoding="utf-8"):
            raise PublicContractError(
                "Patch 21 amendment marker is missing from "
                f"{document.relative_to(ROOT)}"
            )

    current_profile = (ROOT / "docs" / "public-v1-profile.md").read_text(
        encoding="utf-8"
    )
    current_markers = (
        "Release candidate: `1.0.0rc3`",
        "fitted single-output `LinearRegression`",
        "direct fitted binary `LogisticRegression`",
        "target[point].label",
        "target[point].probability(label)",
        "CLASSIFICATION.EQUAL()",
        "`FixedThresholdClassifier`",
    )
    missing_current = tuple(
        marker for marker in current_markers if marker not in current_profile
    )
    if missing_current:
        raise PublicContractError(
            "Current public rc3 profile is missing markers: "
            + ", ".join(missing_current)
        )

    release_documents = (
        ROOT / "docs" / "adr" / "ADR-0026-public-v1-binary-classification-extension.md",
        ROOT / "docs" / "releases" / "1.0.0rc2.md",
        ROOT / "docs" / "releases" / "1.0.0rc3.md",
    )
    for document in release_documents:
        if not document.is_file():
            raise PublicContractError(
                f"Missing release document: {document.relative_to(ROOT)}"
            )
        _validate_local_links(document)

    demo = ROOT / "demo" / "classification" / "binary_classification_policy.toetra"
    if not demo.is_file():
        raise PublicContractError("Missing binary-classification release demo")
    try:
        parse_program(parse_toetra_code(demo.read_text(encoding="utf-8")))
    except Exception as error:
        raise PublicContractError(
            f"Invalid binary-classification release demo: {error}"
        ) from error


def _validate_sdist_manifest() -> None:
    manifest_path = ROOT / "MANIFEST.in"
    if not manifest_path.is_file():
        raise PublicContractError("MANIFEST.in is missing")

    directives = {
        line.strip()
        for line in manifest_path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    required = {
        "include LICENSE",
        "include README.md",
        "include CHANGELOG.md",
        "include pyproject.toml",
        "recursive-include dsl/language/grammar *.ebnf *.lark",
        "recursive-include toetra/examples *.toetra",
    }
    missing = sorted(required - directives)
    if missing:
        raise PublicContractError(
            "MANIFEST.in is missing required release directives: " + ", ".join(missing)
        )


def check_public_contract() -> None:
    project = _project()
    if project.get("name") != EXPECTED_PROJECT_NAME:
        raise PublicContractError(
            f"Expected project name {EXPECTED_PROJECT_NAME!r}, "
            f"got {project.get('name')!r}"
        )
    if project.get("version") != EXPECTED_VERSION:
        raise PublicContractError(
            f"Expected project version {EXPECTED_VERSION}, got {project.get('version')!r}"
        )
    if project.get("license") != EXPECTED_LICENSE:
        raise PublicContractError(
            f"Expected SPDX license {EXPECTED_LICENSE}, got {project.get('license')!r}"
        )
    if report_schema_version() != 6:
        raise PublicContractError(
            "JSON report schema v6 is frozen for the Toetra identity; use a new schema "
            "version for incompatible changes."
        )
    expected_schema_ids = (
        "toetra.verification-report",
        "toetra.verification-report-collection",
    )
    if report_schema_identities() != expected_schema_ids:
        raise PublicContractError(
            "JSON report schema identifiers must use the canonical Toetra identity."
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
        _validate_toetra_examples(document)

    _validate_mkdocs_navigation()
    _validate_classification_target_contract()
    _validate_sdist_manifest()

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
