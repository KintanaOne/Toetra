import json
from toetra._compiler.ir.ir1.pretty import pretty_task
from tests.support.ir_serialization import serialize_task, translate_source
from tests.support.paths import GOLDEN_ROOT
from tests.fixtures.ir_schema_aware.samples import (
    CHECK_AT_INCOME,
    CLASSIFICATION_OBSERVABLES,
)
from tests.support.schemas import (
    make_binary_classification_schema,
    make_schema,
)

GOLDEN_DIR = GOLDEN_ROOT / "ir" / "schema_aware"


def test_check_at_income_typed_ir_matches_golden_json():
    tasks = translate_source(CHECK_AT_INCOME, model_schema=make_schema())

    actual = serialize_task(tasks[0])

    expected = json.loads(
        (GOLDEN_DIR / "check_at_income_typed_ir.json").read_text(encoding="utf-8")
    )

    assert actual == expected


def test_check_at_income_pretty_output_matches_golden_text():
    tasks = translate_source(CHECK_AT_INCOME, model_schema=make_schema())

    actual = pretty_task(tasks[0]).strip()
    expected = (
        (GOLDEN_DIR / "check_at_income_pretty.txt").read_text(encoding="utf-8").strip()
    )

    assert actual == expected


def test_classification_observables_typed_ir_matches_golden_json():
    tasks = translate_source(
        CLASSIFICATION_OBSERVABLES,
        model_schema=make_binary_classification_schema(),
    )
    actual = serialize_task(tasks[0])
    expected = json.loads(
        (GOLDEN_DIR / "classification_observables_typed_ir.json").read_text(
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
        (GOLDEN_DIR / "classification_observables_pretty.txt")
        .read_text(encoding="utf-8")
        .strip()
    )
    assert actual == expected
