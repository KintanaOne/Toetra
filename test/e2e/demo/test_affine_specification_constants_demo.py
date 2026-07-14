from __future__ import annotations

from demo.affine_specification_constants_z3 import EXPECTED_STATUSES, run_demo
from dsl.backends.results import VerificationStatus
from dsl.semantic.types.enums import EnumDataType


def test_affine_specification_constants_demo_runs_end_to_end() -> None:
    schema, executions = run_demo()

    assert schema.model_type == "LinearRegression"
    assert schema.target == "score"
    assert schema.target_dtype is EnumDataType.FLOAT
    assert schema.metadata["linear"]["coef"] == [2.0]
    assert schema.metadata["linear"]["intercept"] == 1.0

    statuses = tuple(execution.result.status for execution in executions)
    assert statuses == EXPECTED_STATUSES
    assert statuses == (
        VerificationStatus.PROVED,
        VerificationStatus.COUNTEREXAMPLE,
        VerificationStatus.WITNESS,
    )

    counterexample = executions[1].result.model
    witness = executions[2].result.model
    assert counterexample is not None
    assert witness is not None
    assert counterexample["x0.a"] == "3"
    assert counterexample["_model.score"] == "7"
    assert witness["x0.a"] == "2"
    assert witness["_model.score"] == "5"


def test_affine_demo_exposes_backend_neutral_reports() -> None:
    _, executions = run_demo()

    proved, counterexample, witness = (execution.report for execution in executions)

    assert proved.status is VerificationStatus.PROVED
    assert proved.assignments == ()
    assert proved.specification == "_model.score <= 7.0"

    assert counterexample.status is VerificationStatus.COUNTEREXAMPLE
    assert [item.display_name for item in counterexample.inputs] == ["x0.a"]
    assert [item.display_name for item in counterexample.outputs] == ["score"]
    assert counterexample.inputs[0].value == "3"
    assert counterexample.outputs[0].value == "7"

    assert witness.status is VerificationStatus.WITNESS
    assert witness.inputs[0].value == "2"
    assert witness.outputs[0].value == "5"
