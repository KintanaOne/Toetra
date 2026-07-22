import pytest

from model.runtime.manager import ModelManager


def test_model_manager_uses_output_name_as_source_of_truth() -> None:
    manager = ModelManager("model.joblib", output_name="decision")

    assert manager.output_name == "decision"
    assert manager.target_name == "decision"


def test_model_manager_accepts_legacy_target_name_projection() -> None:
    manager = ModelManager("model.joblib", target_name="score")

    assert manager.output_name == "score"


def test_model_manager_rejects_conflicting_output_names() -> None:
    with pytest.raises(ValueError, match="must match"):
        ModelManager(
            "model.joblib",
            target_name="score",
            output_name="decision",
        )
