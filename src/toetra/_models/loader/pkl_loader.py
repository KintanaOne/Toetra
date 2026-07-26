import pickle

from toetra._models.errors.loading import (
    ModelDeserializationError,
    ModelFileNotFoundError,
)
from toetra._models.loader.base_loader import BaseModelLoader


class PklModelLoader(BaseModelLoader):

    def load(self):

        try:
            with open(self.path, "rb") as f:
                return pickle.load(f)

        except FileNotFoundError as e:
            raise ModelFileNotFoundError(str(self.path)) from e

        except Exception as e:
            raise ModelDeserializationError(
                f"Failed to deserialize pickle model: {self.path}"
            ) from e
