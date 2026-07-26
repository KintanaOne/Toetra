import json

import pytest

from toetra._models.errors.loading import (
    ModelDeserializationError,
    ModelFileNotFoundError,
)
from toetra._models.loader.joblib_loader import JoblibModelLoader
from toetra._models.loader.json_loader import JsonModelLoader
from toetra._models.loader.pkl_loader import PklModelLoader
from test.fixtures.model_bridge.factories import (
    make_classification_joblib,
    make_classification_pkl,
)


def test_joblib_loader_loads_sklearn_model(tmp_path):
    path = make_classification_joblib(tmp_path)

    model = JoblibModelLoader(path).load()

    assert type(model).__name__ == "LogisticRegression"
    assert hasattr(model, "predict")


def test_pickle_loader_loads_sklearn_model(tmp_path):
    path = make_classification_pkl(tmp_path)

    model = PklModelLoader(path).load()

    assert type(model).__name__ == "LogisticRegression"
    assert hasattr(model, "predict")


def test_json_loader_loads_json_artifact(tmp_path):
    path = tmp_path / "artifact.json"
    path.write_text(json.dumps({"kind": "schema", "version": 1}), encoding="utf-8")

    artifact = JsonModelLoader(path).load()

    assert artifact == {"kind": "schema", "version": 1}


def test_json_loader_raises_on_missing_file(tmp_path):
    with pytest.raises(ModelFileNotFoundError):
        JsonModelLoader(tmp_path / "missing.json").load()


def test_json_loader_raises_on_invalid_json(tmp_path):
    path = tmp_path / "invalid.json"
    path.write_text("{invalid json", encoding="utf-8")

    with pytest.raises(ModelDeserializationError):
        JsonModelLoader(path).load()
