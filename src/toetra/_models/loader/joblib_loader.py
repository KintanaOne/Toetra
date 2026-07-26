import joblib

from toetra._models.errors.loading import (
    ModelDeserializationError,
    ModelFileNotFoundError,
)
from toetra._models.loader.base_loader import BaseModelLoader


class JoblibModelLoader(BaseModelLoader):

    def load(self):
        """Load the model using joblib."""

        try:

            return joblib.load(self.path)

        except FileNotFoundError as e:
            raise ModelFileNotFoundError(str(self.path)) from e

        except Exception as e:
            raise ModelDeserializationError(
                f"Failed to deserialize joblib model: {self.path}"
            ) from e
