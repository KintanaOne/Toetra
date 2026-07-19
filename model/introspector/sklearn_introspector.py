from typing import Any

import pandas as pd

from sklearn import __version__ as sklearn_version
from sklearn.base import (
    ClassifierMixin,
    RegressorMixin,
)

from dsl.compatibility.descriptors import (
    FrameworkModelDescriptor,
    NumericSemanticDescriptor,
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

        target = self._detect_target()
        features = (
            self.input_schema.features
            if self.input_schema is not None
            else self._detect_features()
        )

        task = self._detect_task()
        metadata = self._build_metadata()
        target_source_dtype = self._detect_target_source_dtype(target)
        return ModelSchema(
            framework=EnumModelFramework.SKLEARN,
            model_type=type(self.model).__name__,
            features=features,
            task=task,
            target=target,
            target_dtype=self._detect_target_dtype(target),
            metadata=metadata,
            compatibility=self._compatibility_descriptor(
                features=features,
                task=task,
                metadata=metadata,
                target_source_dtype=target_source_dtype,
            ),
            target_source_dtype=target_source_dtype,
        )

    # ======================================================
    # Feature detection
    # ======================================================

    def _detect_features(self) -> dict[str, FeatureSchema]:
        """Infer the model input schema from model metadata and the dataset.

        When sklearn exposes ``feature_names_in_``, those names are the source
        of truth for model inputs. The dataset may then contain additional
        lookup or provenance columns (for example an anchor identifier), which
        must not leak into ``ModelSchema.features``. Models without named-input
        metadata retain the historical fallback of using every non-target
        dataset column.
        """

        if self.source_path is None:
            raise MissingFeatureMetadataError(
                "Feature detection requires a dataset source path "
                "or an explicit input schema."
            )

        data = pd.read_csv(self.source_path)
        feature_names = self._model_feature_names()
        if feature_names is None:
            target = self._detect_target()
            feature_names = tuple(
                str(column) for column in data.columns if str(column) != target
            )

        missing = [name for name in feature_names if name not in data.columns]
        if missing:
            raise MissingFeatureMetadataError(
                "Reference dataset is missing model-declared feature(s): "
                + ", ".join(missing)
            )

        return {
            name: FeatureSchema(
                name=name,
                dtype=self._map_dtype(data[name].dtype),
                nullable=bool(data[name].isnull().any()),
                source_dtype=str(data[name].dtype),
            )
            for name in feature_names
        }

    def _model_feature_names(self) -> tuple[str, ...] | None:
        """Return sklearn's ordered named-input contract when available."""

        raw_names = self._safe_getattr("feature_names_in_")
        if raw_names is None:
            return None

        normalized = self._to_python(raw_names)
        if not isinstance(normalized, list):
            normalized = list(normalized)
        return tuple(str(name) for name in normalized)

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

    def _detect_target_dtype(self, target: str) -> EnumDataType | None:
        """Infer the target dtype without guessing when metadata is absent."""

        if self.input_schema is not None and self.input_schema.target_dtype is not None:
            return self.input_schema.target_dtype

        if self.source_path is None:
            return None

        data = pd.read_csv(self.source_path)
        if target not in data.columns:
            return None

        return self._map_dtype(data[target].dtype)

    # ======================================================
    # Metadata extraction
    # ======================================================

    def _build_metadata(self) -> dict:
        """
        Extract sklearn-specific metadata.
        """

        metadata = self._build_base_metadata()

        feature_names_in = self._safe_getattr("feature_names_in_")

        metadata.update(
            {
                "framework_version": sklearn_version,
                "n_features_in": self._safe_getattr("n_features_in_"),
                "classes": self._safe_getattr("classes_"),
                "feature_names_in": feature_names_in,
            }
        )

        linear_metadata = self._extract_linear_metadata(feature_names_in)

        if linear_metadata is not None:
            metadata["linear"] = linear_metadata

        return metadata

    def _extract_linear_metadata(self, feature_names_in: Any) -> dict[str, Any] | None:
        """Extract generic coef/intercept metadata for linear sklearn estimators."""

        if not self._has_attr("coef_") or not self._has_attr("intercept_"):
            return None

        feature_names = None

        if feature_names_in is not None:
            feature_names = self._to_python(feature_names_in)

        coefficient = self._safe_getattr("coef_")
        intercept = self._safe_getattr("intercept_")
        return {
            "coef": self._to_python(coefficient),
            "intercept": self._to_python(intercept),
            "feature_names": feature_names,
            "coef_source_dtype": self._source_dtype_name(coefficient),
            "intercept_source_dtype": self._source_dtype_name(intercept),
        }

    def _detect_target_source_dtype(self, target: str) -> str | None:
        if self.source_path is None:
            return None

        data = pd.read_csv(self.source_path)
        if target not in data.columns:
            return None
        return str(data[target].dtype)

    def _compatibility_descriptor(
        self,
        *,
        features: dict[str, FeatureSchema],
        task: str,
        metadata: dict[str, Any],
        target_source_dtype: str | None,
    ) -> FrameworkModelDescriptor:
        linear = metadata.get("linear")
        parameter_dtypes: tuple[str, ...] = ()
        if isinstance(linear, dict):
            parameter_dtypes = tuple(
                dict.fromkeys(
                    str(value)
                    for value in (
                        linear.get("coef_source_dtype"),
                        linear.get("intercept_source_dtype"),
                    )
                    if value
                )
            )

        numeric_semantics, profile_id = self._numeric_profile(parameter_dtypes)
        model_type = type(self.model).__name__
        model_family = (
            "affine_regression"
            if model_type == "LinearRegression" and task == "regression"
            else f"unknown:{task}:{model_type}"
        )
        return FrameworkModelDescriptor(
            framework_adapter_id=EnumModelFramework.SKLEARN.value,
            framework_version=sklearn_version,
            model_family=model_family,
            source_execution_profile_id=profile_id,
            numeric_semantics=numeric_semantics,
            parameter_dtypes=parameter_dtypes,
            input_dtypes=tuple(
                feature.source_dtype or feature.dtype.value
                for feature in features.values()
            ),
            output_dtype=target_source_dtype,
        )

    @staticmethod
    def _numeric_profile(
        parameter_dtypes: tuple[str, ...],
    ) -> tuple[NumericSemanticDescriptor, str]:
        normalized = {value.lower() for value in parameter_dtypes}
        if normalized and all("float64" in value for value in normalized):
            return NumericSemanticDescriptor.binary_float(64), "ieee754_binary64"
        if normalized and all("float32" in value for value in normalized):
            return NumericSemanticDescriptor.binary_float(32), "ieee754_binary32"
        if any("float" in value for value in normalized):
            return (
                NumericSemanticDescriptor.binary_float(None),
                "binary_float_unknown_width",
            )
        return NumericSemanticDescriptor.unknown(), "unknown"

    @staticmethod
    def _source_dtype_name(value: Any) -> str | None:
        dtype = getattr(value, "dtype", None)
        if dtype is not None:
            return str(dtype)
        if value is None:
            return None
        return type(value).__name__

    def _to_python(self, value: Any) -> Any:
        """Convert numpy/pandas values to plain Python structures when possible."""

        if hasattr(value, "tolist"):
            return value.tolist()

        return value
