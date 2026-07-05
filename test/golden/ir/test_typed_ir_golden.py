import json
from pathlib import Path

from dsl.ir.ir1.pretty import pretty_task
from test.fixtures.ir_schema_aware.ir_helpers import serialize_task, translate_source
from test.fixtures.ir_schema_aware.samples import CHECK_AT_INCOME
from test.fixtures.ir_schema_aware.schemas import make_schema


FIXTURE_DIR = Path("test/fixtures/ir_schema_aware/golden")


def test_check_at_income_typed_ir_matches_golden_json():
    tasks = translate_source(CHECK_AT_INCOME, model_schema=make_schema())

    actual = serialize_task(tasks[0])

    expected = json.loads(
        (FIXTURE_DIR / "check_at_income_typed_ir.json").read_text(
            encoding="utf-8"
        )
    )

    assert actual == expected


def test_check_at_income_pretty_output_matches_golden_text():
    tasks = translate_source(CHECK_AT_INCOME, model_schema=make_schema())

    actual = pretty_task(tasks[0]).strip()
    expected = (
        FIXTURE_DIR / "check_at_income_pretty.txt"
    ).read_text(encoding="utf-8").strip()

    assert actual == expected
