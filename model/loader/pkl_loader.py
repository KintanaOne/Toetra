import pickle

from model.errors.loading import ModelLoadError
from model.loader.base_loader import BaseModelLoader


class PklModelLoader(BaseModelLoader):

    def load(self):
        """Load the model using pickle."""
        try:

            with open(self.path, "rb") as f:
                return pickle.load(f)

        except Exception as e:

            raise ModelLoadError(
                f"Failed to load pickle model "
                f"'{self.path}': {e}"
            ) from e