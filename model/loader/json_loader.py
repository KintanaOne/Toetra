import json

from model.errors.loading import (
    ModelDeserializationError,
    ModelFileNotFoundError,
)
from model.loader.base_loader import BaseModelLoader


class JsonModelLoader(BaseModelLoader):
    """
    Load a JSON artifact.

    Note:
        This loader only deserializes JSON.
        It does not imply that the loaded object is a supported ML model.
    """

    def load(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)

        except FileNotFoundError as e:
            raise ModelFileNotFoundError(str(self.path)) from e

        except json.JSONDecodeError as e:
            raise ModelDeserializationError(
                f"Failed to decode JSON model artifact: {self.path}"
            ) from e

        except OSError as e:
            raise ModelDeserializationError(
                f"Failed to read JSON model artifact: {self.path}"
            ) from e
