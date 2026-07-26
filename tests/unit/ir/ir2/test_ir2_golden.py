import pytest

from toetra._compiler.ir.ir2.pretty import pretty_ir2_task
from toetra._compiler.ir.ir2.run_ir2 import run_ir2
from tests.support.paths import FIXTURES_ROOT, GOLDEN_ROOT

EXPECTED_DIR = GOLDEN_ROOT / "ir2"


@pytest.mark.parametrize(
    ("fixture_path", "golden_name"),
    [
        ("ir2/forall_implication.toetra", "forall_implication"),
        ("normalization/nnf/demorgan_and.toetra", "check_at_demorgan"),
    ],
)
def test_ir2_pretty_output_matches_golden(fixture_path: str, golden_name: str) -> None:
    source = (FIXTURES_ROOT / fixture_path).read_text(encoding="utf-8")
    expected = (EXPECTED_DIR / f"{golden_name}.ir2.txt").read_text(encoding="utf-8")

    tasks = run_ir2(source)

    assert len(tasks) == 1
    assert pretty_ir2_task(tasks[0]) + "\n" == expected
