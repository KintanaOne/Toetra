
from model.loader.base_loader import BaseModelLoader


class JsonModelLoader(BaseModelLoader):
    def __init__(self, path: str) -> None:
        """Loader for JSON models."""
        super().__init__(path)
        self.path = path

    def load(self):
        """Load the model from a JSON file."""
        import json
        with open(self.path, 'r') as f:
            model_data = json.load(f)
        return model_data