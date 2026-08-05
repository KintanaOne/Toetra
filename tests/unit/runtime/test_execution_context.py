from __future__ import annotations

from pathlib import Path

import pytest

from toetra._compiler.builder.program import parse_program
from toetra._compiler.parser.parser import parse_toetra_code
from toetra._runtime.errors import VerificationConfigurationError
from toetra._runtime.execution_context import resolve_execution_context

_SOURCE = """
model := "models/base.joblib"
target := score
dataset := "data/base.csv"

[BOUND]:
forall x0 => target[x0] <= 7 using Z3
"""


def _program():
    return parse_program(parse_toetra_code(_SOURCE))


def test_execution_context_preserves_declared_defaults_without_overrides() -> None:
    program = _program()

    context = resolve_execution_context(
        declared_model_reference=program.header.model,
        declared_target=program.header.target,
        declared_dataset_reference=program.header.dataset,
        model=None,
        target=None,
        dataset=None,
    )

    assert context.to_dict() == {
        "declared": {
            "model": "models/base.joblib",
            "target": "score",
            "dataset": "data/base.csv",
        },
        "effective": {
            "model": "models/base.joblib",
            "target": "score",
            "dataset": "data/base.csv",
        },
        "overrides": {
            "model": False,
            "target": False,
            "dataset": False,
        },
    }


def test_execution_context_rebinds_header_without_mutating_declared_ast() -> None:
    program = _program()
    context = resolve_execution_context(
        declared_model_reference=program.header.model,
        declared_target=program.header.target,
        declared_dataset_reference=program.header.dataset,
        model="candidate.joblib",
        target="risk_score",
        dataset="candidate.csv",
    )

    effective = context.apply_to(program)

    assert program.header.model == "models/base.joblib"
    assert program.header.target == "score"
    assert program.header.dataset == "data/base.csv"
    assert effective.header.model == "candidate.joblib"
    assert effective.header.target == "risk_score"
    assert effective.header.dataset == "candidate.csv"
    assert context.model_overridden is True
    assert context.target_overridden is True
    assert context.dataset_overridden is True


@pytest.mark.parametrize("target", ["", " target", "target", "risk-score", "1score"])
def test_execution_context_rejects_invalid_target_overrides(target: str) -> None:
    with pytest.raises(VerificationConfigurationError) as caught:
        resolve_execution_context(
            declared_model_reference="model.joblib",
            declared_target="score",
            declared_dataset_reference=None,
            model=None,
            target=target,
            dataset=None,
        )

    assert caught.value.code == "TARGET_OVERRIDE_INVALID"


def test_execution_context_rebinds_model_and_target_through_ir1() -> None:
    from toetra._compiler.ir.ir1.nodes import ComparisonIR, TargetExpressionIR
    from toetra._compiler.ir.ir1.run_ir1 import run_ir_from_program
    from tests.support.semantic_restrictions import numeric_schema

    program = _program()
    context = resolve_execution_context(
        declared_model_reference=program.header.model,
        declared_target=program.header.target,
        declared_dataset_reference=program.header.dataset,
        model="candidate.joblib",
        target="risk_score",
        dataset="candidate.csv",
    )
    schema = numeric_schema()
    schema.output_name = "risk_score"

    expression = run_ir_from_program(
        context.apply_to(program),
        model_schema=schema,
    )[0].query.expression

    assert isinstance(expression, ComparisonIR)
    assert isinstance(expression.left, TargetExpressionIR)
    assert expression.left.feature == "risk_score"
    assert expression.left.model_identity == "candidate.joblib"
    assert program.header.model == "models/base.joblib"
    assert program.header.target == "score"
    assert program.header.dataset == "data/base.csv"


def test_schema_only_resolution_rebinds_target_without_mutating_schema() -> None:
    from toetra._runtime.api import _load_specification, _resolve_model
    from tests.support.semantic_restrictions import numeric_schema

    loaded = _load_specification(_SOURCE.replace('dataset := "data/base.csv"\n', ""))
    schema = numeric_schema()

    resolved = _resolve_model(
        loaded,
        model=None,
        dataset=None,
        target="risk_score",
        schema=schema,
    )

    assert schema.output_name == "score"
    assert resolved.schema.output_name == "risk_score"
    assert resolved.program.header.target == "risk_score"
    assert resolved.execution_context.target_overridden is True


def test_pre_resolved_context_must_match_declared_header() -> None:
    from toetra._runtime.api import _load_specification, _resolve_model
    from tests.support.semantic_restrictions import numeric_schema

    loaded = _load_specification(_SOURCE.replace('dataset := "data/base.csv"\n', ""))
    context = resolve_execution_context(
        declared_model_reference="another.joblib",
        declared_target="score",
        declared_dataset_reference=None,
        model=None,
        target=None,
        dataset=None,
    )

    with pytest.raises(VerificationConfigurationError) as caught:
        _resolve_model(
            loaded,
            model=None,
            dataset=None,
            target=None,
            schema=numeric_schema(),
            execution_context=context,
        )

    assert caught.value.code == "EXECUTION_CONTEXT_DECLARATION_MISMATCH"


def test_artifact_overrides_rebuild_the_effective_schema(
    tmp_path: Path,
) -> None:
    import joblib
    import pandas as pd
    from sklearn.linear_model import LinearRegression

    from toetra._runtime.api import _load_specification, _resolve_model

    frame = pd.DataFrame(
        {
            "a": [0.0, 1.0, 2.0, 3.0],
            "score": [1.0, 3.0, 5.0, 7.0],
            "risk_score": [1.0, 3.0, 5.0, 7.0],
        }
    )
    model = LinearRegression().fit(frame[["a"]], frame["score"])
    model_path = tmp_path / "candidate.joblib"
    dataset_path = tmp_path / "candidate.csv"
    joblib.dump(model, model_path)
    frame.to_csv(dataset_path, index=False)

    loaded = _load_specification(_SOURCE)
    resolved = _resolve_model(
        loaded,
        model=model_path,
        dataset=dataset_path,
        target="risk_score",
        schema=None,
    )

    assert resolved.model_path == model_path.resolve()
    assert resolved.dataset_path == dataset_path.resolve()
    assert resolved.schema.output_name == "risk_score"
    assert resolved.execution_context.model_overridden is True
    assert resolved.execution_context.target_overridden is True
    assert resolved.execution_context.dataset_overridden is True
    assert resolved.program.header.model == str(model_path)
    assert resolved.program.header.target == "risk_score"
    assert resolved.program.header.dataset == str(dataset_path)
    assert loaded.program.header.model == "models/base.joblib"
    assert loaded.program.header.target == "score"
    assert loaded.program.header.dataset == "data/base.csv"
