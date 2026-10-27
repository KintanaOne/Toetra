from __future__ import annotations

import re
from pathlib import Path

import pytest

from scripts.repository.check_public_collaboration import (
    EXPECTED_PUBLIC_FILES,
    public_collaboration_errors,
)

ROOT = Path(__file__).parents[3]


def _collaboration_fixture(tmp_path: Path) -> Path:
    repository = tmp_path / "Toetra"
    for raw_path in EXPECTED_PUBLIC_FILES:
        source = ROOT / raw_path
        destination = repository / raw_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(source.read_bytes())
    return repository


def test_current_repository_satisfies_public_collaboration_contract() -> None:
    assert public_collaboration_errors(ROOT) == ()


def test_collaboration_check_rejects_privileged_pull_request_trigger(
    tmp_path: Path,
) -> None:
    repository = _collaboration_fixture(tmp_path)
    workflow = repository / ".github" / "workflows" / "ci.yml"
    source = workflow.read_text(encoding="utf-8")
    workflow.write_text(
        source.replace("  pull_request:\n", "  pull_request_target:\n"),
        encoding="utf-8",
    )

    errors = public_collaboration_errors(repository)

    assert any("pull_request_target:" in error for error in errors)


def test_collaboration_check_rejects_mutable_action_reference(
    tmp_path: Path,
) -> None:
    repository = _collaboration_fixture(tmp_path)
    workflow = repository / ".github" / "workflows" / "ci.yml"
    source = workflow.read_text(encoding="utf-8")
    mutated_source, replacement_count = re.subn(
        r"actions/checkout@[0-9a-f]{40}",
        "actions/checkout@v4",
        source,
        count=1,
    )
    assert replacement_count == 1
    workflow.write_text(mutated_source, encoding="utf-8")

    errors = public_collaboration_errors(repository)

    assert any("not pinned to a full commit SHA" in error for error in errors)


def test_collaboration_check_rejects_write_permission_and_secret_use(
    tmp_path: Path,
) -> None:
    repository = _collaboration_fixture(tmp_path)
    workflow = repository / ".github" / "workflows" / "ci.yml"
    source = workflow.read_text(encoding="utf-8")
    workflow.write_text(
        source.replace(
            "permissions:\n  contents: read",
            "permissions:\n  contents: write",
        )
        + "\n# ${{ secrets.PUBLICATION_TOKEN }}\n",
        encoding="utf-8",
    )

    errors = public_collaboration_errors(repository)

    assert any("write-capable workflow permission" in error for error in errors)
    assert any("secrets." in error for error in errors)


@pytest.mark.parametrize(
    ("before", "after"),
    [
        ("  workflow_dispatch:", "  push:"),
        ("needs: verify", "needs: []"),
        ("github.ref == 'refs/heads/main'", "true"),
        ("      name: pypi", "      name: unprotected"),
        ("      id-token: write", "      contents: write"),
        ("          digest-mismatch: error", "          digest-mismatch: warn"),
        ('          skip-existing: "false"', '          skip-existing: "true"'),
        ("./.github/workflows/ci.yml", "./.github/workflows/other.yml"),
    ],
)
def test_pypi_contract_rejects_bypassing_publication_gates(
    tmp_path: Path, before: str, after: str
) -> None:
    repository = _collaboration_fixture(tmp_path)
    workflow = repository / ".github/workflows/publish-pypi.yml"
    source = workflow.read_text()
    assert before in source
    workflow.write_text(source.replace(before, after))
    assert public_collaboration_errors(repository)


def test_pypi_permissions_remain_forbidden_in_pull_request_ci(tmp_path: Path) -> None:
    repository = _collaboration_fixture(tmp_path)
    workflow = repository / ".github/workflows/ci.yml"
    workflow.write_text(workflow.read_text() + "\n# pypa/gh-action-pypi-publish\n")
    assert any(
        "forbidden workflow marker" in error
        for error in public_collaboration_errors(repository)
    )
