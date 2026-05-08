import joblib

from model.loader.base_loader import BaseModelLoader


class JoblibModelLoader(BaseModelLoader):
    def __init__(self, path: str) -> None:
        """Loader for joblib models."""
        super().__init__(path)
        self.path = path

    def load(self):
        """Load the model using joblib."""
        return joblib.load(self.path)