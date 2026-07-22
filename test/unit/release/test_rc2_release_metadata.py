from __future__ import annotations

from pathlib import Path

from scripts.prepare_rc2_changelog import RELEASE_MARKER, update_changelog


def test_rc2_changelog_update_is_idempotent_and_preserves_history(
    tmp_path: Path,
) -> None:
    path = tmp_path / "CHANGELOG.md"
    path.write_text("# Changelog\n\n## [1.0.0rc1]\n\nOld notes.\n", encoding="utf-8")
    assert update_changelog(path) is True
    assert update_changelog(path) is False
    source = path.read_text(encoding="utf-8")
    assert source.count(RELEASE_MARKER) == 1
    assert "[1.0.0rc1]" in source
