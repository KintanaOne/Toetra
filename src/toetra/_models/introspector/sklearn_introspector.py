from collections.abc import Iterable, Mapping
from typing import Any

import pandas as pd

from sklearn import __version__ as sklearn_version
from sklearn.base import is_classifier, is_regressor
from sklearn.linear_model import LogisticRegression

from toetra._compatibility.descriptors import (
    FrameworkModelDescriptor,
    NumericSemanticDescriptor,
)
from toetra._compiler.semantic.types.enums import EnumDataType

from toetra._models.detector.model_framework import EnumModelFramework
from toetra._models.introspector.base_introspector import BaseIntrospector
from toetra._models.schema.feature_schema import FeatureSchema
from toetra._models.schema.model_schema import ModelSchema
from toetra._models.schema.output_schema import (
    BinaryClassificationDecisionPolicy,
    ClassificationOutputSchema,
    RegressionOutputSchema,
    UnknownOutputSchema,
)

from toetra._models.errors.introspection import (
    MissingFeatureMetadataError,
    ReferenceDatasetError,
)
from toetra._models.families import (
    BINARY_LOGISTIC_AFFINE_MODEL_FAMILY,
    BINARY_LOGISTIC_AFFINE_SEMANTIC_PROFILE_ID,
)


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
        target_dtype = self._detect_target_dtype(target)
        target_source_dtype = self._detect_target_source_dtype(target)
        output_schema = self._build_output_schema(
            task=task,
            target_dtype=target_dtype,
            target_source_dtype=target_source_dtype,
            metadata=metadata,
        )
        return ModelSchema(
            framework=EnumModelFramework.SKLEARN,
            model_type=type(self.model).__name__,
            features=features,
            task=task,
            output_name=target,
            output_schema=output_schema,
            metadata=metadata,
            compatibility=self._compatibility_descriptor(
                features=features,
                task=task,
                metadata=metadata,
                target_source_dtype=target_source_dtype,
            ),
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

        data = self._read_source_data()
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
    # Pandas → Toetra type mapping
    # ======================================================

    def _map_dtype(self, dtype) -> EnumDataType:
        """
        Map pandas dtypes to Toetra semantic types.
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

        if is_classifier(self.model):
            return "classification"

        if is_regressor(self.model):
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
            2. explicit Toetra target_name
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

        data = self._read_source_data()
        if target not in data.columns:
            return None

        return self._map_dtype(data[target].dtype)

    # ======================================================
    # Output schema
    # ======================================================

    def _build_output_schema(
        self,
        *,
        task: str,
        target_dtype: EnumDataType | None,
        target_source_dtype: str | None,
        metadata: dict[str, Any],
    ):
        if task == "regression":
            return RegressionOutputSchema(
                value_dtype=target_dtype,
                value_source_dtype=target_source_dtype,
            )

        if task == "classification":
            raw_labels = metadata.get("classes")
            labels = self._to_python(raw_labels) if raw_labels is not None else []
            if not isinstance(labels, list):
                labels = list(labels)
            normalized_labels = tuple(self._normalize_label(label) for label in labels)
            probability_available = callable(getattr(self.model, "predict_proba", None))
            decision_policy = None
            if self._supports_binary_logistic_profile(
                labels=normalized_labels,
                metadata=metadata,
            ):
                decision_policy = BinaryClassificationDecisionPolicy(
                    negative_label=normalized_labels[0],
                    positive_label=normalized_labels[1],
                    semantic_profile_id=(BINARY_LOGISTIC_AFFINE_SEMANTIC_PROFILE_ID),
                )
            return ClassificationOutputSchema(
                label_dtype=target_dtype,
                labels=normalized_labels,
                label_source_dtype=target_source_dtype,
                probability_available=probability_available,
                decision_policy=decision_policy,
            )

        return UnknownOutputSchema(
            value_dtype=target_dtype,
            value_source_dtype=target_source_dtype,
        )

    @staticmethod
    def _normalize_label(value: Any) -> str | int | float | bool:
        if hasattr(value, "item"):
            value = value.item()
        if not isinstance(value, (str, int, float, bool)):
            raise TypeError(
                "Classification labels must normalize to string, integer, "
                "float, or boolean values"
            )
        return value

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

        data = self._read_source_data()
        if target not in data.columns:
            return None
        return str(data[target].dtype)

    def _read_source_data(self) -> pd.DataFrame:
        """Read the reference CSV while retaining model-layer ownership."""

        assert self.source_path is not None
        try:
            return pd.read_csv(self.source_path)
        except (
            OSError,
            UnicodeError,
            pd.errors.EmptyDataError,
            pd.errors.ParserError,
        ) as error:
            raise ReferenceDatasetError(
                f"Failed to read reference dataset: {self.source_path}"
            ) from error

    def _compatibility_descriptor(
        self,
        *,
        features: Mapping[str, FeatureSchema] | Iterable[FeatureSchema],
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
        if model_type == "LinearRegression" and task == "regression":
            model_family = "affine_regression"
        elif self._supports_binary_logistic_profile(
            labels=self._normalized_metadata_labels(metadata),
            metadata=metadata,
        ):
            model_family = BINARY_LOGISTIC_AFFINE_MODEL_FAMILY
        else:
            model_family = f"unknown:{task}:{model_type}"
        return FrameworkModelDescriptor(
            framework_adapter_id=EnumModelFramework.SKLEARN.value,
            framework_version=sklearn_version,
            model_family=model_family,
            source_execution_profile_id=profile_id,
            numeric_semantics=numeric_semantics,
            parameter_dtypes=parameter_dtypes,
            input_dtypes=tuple(
                feature.source_dtype or feature.dtype.value
                for feature in (
                    features.values() if isinstance(features, Mapping) else features
                )
            ),
            output_dtype=target_source_dtype,
        )

    def _supports_binary_logistic_profile(
        self,
        *,
        labels: tuple[Any, ...] | list[Any],
        metadata: dict[str, Any],
    ) -> bool:
        """Return whether this exact estimator matches the frozen P21 profile."""

        if type(self.model) is not LogisticRegression:
            return False
        if len(labels) != 2:
            return False
        if not callable(getattr(self.model, "predict_proba", None)):
            return False
        if not callable(getattr(self.model, "decision_function", None)):
            return False

        linear = metadata.get("linear")
        if not isinstance(linear, dict):
            return False
        coef = linear.get("coef")
        intercept = linear.get("intercept")
        if not isinstance(coef, list) or len(coef) != 1:
            return False
        if not isinstance(coef[0], list):
            return False
        if not isinstance(intercept, list) or len(intercept) != 1:
            return False
        return True

    def _normalized_metadata_labels(
        self,
        metadata: dict[str, Any],
    ) -> tuple[Any, ...]:
        raw_labels = metadata.get("classes")
        if raw_labels is None:
            return ()
        labels = self._to_python(raw_labels)
        if not isinstance(labels, list):
            labels = list(labels)
        return tuple(self._normalize_label(label) for label in labels)

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
