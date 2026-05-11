import json

from model.errors.loading import ModelLoadError
from model.loader.base_loader import BaseModelLoader


class JsonModelLoader(BaseModelLoader):
    
    def load(self):
        """Load the model from a JSON file."""
        
        try:

            with open(self.path, 'r') as f:
                model_data = json.load(f)
            return model_data

        except Exception as e:

            raise ModelLoadError(
                f"Failed to load JSON model "
                f"'{self.path}': {e}"
            ) from e