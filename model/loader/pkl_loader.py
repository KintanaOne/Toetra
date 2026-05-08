
from model.loader.base_loader import BaseModelLoader


class PklModelLoader(BaseModelLoader):
    def __init__(self, path: str) -> None:
        """Loader for models saved in .pkl format."""
        super().__init__(path)
        self.path = path

    def load(self):
        """Load the model from a .pkl file."""
        import pickle
        with open(self.path, 'rb') as f:
            model = pickle.load(f)
        return model