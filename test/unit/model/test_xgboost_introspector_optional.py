import pytest

xgboost = pytest.importorskip("xgboost")

from toetra._models.detector.model_framework import EnumModelFramework
from toetra._models.introspector.xgboost_introspector import XGBoostIntrospector
from test.fixtures.model_bridge.factories import dataset_path


def test_xgboost_introspector_reuses_sklearn_contract_and_preserves_target():
    import pandas as pd

    data = pd.read_csv(dataset_path("classification.csv"))
    x = data.drop(columns=["MyTarget"])
    y = data["MyTarget"]

    model = xgboost.XGBClassifier(
        n_estimators=2,
        max_depth=1,
        eval_metric="logloss",
        random_state=0,
    )
    model.fit(x, y)

    schema = XGBoostIntrospector(
        model=model,
        source_path=dataset_path("classification.csv"),
        target_name="MyTarget",
        serialization_format=".joblib",
    ).introspect()

    assert schema.framework is EnumModelFramework.XGBOOST
    assert schema.target == "MyTarget"
    assert "MyTarget" not in schema.features
    assert "xgboost" in schema.metadata
