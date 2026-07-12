"""Migrate historical FORML source strings to the G1 language syntax.

This is deliberately an allow-listed repository migration, not a general-purpose
source-to-source compiler. It only rewrites known historical test/demo files.

Usage from the repository root:

    python scripts/migrations/migrate_g1_historical_syntax.py --check
    python scripts/migrations/migrate_g1_historical_syntax.py --write
    python scripts/migrations/migrate_g1_historical_syntax.py --self-test
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

QUANTIFIER_TARGETS = {
    "dsl/ir/ir2/examples/samples.py",
    "dsl/ir/normalization/run_nnf.py",
    "test/fixtures/program_samples.py",
    "test/unit/parsing/test_footer.py",
    "test/unit/semantic/test_attribute_semantic_binding.py",
    "test/e2e/normalization/nnf/test_run_nnf.py",
    "test/e2e/normalization/test_run_nnf.py",
    "test/golden/ir2/test_ir2_golden.py",
    "test/golden/normalization/nnf/test_nnf_golden.py",
    "test/integration/normalization/nnf/test_ir1_to_nnf_quantifiers.py",
    "test/unit/ir/test_comparison_ir_schema_types.py",
    "test/e2e/backends/test_z3_domain_assumptions.py",
}

DOMAIN_TARGETS = {
    "test/fixtures/program_samples.py",
    "test/e2e/backends/test_z3_domain_assumptions.py",
    "test/golden/normalization/nnf/test_nnf_golden.py",
    "test/integration/normalization/nnf/test_ir1_to_nnf_quantifiers.py",
}

ALL_TARGETS = QUANTIFIER_TARGETS | DOMAIN_TARGETS


_QUANTIFIER_RULES: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bforall\s+with\s+domain\s*\("), "forall x0 with domain("),
    (re.compile(r"\bexists\s+with\s+domain\s*\("), "exists x0 with domain("),
    (re.compile(r"∀\s+with\s+domain\s*\("), "∀ x0 with domain("),
    (re.compile(r"∃\s+with\s+domain\s*\("), "∃ x0 with domain("),
    (re.compile(r"\bforall\s*(?==>)"), "forall x0 "),
    (re.compile(r"\bexists\s*(?==>)"), "exists x0 "),
    (re.compile(r"∀\s*(?==>)"), "∀ x0 "),
    (re.compile(r"∃\s*(?==>)"), "∃ x0 "),
)

_DOMAIN_EXACT_REPLACEMENTS: tuple[tuple[str, str], ...] = (
    (
        'with gender("male", "female")',
        'with domain(x0.gender: {"male", "female"})',
    ),
    (
        'with gender("male","female")',
        'with domain(x0.gender: {"male", "female"})',
    ),
    (
        'with sex("male", "female")',
        'with domain(x0.sex: {"male", "female"})',
    ),
    (
        'with sex("male","female")',
        'with domain(x0.sex: {"male", "female"})',
    ),
    (
        "with age(18, 65)",
        "with domain(x0.age: [18, 65])",
    ),
)

_STALE_QUANTIFIER = re.compile(r"(?:\bforall|\bexists|∀|∃)\s*(?:=>|with\b)")
_STALE_DOMAIN = re.compile(r"\bwith\s+(?:sex|gender|age)\s*\(")


def _relative_posix(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def migrate_text(relative_path: str, text: str) -> str:
    """Return migrated content for one allow-listed repository path."""

    migrated = text

    # Domain calls must be normalized first. A historical form such as
    # ``forall with gender(...)`` becomes ``forall with domain(...)`` and can
    # then receive its explicit quantified identifier in the next pass.
    if relative_path in DOMAIN_TARGETS:
        for old, new in _DOMAIN_EXACT_REPLACEMENTS:
            migrated = migrated.replace(old, new)

    if relative_path in QUANTIFIER_TARGETS:
        for pattern, replacement in _QUANTIFIER_RULES:
            migrated = pattern.sub(replacement, migrated)

    return migrated


def stale_reasons(relative_path: str, text: str) -> tuple[str, ...]:
    reasons: list[str] = []

    if relative_path in QUANTIFIER_TARGETS and _STALE_QUANTIFIER.search(text):
        reasons.append("legacy quantifier syntax without explicit identifier")

    if relative_path in DOMAIN_TARGETS and _STALE_DOMAIN.search(text):
        reasons.append("legacy named-domain call instead of with domain(...)")

    return tuple(reasons)


def run(root: Path, *, write: bool) -> int:
    changed: list[str] = []
    stale: list[tuple[str, tuple[str, ...]]] = []

    for relative_path in sorted(ALL_TARGETS):
        path = root / relative_path
        if not path.exists():
            continue

        original = path.read_text(encoding="utf-8")
        migrated = migrate_text(relative_path, original)

        if migrated != original:
            changed.append(relative_path)
            if write:
                path.write_text(migrated, encoding="utf-8")

        inspected = migrated if write else original
        reasons = stale_reasons(relative_path, inspected)
        if reasons:
            stale.append((relative_path, reasons))

    if changed:
        action = "updated" if write else "would update"
        print(f"G1-S: {action} {len(changed)} file(s):")
        for relative_path in changed:
            print(f"  - {relative_path}")

    if stale:
        print("G1-S: stale historical syntax remains:")
        for relative_path, reasons in stale:
            print(f"  - {relative_path}: {', '.join(reasons)}")
        return 1

    if not changed:
        print("G1-S: no migration required; allow-listed files are clean.")

    if changed and not write:
        print("Run again with --write to apply the migration.")
        return 1

    return 0


def self_test() -> None:
    quantifier_source = """
model := "model.onnx"
target := MyTarget

[LOGIC]:
forall => a <= 1

[LOGIC]:
∃ => b <= 2
"""
    migrated = migrate_text(
        "test/golden/normalization/nnf/test_nnf_golden.py",
        quantifier_source,
    )
    assert "forall x0 =>" in migrated
    assert "∃ x0 =>" in migrated

    domain_source = """
model := "model.onnx"
target := MyTarget

[LOGIC]:
forall with gender("male", "female") => a <= 1
"""
    migrated = migrate_text(
        "test/fixtures/program_samples.py",
        domain_source,
    )
    assert 'forall x0 with domain(x0.gender: {"male", "female"})' in migrated
    assert stale_reasons("test/fixtures/program_samples.py", migrated) == ()

    untouched = migrate_text("test/unit/parser/test_quantified_scopes.py", "forall =>")
    assert untouched == "forall =>"

    print("G1-S migration self-test passed.")


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--self-test", action="store_true")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return 0

    return run(args.root, write=args.write)


if __name__ == "__main__":
    raise SystemExit(main())
