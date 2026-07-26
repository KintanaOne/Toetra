from __future__ import annotations

import pytest

from tests.support.paths import FIXTURES_ROOT, GOLDEN_ROOT

from tests.support.normalization import (
    assert_is_nnf,
    import_run_nnf,
    tasks_to_golden,
)

CASES_DIR = FIXTURES_ROOT / "normalization" / "nnf"
EXPECTED_DIR = GOLDEN_ROOT / "normalization" / "nnf"


@pytest.mark.parametrize(
    "case_name",
    [
        "implication",
        "demorgan_and",
        "demorgan_or",
        "negated_implication",
        "nested",
        "forall_demorgan",
        "exists_implication",
        "forall_domain_demorgan_or",
        "problem_predicate_implication",
    ],
)
def test_nnf_golden_outputs(case_name: str):
    source = (CASES_DIR / f"{case_name}.toetra").read_text(encoding="utf-8")
    expected = (EXPECTED_DIR / f"{case_name}.nnf.txt").read_text(encoding="utf-8")

    run_nnf = import_run_nnf()
    tasks = run_nnf(source)
    actual = tasks_to_golden(tasks)

    for task in tasks:
        assert_is_nnf(task.query.expression)

    assert actual == expected
