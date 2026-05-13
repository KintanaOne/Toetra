from pathlib import Path
from typing import Type

from model.loader.base_loader import BaseModelLoader
from model.loader.joblib_loader import JoblibModelLoader
from model.loader.pkl_loader import PklModelLoader
from model.loader.json_loader import JsonModelLoader

from model.errors.loading import UnsupportedModelFormatError


class LoaderFactory:

    LOADERS: dict[str, Type[BaseModelLoader]] = {
        ".pkl": PklModelLoader,
        ".joblib": JoblibModelLoader,
        ".json": JsonModelLoader,
    }

    @classmethod
    def get_loader(cls, path: str | Path) -> BaseModelLoader:

        model_path = Path(path)

        extension: str = model_path.suffix.lower()

        loader_class = cls.LOADERS.get(extension)

        if loader_class is None:
            raise UnsupportedModelFormatError(
                f"Unsupported model format: {extension}"
            )

        return loader_class(model_path)