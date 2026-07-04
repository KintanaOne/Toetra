import pandas as pd

from sklearn.base import (
    ClassifierMixin,
    RegressorMixin,
)

from dsl.semantic.types.enums import EnumDataType

from model.detector.model_framework import EnumModelFramework
from model.introspector.base_introspector import BaseIntrospector
from model.schema.feature_schema import FeatureSchema
from model.schema.model_schema import ModelSchema

from model.errors.introspection import MissingFeatureMetadataError

class SklearnIntrospector(BaseIntrospector):

    # ======================================================
    # Public API
    # ======================================================

    def introspect(self) -> ModelSchema:
        """
        Build a normalized schema representation
        from a scikit-learn model.
        """

        features = (
            self.input_schema.features
            if self.input_schema is not None
            else self._detect_features()
        )

        return ModelSchema(
            framework=EnumModelFramework.SKLEARN,
            model_type=type(self.model).__name__,
            features=features,
            task=self._detect_task(),
            target=self._detect_target(),
            metadata=self._build_metadata(),
        )

    # ======================================================
    # Feature detection
    # ======================================================

    def _detect_features(self) -> dict[str, FeatureSchema]:
        """
        Infer feature schema from the dataset.

        The target column is excluded from features when known.
        """

        if self.source_path is None:
            raise MissingFeatureMetadataError(
                "Feature detection requires a dataset source path "
                "or an explicit input schema."
            )

        data = pd.read_csv(self.source_path)

        target = self._detect_target()

        features: dict[str, FeatureSchema] = {}

        for column, dtype in data.dtypes.items():
            column_name = str(column)

            if column_name == target:
                continue

            enum_dtype = self._map_dtype(dtype)

            features[column_name] = FeatureSchema(
                name=column_name,
                dtype=enum_dtype,
                nullable=bool(data[column].isnull().any()),
            )

        return features

    # ======================================================
    # Pandas → FORML type mapping
    # ======================================================

    def _map_dtype(self, dtype) -> EnumDataType:
        """
        Map pandas dtypes to FORML semantic types.
        """

        dtype_str = str(dtype)

        if "int" in dtype_str:
            return EnumDataType.INT

        if "float" in dtype_str:
            return EnumDataType.FLOAT

        if "bool" in dtype_str:
            return EnumDataType.BOOL

        return EnumDataType.STRING

    # ======================================================
    # Task detection
    # ======================================================

    def _detect_task(self) -> str:
        """
        Detect ML task type.
        """

        if isinstance(self.model, ClassifierMixin):
            return "classification"

        if isinstance(self.model, RegressorMixin):
            return "regression"

        return "unknown"

    # ======================================================
    # Target detection
    # ======================================================

    def _detect_target(self) -> str:
        """
        Detect prediction target.

        Priority:
            1. external schema target
            2. explicit FORML target_name
            3. conventional default: "target"
        """

        if self.input_schema is not None and self.input_schema.target is not None:
            return self.input_schema.target

        if self.target_name is not None:
            return self.target_name

        return "target"

    # ======================================================
    # Metadata extraction
    # ======================================================

    def _build_metadata(self) -> dict:
        """
        Extract sklearn-specific metadata.
        """

        metadata = self._build_base_metadata()

        metadata.update(
            {
                "n_features_in": self._safe_getattr("n_features_in_"),
                "classes": self._safe_getattr("classes_"),
                "feature_names_in": self._safe_getattr("feature_names_in_"),
            }
        )

        return metadata
