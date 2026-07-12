"""Finish historical contract stabilization after explicit quantifiers and typed domains.

This repository migration is deliberately narrow and idempotent. It updates
only known tests, fixtures, and golden artifacts affected by G2-A/G2-B.

Usage from the repository root::

    python scripts/migrations/migrate_g2b_typed_domain_tests.py --self-test
    python scripts/migrations/migrate_g2b_typed_domain_tests.py --write
    python scripts/migrations/migrate_g2b_typed_domain_tests.py --check
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

TEXT_TARGETS = {
    "test/e2e/backends/test_z3_domain_assumptions.py",
    "test/e2e/normalization/nnf/test_run_nnf.py",
    "test/e2e/normalization/test_run_nnf.py",
    "test/fixtures/normalization/nnf/helpers.py",
    "test/integration/normalization/nnf/test_ir1_to_nnf_quantifiers.py",
    "test/unit/ir/test_comparison_ir_schema_types.py",
    "test/unit/normalization/nnf/test_nnf_quantifier_scope_passthrough.py",
    "test/unit/semantic/test_attribute_semantic_binding.py",
    "test/unit/parsing/test_semantic.py",
    "test/unit/parsing/helper.py",
}

GOLDEN_SOURCE_TARGETS = {
    "test/golden/ir2/cases/forall_implication.forml",
    "test/golden/normalization/nnf/cases/forall_demorgan.forml",
    "test/golden/normalization/nnf/cases/exists_implication.forml",
    "test/golden/normalization/nnf/cases/forall_domain_demorgan_or.forml",
}

GOLDEN_EXPECTED_TARGETS = {
    "test/golden/ir2/expected/forall_implication.ir2.txt",
    "test/golden/normalization/nnf/expected/forall_demorgan.nnf.txt",
    "test/golden/normalization/nnf/expected/exists_implication.nnf.txt",
    "test/golden/normalization/nnf/expected/forall_domain_demorgan_or.nnf.txt",
}

# The exact filename containing FORALL_IMPLICIT_AGE may vary between repository
# revisions. Only this narrow fixture directory is searched dynamically.
DYNAMIC_FIXTURE_DIRS = {
    "test/fixtures/ir_schema_aware",
}

ALL_STATIC_TARGETS = TEXT_TARGETS | GOLDEN_SOURCE_TARGETS | GOLDEN_EXPECTED_TARGETS

_QUANTIFIER_RULES: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bforall\s*(?==>)"), "forall x0 "),
    (re.compile(r"\bexists\s*(?==>)"), "exists x0 "),
    (re.compile(r"∀\s*(?==>)"), "∀ x0 "),
    (re.compile(r"∃\s*(?==>)"), "∃ x0 "),
)

_OLD_SEGMENT_DOMAIN = re.compile(
    r"forall\s+with\s+Segment\(\s*[\"']A[\"']\s*,\s*[\"']B[\"']\s*\)"
)

_DUPLICATED_FORALL_BEFORE_DOMAIN = re.compile(
    r"(?m)^(?P<first_indent>[ \t]*)forall x0[ \t]*\n"
    r"(?P<second_indent>[ \t]*)forall x0[ \t]*\n"
    r"(?P<domain_indent>[ \t]*)with domain\("
)

_CONSECUTIVE_FORALL = re.compile(
    r"(?m)^[ \t]*forall x0[ \t]*\n[ \t]*forall x0(?:[ \t]*\n|[ \t]*$)"
)

_BARE_BOUND_DOMAIN = re.compile(
    r"(?m)^(?P<header_indent>[ \t]*)\[BOUND\]:[ \t]*\n"
    r"(?P<body_indent>[ \t]+)with domain\("
)

_LEGACY_DOMAIN_CONSTRUCTOR = re.compile(
    r"DomainIR\(\s*name=[\"']Segment[\"']\s*,\s*"
    r"args=\{[\"']values[\"']:\s*\[[\"']A[\"'],\s*[\"']B[\"']\]\}\s*\)",
    re.MULTILINE,
)

_SCOPE_DOMAIN_HELPER = re.compile(
    r"(?ms)^def assert_scope_domain_values\(.*?(?=^def |\Z)"
)

_TYPED_SCOPE_DOMAIN_HELPER = '''def assert_scope_domain_values(
    task: VerificationTask,
    name: str,
    values: list[object],
    *,
    entity: str = "x0",
) -> None:
    """Assert one finite-set domain entry preserved in the IR1 scope."""

    from dsl.ir.ir1.nodes import (
        ConstantExpressionIR,
        FiniteSetDomainIR,
        SymbolLiteralIR,
    )

    domain = task.scope.domain
    assert domain is not None
    assert len(domain.entries) == 1

    entry = domain.entries[0]
    assert entry.entity == entity
    assert entry.feature == name
    assert isinstance(entry.constraint, FiniteSetDomainIR)

    actual_values = [
        value.name
        if isinstance(value, SymbolLiteralIR)
        else value.value
        if isinstance(value, ConstantExpressionIR)
        else value
        for value in entry.constraint.values
    ]
    assert actual_values == values


'''

_TYPED_DOMAIN_CONSTRUCTOR = """DomainIR(
                entries=(
                    DomainEntryIR(
                        entity="x0",
                        feature="Segment",
                        constraint=FiniteSetDomainIR(
                            values=(
                                SymbolLiteralIR("A"),
                                SymbolLiteralIR("B"),
                            )
                        ),
                    ),
                )
            )"""

_EXTRA_IR_IMPORT = (
    "from dsl.ir.ir1.nodes import "
    "DomainEntryIR, FiniteSetDomainIR, SymbolLiteralIR\n"
)


def _migrate_quantifier_syntax(text: str) -> str:
    migrated = text
    for pattern, replacement in _QUANTIFIER_RULES:
        migrated = pattern.sub(replacement, migrated)

    migrated = _OLD_SEGMENT_DOMAIN.sub(
        'forall x0 with domain(x0.Segment: {"A", "B"})',
        migrated,
    )

    # Parameterized Unicode tests now require a declared identifier too.
    migrated = migrated.replace("{token} =>", "{token} x0 =>")
    return migrated


def _normalize_domain_scope(relative_path: str, text: str) -> str:
    if relative_path != "test/e2e/backends/test_z3_domain_assumptions.py":
        return text

    migrated = text

    # Repair the non-idempotent output of the previous migration version.
    while _DUPLICATED_FORALL_BEFORE_DOMAIN.search(migrated):
        migrated = _DUPLICATED_FORALL_BEFORE_DOMAIN.sub(
            lambda match: (
                f"{match.group('first_indent')}forall x0\n"
                f"{match.group('domain_indent')}with domain("
            ),
            migrated,
        )

    # Migrate a still-bare BOUND domain exactly once.
    migrated = _BARE_BOUND_DOMAIN.sub(
        lambda match: (
            f"{match.group('header_indent')}[BOUND]:\n"
            f"{match.group('body_indent')}forall x0\n"
            f"{match.group('body_indent')}    with domain("
        ),
        migrated,
    )

    return migrated


def _migrate_explicit_binding_expectations(text: str) -> str:
    migrated = text.replace('{"_x": "symbolic"}', '{"x0": "symbolic"}')
    migrated = migrated.replace("variables=_x:symbolic", "variables=x0:symbolic")
    migrated = migrated.replace("_x.a", "x0.a")
    migrated = migrated.replace("_x.b", "x0.b")
    migrated = migrated.replace('resolved_entity == "_x"', 'resolved_entity == "x0"')
    migrated = migrated.replace(
        'resolved_path == ["_x", "age"]',
        'resolved_path == ["x0", "age"]',
    )
    migrated = migrated.replace(
        "implicit symbolic entity `_x` for forall/exists",
        "explicit symbolic entity declared by forall/exists",
    )
    return migrated


def _migrate_scope_domain_helper(relative_path: str, text: str) -> str:
    if relative_path != "test/fixtures/normalization/nnf/helpers.py":
        return text
    if "def assert_scope_domain_values(" not in text:
        return text
    return _SCOPE_DOMAIN_HELPER.sub(_TYPED_SCOPE_DOMAIN_HELPER, text, count=1)


def _migrate_manual_domain_ir(relative_path: str, text: str) -> str:
    if (
        relative_path
        != "test/unit/normalization/nnf/test_nnf_quantifier_scope_passthrough.py"
    ):
        return text

    migrated = _LEGACY_DOMAIN_CONSTRUCTOR.sub(_TYPED_DOMAIN_CONSTRUCTOR, text)

    if (
        "DomainEntryIR(" in migrated
        and "from dsl.ir.ir1.nodes import DomainEntryIR" not in migrated
    ):
        future_import = "from __future__ import annotations\n"
        if future_import in migrated:
            migrated = migrated.replace(
                future_import,
                future_import + _EXTRA_IR_IMPORT,
                1,
            )
        else:
            migrated = _EXTRA_IR_IMPORT + migrated

    return migrated


def _migrate_remaining_explicit_binding_contracts(
    relative_path: str,
    text: str,
) -> str:
    migrated = text

    if relative_path == "test/unit/ir/test_comparison_ir_schema_types.py":
        migrated = migrated.replace(
            'assert comparison.entity == "_x"',
            'assert comparison.entity == "x0"',
        )

    if (
        relative_path
        == "test/unit/normalization/nnf/test_nnf_quantifier_scope_passthrough.py"
    ):
        migrated = migrated.replace('entity="_x"', 'entity="x0"')

    return migrated


def migrate_text(relative_path: str, text: str) -> str:
    migrated = _migrate_quantifier_syntax(text)
    migrated = _normalize_domain_scope(relative_path, migrated)
    migrated = _migrate_explicit_binding_expectations(migrated)
    migrated = _migrate_scope_domain_helper(relative_path, migrated)
    migrated = _migrate_manual_domain_ir(relative_path, migrated)
    migrated = _migrate_remaining_explicit_binding_contracts(relative_path, migrated)
    return migrated


def _dynamic_targets(root: Path) -> set[str]:
    targets: set[str] = set()
    for relative_dir in DYNAMIC_FIXTURE_DIRS:
        directory = root / relative_dir
        if not directory.exists():
            continue
        for path in directory.rglob("*.py"):
            targets.add(path.relative_to(root).as_posix())
    return targets


def stale_reasons(relative_path: str, text: str) -> tuple[str, ...]:
    reasons: list[str] = []

    if re.search(r"(?:\bforall|\bexists|∀|∃)\s*=>", text):
        reasons.append("quantifier without explicit identifier")
    if "{token} =>" in text:
        reasons.append("parameterized Unicode quantifier without identifier")
    if "forall with Segment(" in text:
        reasons.append("legacy named domain syntax")
    if "variables=_x:symbolic" in text:
        reasons.append("legacy golden symbolic variable")
    if '{"_x": "symbolic"}' in text or "_x.a" in text or "_x.b" in text:
        reasons.append("legacy implicit _x expectation")
    if 'resolved_path == ["_x", "age"]' in text:
        reasons.append("legacy semantic resolved path")
    if ".scope.domain.name" in text or ".scope.domain.values" in text:
        reasons.append("legacy DomainIR name/values expectation")
    if "DomainIR(name=" in text:
        reasons.append("legacy DomainIR constructor")
    if _DUPLICATED_FORALL_BEFORE_DOMAIN.search(text) or _CONSECUTIVE_FORALL.search(
        text
    ):
        reasons.append("duplicated forall before typed domain")
    if (
        relative_path == "test/unit/ir/test_comparison_ir_schema_types.py"
        and 'comparison.entity == "_x"' in text
    ):
        reasons.append("legacy IR comparison entity expectation")
    if (
        relative_path
        == "test/unit/normalization/nnf/test_nnf_quantifier_scope_passthrough.py"
        and 'entity="_x"' in text
    ):
        reasons.append("legacy manually constructed IR entity")

    return tuple(reasons)


def run(root: Path, *, write: bool) -> int:
    targets = ALL_STATIC_TARGETS | _dynamic_targets(root)
    changed: list[str] = []
    stale: list[tuple[str, tuple[str, ...]]] = []

    for relative_path in sorted(targets):
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
        print(f"G2-B.3 migration: {action} {len(changed)} file(s):")
        for relative_path in changed:
            print(f"  - {relative_path}")

    if stale:
        print("G2-B.3 migration: stale contracts remain:")
        for relative_path, reasons in stale:
            print(f"  - {relative_path}: {', '.join(reasons)}")
        return 1

    if not changed:
        print("G2-B.3 migration: allow-listed files are clean.")

    if changed and not write:
        print("Run again with --write to apply the migration.")
        return 1

    return 0


def self_test() -> None:
    sample = """
[LOGIC]:
∀ => NOT (a <= 1 AND b <= 2)
assert task.scope.variables == {"_x": "symbolic"}
SCOPE variables=_x:symbolic
assert semantic.resolved_path == ["_x", "age"]
"""
    migrated = migrate_text(
        "test/integration/normalization/nnf/test_ir1_to_nnf_quantifiers.py",
        sample,
    )
    assert "∀ x0 =>" in migrated
    assert '{"x0": "symbolic"}' in migrated
    assert "variables=x0:symbolic" in migrated
    assert 'resolved_path == ["x0", "age"]' in migrated

    unicode_sample = 'source = f"""\n{token} => a <= 1\n"""'
    migrated = migrate_text(
        "test/integration/normalization/nnf/test_ir1_to_nnf_quantifiers.py",
        unicode_sample,
    )
    assert "{token} x0 =>" in migrated

    duplicated_domain = """
[BOUND]:
    forall x0
        forall x0
            with domain(
                x0.a: [0, 3]
            )
    => x0.a <= 3
"""
    migrated_once = migrate_text(
        "test/e2e/backends/test_z3_domain_assumptions.py",
        duplicated_domain,
    )
    migrated_twice = migrate_text(
        "test/e2e/backends/test_z3_domain_assumptions.py",
        migrated_once,
    )
    assert migrated_once == migrated_twice
    assert migrated_once.count("forall x0") == 1

    bare_domain = """
[BOUND]:
    with domain(
        x0.a: [0, 3]
    )
    => x0.a <= 3
"""
    migrated_once = migrate_text(
        "test/e2e/backends/test_z3_domain_assumptions.py",
        bare_domain,
    )
    migrated_twice = migrate_text(
        "test/e2e/backends/test_z3_domain_assumptions.py",
        migrated_once,
    )
    assert migrated_once == migrated_twice
    assert migrated_once.count("forall x0") == 1

    manual_domain = """from dsl.ir.ir1.nodes import DomainIR\n\ndomain=DomainIR(name="Segment", args={"values": ["A", "B"]})\n"""
    migrated = migrate_text(
        "test/unit/normalization/nnf/test_nnf_quantifier_scope_passthrough.py",
        manual_domain,
    )
    assert "DomainEntryIR(" in migrated
    assert "FiniteSetDomainIR(" in migrated
    assert 'SymbolLiteralIR("A")' in migrated

    same_indent_duplicate = """
[BOUND]:
    forall x0
    forall x0
        with domain(
            x0.a: [0, 3]
        )
    => x0.a <= 3
"""
    migrated_once = migrate_text(
        "test/e2e/backends/test_z3_domain_assumptions.py",
        same_indent_duplicate,
    )
    migrated_twice = migrate_text(
        "test/e2e/backends/test_z3_domain_assumptions.py",
        migrated_once,
    )
    assert migrated_once == migrated_twice
    assert migrated_once.count("forall x0") == 1

    ir_expectation = 'assert comparison.entity == "_x"'
    migrated = migrate_text(
        "test/unit/ir/test_comparison_ir_schema_types.py",
        ir_expectation,
    )
    assert migrated == 'assert comparison.entity == "x0"'

    manual_entity = 'cmp("a", 1, entity="_x")'
    migrated = migrate_text(
        "test/unit/normalization/nnf/test_nnf_quantifier_scope_passthrough.py",
        manual_entity,
    )
    assert migrated == 'cmp("a", 1, entity="x0")'

    print("G2-B.3 migration self-test passed.")


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
