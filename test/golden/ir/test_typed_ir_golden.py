import json
from pathlib import Path

from toetra._compiler.ir.ir1.pretty import pretty_task
from test.fixtures.ir_schema_aware.ir_helpers import serialize_task, translate_source
from test.fixtures.ir_schema_aware.samples import (
    CHECK_AT_INCOME,
    CLASSIFICATION_OBSERVABLES,
)
from test.fixtures.ir_schema_aware.schemas import (
    make_binary_classification_schema,
    make_schema,
)

FIXTURE_DIR = Path("test/fixtures/ir_schema_aware/golden")


def test_check_at_income_typed_ir_matches_golden_json():
    tasks = translate_source(CHECK_AT_INCOME, model_schema=make_schema())

    actual = serialize_task(tasks[0])

    expected = json.loads(
        (FIXTURE_DIR / "check_at_income_typed_ir.json").read_text(encoding="utf-8")
    )

    assert actual == expected


def test_check_at_income_pretty_output_matches_golden_text():
    tasks = translate_source(CHECK_AT_INCOME, model_schema=make_schema())

    actual = pretty_task(tasks[0]).strip()
    expected = (
        (FIXTURE_DIR / "check_at_income_pretty.txt").read_text(encoding="utf-8").strip()
    )

    assert actual == expected


def test_classification_observables_typed_ir_matches_golden_json():
    tasks = translate_source(
        CLASSIFICATION_OBSERVABLES,
        model_schema=make_binary_classification_schema(),
    )
    actual = serialize_task(tasks[0])
    expected = json.loads(
        (FIXTURE_DIR / "classification_observables_typed_ir.json").read_text(
            encoding="utf-8"
        )
    )
    assert actual == expected


def test_classification_observables_pretty_matches_golden_text():
    tasks = translate_source(
        CLASSIFICATION_OBSERVABLES,
        model_schema=make_binary_classification_schema(),
    )
    actual = pretty_task(tasks[0]).strip()
    expected = (
        (FIXTURE_DIR / "classification_observables_pretty.txt")
        .read_text(encoding="utf-8")
        .strip()
    )
    assert actual == expected
