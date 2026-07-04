import pytest

from model.detector.detector import ModelDetector
from model.detector.model_framework import EnumModelFramework
from model.errors.detection import UnsupportedModelError
from test.fixtures.model_bridge.factories import train_classification_model


def test_detector_detects_sklearn_estimator():
    model = train_classification_model()

    framework = ModelDetector().detect(model)

    assert framework is EnumModelFramework.SKLEARN


def test_detector_rejects_plain_dict():
    with pytest.raises(UnsupportedModelError):
        ModelDetector().detect({"not": "a model"})
