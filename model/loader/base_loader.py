
from pathlib import Path


class BaseModelLoader:
    def __init__(self, path: str | Path) -> None:
        """Base class for model loaders."""
        self.path = Path(path)
        

    def load(self):
        """Load the model."""
        raise NotImplementedError("Subclasses must implement this method.")