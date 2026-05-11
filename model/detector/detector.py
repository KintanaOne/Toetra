from model.detector.model_framework import (
    EnumModelFramework,
)

from model.errors.detection import (
    UnsupportedModelError,
)

# ==================================================
# Optional dependencies
# ==================================================

try:
    from xgboost import XGBModel
except ImportError:
    XGBModel = None

try:
    from sklearn.base import BaseEstimator
except ImportError:
    BaseEstimator = None


class ModelDetector:
    """
    Detect the framework associated with a loaded model.
    """

    def detect(self, model):
        """
        Detect the model framework.

        Returns:
            EnumModelFramework

        Raises:
            UnsupportedModelError
        """

        # -----------------------------------------
        # XGBoost
        # -----------------------------------------

        if (
            XGBModel is not None
            and isinstance(model, XGBModel)
        ):
            return EnumModelFramework.XGBOOST

        # -----------------------------------------
        # Scikit-learn
        # -----------------------------------------

        if (
            BaseEstimator is not None
            and isinstance(model, BaseEstimator)
        ):
            return EnumModelFramework.SKLEARN

        # -----------------------------------------
        # Unsupported
        # -----------------------------------------

        raise UnsupportedModelError(
            f"Unsupported model type: {type(model)}"
        )