from pathlib import Path

import pytest

from model.errors.loading import UnsupportedModelFormatError
from model.loader.joblib_loader import JoblibModelLoader
from model.loader.json_loader import JsonModelLoader
from model.loader.loader_factory import LoaderFactory
from model.loader.pkl_loader import PklModelLoader


def test_loader_factory_selects_joblib_loader():
    loader = LoaderFactory.get_loader(Path("model.joblib"))

    assert isinstance(loader, JoblibModelLoader)


def test_loader_factory_selects_pickle_loader():
    loader = LoaderFactory.get_loader(Path("model.pkl"))

    assert isinstance(loader, PklModelLoader)


def test_loader_factory_selects_json_loader():
    loader = LoaderFactory.get_loader(Path("model.json"))

    assert isinstance(loader, JsonModelLoader)


def test_loader_factory_rejects_unsupported_extension():
    with pytest.raises(UnsupportedModelFormatError):
        LoaderFactory.get_loader(Path("model.onnx"))
