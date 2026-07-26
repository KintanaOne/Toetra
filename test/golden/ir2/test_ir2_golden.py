from pathlib import Path

import pytest

from toetra._compiler.ir.ir2.pretty import pretty_ir2_task
from toetra._compiler.ir.ir2.run_ir2 import run_ir2

CASES_DIR = Path(__file__).parent / "cases"
EXPECTED_DIR = Path(__file__).parent / "expected"


@pytest.mark.parametrize(
    "case_name",
    [
        "forall_implication",
        "check_at_demorgan",
    ],
)
def test_ir2_pretty_output_matches_golden(case_name: str):
    source = (CASES_DIR / f"{case_name}.toetra").read_text(encoding="utf-8")
    expected = (EXPECTED_DIR / f"{case_name}.ir2.txt").read_text(encoding="utf-8")

    tasks = run_ir2(source)

    assert len(tasks) == 1
    assert pretty_ir2_task(tasks[0]) + "\n" == expected
