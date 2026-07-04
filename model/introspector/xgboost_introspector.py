from model.detector.model_framework import EnumModelFramework

from model.introspector.base_introspector import BaseIntrospector
from model.introspector.sklearn_introspector import (
    SklearnIntrospector,
)

from model.schema.model_schema import ModelSchema


class XGBoostIntrospector(BaseIntrospector):
    """
    XGBoost introspector.

    XGBoost models expose a sklearn-compatible API,
    so we reuse the sklearn introspection layer and
    enrich it with XGBoost-specific metadata.
    """

    def introspect(self) -> ModelSchema:

        # --------------------------------------------------
        # Reuse sklearn introspection
        # --------------------------------------------------

        sklearn_schema = SklearnIntrospector(
            model=self.model,
            source_path=self.source_path,
            schema=self.input_schema,
            serialization_format=self.serialization_format,
            target_name=self.target_name,
        ).introspect()

        # --------------------------------------------------
        # Override framework
        # --------------------------------------------------

        sklearn_schema.framework = EnumModelFramework.XGBOOST

        # --------------------------------------------------
        # Inject XGBoost-specific metadata
        # --------------------------------------------------

        sklearn_schema.metadata.update({"xgboost": self._extract_xgb_metadata()})

        return sklearn_schema

    # ======================================================
    # XGBoost metadata
    # ======================================================

    def _extract_xgb_metadata(self) -> dict:
        """
        Extract XGBoost-specific metadata.
        """

        metadata = {}

        metadata["n_estimators"] = self._safe_getattr("n_estimators")

        metadata["max_depth"] = self._safe_getattr("max_depth")

        metadata["objective"] = self._safe_getattr("objective")

        metadata["booster"] = self._safe_getattr("booster")

        return metadata
