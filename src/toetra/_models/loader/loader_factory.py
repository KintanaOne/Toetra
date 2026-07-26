from pathlib import Path
from typing import Type

from toetra._models.loader.base_loader import BaseModelLoader
from toetra._models.loader.joblib_loader import JoblibModelLoader
from toetra._models.loader.pkl_loader import PklModelLoader
from toetra._models.loader.json_loader import JsonModelLoader

from toetra._models.errors.loading import UnsupportedModelFormatError


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
            raise UnsupportedModelFormatError(f"Unsupported model format: {extension}")

        return loader_class(model_path)
