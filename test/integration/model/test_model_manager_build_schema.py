from model.detector.model_framework import EnumModelFramework
from model.runtime.manager import ModelManager
from test.fixtures.model_bridge.factories import (
    dataset_path,
    make_classification_joblib,
    make_regression_pkl,
)


def test_model_manager_builds_schema_for_joblib_sklearn_classifier(tmp_path):
    model_path = make_classification_joblib(tmp_path)

    schema = ModelManager(
        model_path=model_path,
        dataset_path=dataset_path("classification.csv"),
        target_name="MyTarget",
    ).build_schema()

    assert schema.framework is EnumModelFramework.SKLEARN
    assert schema.model_type == "LogisticRegression"
    assert schema.task == "classification"
    assert schema.target == "MyTarget"
    assert set(schema.features) == {"age", "income", "score"}


def test_model_manager_builds_schema_for_pickle_sklearn_regressor(tmp_path):
    model_path = make_regression_pkl(tmp_path)

    schema = ModelManager(
        model_path=model_path,
        dataset_path=dataset_path("regression.csv"),
        target_name="SalePrice",
    ).build_schema()

    assert schema.framework is EnumModelFramework.SKLEARN
    assert schema.model_type == "LinearRegression"
    assert schema.task == "regression"
    assert schema.target == "SalePrice"
    assert set(schema.features) == {"size", "rooms", "distance"}
