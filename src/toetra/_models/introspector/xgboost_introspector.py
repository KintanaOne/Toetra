from dataclasses import replace
from importlib.metadata import PackageNotFoundError, version

from toetra._models.detector.model_framework import EnumModelFramework

from toetra._models.introspector.base_introspector import BaseIntrospector
from toetra._models.introspector.sklearn_introspector import (
    SklearnIntrospector,
)

from toetra._models.schema.model_schema import ModelSchema


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
        xgboost_version = self._xgboost_version()
        if sklearn_schema.compatibility is not None:
            sklearn_schema.compatibility = replace(
                sklearn_schema.compatibility,
                framework_adapter_id=EnumModelFramework.XGBOOST.value,
                framework_version=xgboost_version,
                model_family="tree_ensemble",
            )

        # --------------------------------------------------
        # Inject XGBoost-specific metadata
        # --------------------------------------------------

        sklearn_schema.metadata.update(
            {
                "framework_version": xgboost_version,
                "xgboost": self._extract_xgb_metadata(),
            }
        )

        return sklearn_schema

    # ======================================================
    # XGBoost metadata
    # ======================================================

    @staticmethod
    def _xgboost_version() -> str | None:
        try:
            return version("xgboost")
        except PackageNotFoundError:
            return None

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
