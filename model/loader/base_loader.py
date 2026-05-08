
class BaseModelLoader:
    def __init__(self, path: str) -> None:
        """Base class for model loaders."""
        

    def load(self):
        """Load the model."""
        raise NotImplementedError("Subclasses must implement this method.")