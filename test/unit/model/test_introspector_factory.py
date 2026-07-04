import pytest

from model.detector.model_framework import EnumModelFramework
from model.errors.introspection import UnsupportedIntrospectorError
from model.introspector.introspector_factory import IntrospectorFactory
from model.introspector.sklearn_introspector import SklearnIntrospector
from test.fixtures.model_bridge.factories import dataset_path, train_classification_model


def test_introspector_factory_creates_sklearn_introspector_with_target_name():
    model = train_classification_model()

    introspector = IntrospectorFactory.create(
        framework=EnumModelFramework.SKLEARN,
        model=model,
        dataset_path=dataset_path("classification.csv"),
        target_name="MyTarget",
        serialization_format=".joblib",
    )

    assert isinstance(introspector, SklearnIntrospector)
    assert introspector.target_name == "MyTarget"


def test_introspector_factory_rejects_unsupported_framework():
    class UnknownFramework:
        pass

    with pytest.raises(UnsupportedIntrospectorError):
        IntrospectorFactory.create(
            framework=UnknownFramework(),
            model=object(),
            dataset_path=None,
        )
