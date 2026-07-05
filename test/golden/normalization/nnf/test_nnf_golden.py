from __future__ import annotations

from pathlib import Path

import pytest

from test.fixtures.normalization.nnf.helpers import assert_is_nnf, import_run_nnf, tasks_to_golden


CASES_DIR = Path(__file__).parent / "cases"
EXPECTED_DIR = Path(__file__).parent / "expected"


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
    source = (CASES_DIR / f"{case_name}.forml").read_text(encoding="utf-8")
    expected = (EXPECTED_DIR / f"{case_name}.nnf.txt").read_text(encoding="utf-8")

    run_nnf = import_run_nnf()
    tasks = run_nnf(source)
    actual = tasks_to_golden(tasks)

    for task in tasks:
        assert_is_nnf(task.query.expression)

    assert actual == expected
