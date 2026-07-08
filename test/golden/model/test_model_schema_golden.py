from model.runtime.manager import ModelManager
from test.fixtures.model_bridge.factories import (
    dataset_path,
    load_golden,
    make_classification_joblib,
    make_regression_pkl,
    schema_to_contract,
)


def test_sklearn_classification_schema_matches_golden_contract(tmp_path):
    model_path = make_classification_joblib(tmp_path)

    schema = ModelManager(
        model_path=model_path,
        dataset_path=dataset_path("classification.csv"),
        target_name="MyTarget",
    ).build_schema()

    assert schema_to_contract(schema) == load_golden(
        "sklearn_classification_schema.json"
    )


def test_sklearn_regression_schema_matches_golden_contract(tmp_path):
    model_path = make_regression_pkl(tmp_path)

    schema = ModelManager(
        model_path=model_path,
        dataset_path=dataset_path("regression.csv"),
        target_name="SalePrice",
    ).build_schema()

    assert schema_to_contract(schema) == load_golden("sklearn_regression_schema.json")
