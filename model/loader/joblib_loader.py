import joblib

from model.errors.loading import ModelLoadError
from model.loader.base_loader import BaseModelLoader


class JoblibModelLoader(BaseModelLoader):

    def load(self):
        """Load the model using joblib."""

        try:

            return joblib.load(self.path)
        
        except Exception as e:
            
            raise ModelLoadError(
                f"Failed to load joblib model "
                f"'{self.path}': {e}"
            ) from e