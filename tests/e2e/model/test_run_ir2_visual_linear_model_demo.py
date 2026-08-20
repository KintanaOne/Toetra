import pytest

pytest.importorskip("pandas")
pytest.importorskip("sklearn.linear_model")

from toetra._compiler.ir.ir2.demos.linear_model_demo import (  # noqa: E402
    build_demo_linear_regression_schema,
    print_demo_linear_regression_ir2,
    run_ir2_with_demo_linear_regression_model,
)
from toetra._compiler.ir.ir2.pretty import pretty_ir2_task  # noqa: E402


def test_demo_linear_regression_schema_is_introspected_from_real_model():
    schema = build_demo_linear_regression_schema()

    assert schema.model_type == "LinearRegression"
    assert schema.task == "regression"
    assert schema.target == "MyTarget"
    assert set(schema.feature_names) == {"a", "b"}
    assert "linear" in schema.metadata_by_name
    assert schema.metadata_by_name["linear"]["coef"] is not None
    assert schema.metadata_by_name["linear"]["intercept"] is not None
    assert schema.metadata_by_name["linear"]["feature_names"] == ("a", "b")


def test_visual_demo_pretty_output_contains_model_assumption():
    tasks = run_ir2_with_demo_linear_regression_model()

    assert len(tasks) == 1
    task = tasks[0]
    rendered = pretty_ir2_task(task)

    assert "Assumptions   : 1" in rendered
    assert "model_assertions" in rendered
    assert "Γ[0] source=model" in rendered
    assert "_model.MyTarget" in rendered
    assert "x0.a" in rendered
    assert "x0.b" in rendered
    assert "Verification condition:" in rendered


def test_visual_demo_prints_explainable_gamma_and_vc(capsys):
    print_demo_linear_regression_ir2()

    out = capsys.readouterr().out

    assert "=== IR2 REAL MODEL DEMO ===" in out
    assert "Trained model    : sklearn.LinearRegression" in out
    assert "=== IR2 PRETTY WITH MODEL Γ ===" in out
    assert "=== IR2 EXPLAIN WITH MODEL Γ ===" in out
    assert "Assumptions   : 1" in out
    assert "🧱 Assumptions Γ" in out
    assert "VC = Γ ∧ ¬P" in out
    assert "_model.MyTarget" in out
