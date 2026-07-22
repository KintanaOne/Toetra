from __future__ import annotations

from dataclasses import dataclass

from dsl.compatibility.identifiers import (
    canonical_identifier,
    canonical_optional_version,
    canonical_tags,
    canonical_version,
)
from dsl.compatibility.enums import (
    BackendKind,
    NumericFamily,
    NumericRounding,
    RangeBehavior,
    SpecialValuePolicy,
)
from dsl.ir.ir2.requirements import IR2Requirements


@dataclass(frozen=True)
class NumericSemanticDescriptor:
    """Backend-neutral description of one numeric execution profile."""

    family: NumericFamily
    width_bits: int | None = None
    precision: str = "unknown"
    rounding: NumericRounding = NumericRounding.UNKNOWN
    special_values: SpecialValuePolicy = SpecialValuePolicy.UNKNOWN
    range_behavior: RangeBehavior = RangeBehavior.UNKNOWN

    @classmethod
    def exact_real(cls) -> NumericSemanticDescriptor:
        return cls(
            family=NumericFamily.REAL,
            precision="exact",
            rounding=NumericRounding.EXACT,
            special_values=SpecialValuePolicy.REJECTED,
            range_behavior=RangeBehavior.UNBOUNDED,
        )

    @classmethod
    def binary_float(cls, width_bits: int | None) -> NumericSemanticDescriptor:
        return cls(
            family=NumericFamily.BINARY_FLOAT,
            width_bits=width_bits,
            precision=(str(width_bits) if width_bits is not None else "unknown"),
            rounding=NumericRounding.NEAREST_EVEN,
            special_values=SpecialValuePolicy.SUPPORTED,
            range_behavior=RangeBehavior.FINITE_IEEE754,
        )

    @classmethod
    def unknown(cls) -> NumericSemanticDescriptor:
        return cls(family=NumericFamily.UNKNOWN)


@dataclass(frozen=True)
class FrameworkModelDescriptor:
    framework_adapter_id: str
    model_family: str
    source_execution_profile_id: str
    numeric_semantics: NumericSemanticDescriptor
    framework_version: str | None = None
    parameter_dtypes: tuple[str, ...] = ()
    input_dtypes: tuple[str, ...] = ()
    output_dtype: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "framework_adapter_id",
            canonical_identifier(
                self.framework_adapter_id, field_name="framework_adapter_id"
            ),
        )
        object.__setattr__(
            self,
            "model_family",
            canonical_identifier(self.model_family, field_name="model_family"),
        )
        object.__setattr__(
            self,
            "source_execution_profile_id",
            canonical_identifier(
                self.source_execution_profile_id,
                field_name="source_execution_profile_id",
            ),
        )
        object.__setattr__(
            self,
            "framework_version",
            canonical_optional_version(
                self.framework_version, field_name="framework_version"
            ),
        )
        object.__setattr__(
            self,
            "parameter_dtypes",
            tuple(value.strip() for value in self.parameter_dtypes),
        )
        object.__setattr__(
            self,
            "input_dtypes",
            tuple(value.strip() for value in self.input_dtypes),
        )
        if self.output_dtype is not None:
            object.__setattr__(self, "output_dtype", self.output_dtype.strip())


@dataclass(frozen=True)
class ModelEncoderDescriptor:
    encoder_id: str
    version: str
    semantic_target: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "encoder_id",
            canonical_identifier(self.encoder_id, field_name="encoder_id"),
        )
        object.__setattr__(
            self,
            "version",
            canonical_version(self.version, field_name="encoder_version"),
        )
        object.__setattr__(
            self,
            "semantic_target",
            canonical_identifier(self.semantic_target, field_name="semantic_target"),
        )


@dataclass(frozen=True)
class BackendProfileDescriptor:
    backend_kind: BackendKind
    adapter_id: str
    profile_id: str
    numeric_semantics: NumericSemanticDescriptor
    adapter_version: str | None = None
    supports_non_finite_values: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "adapter_id",
            canonical_identifier(self.adapter_id, field_name="backend_adapter_id"),
        )
        object.__setattr__(
            self,
            "profile_id",
            canonical_identifier(self.profile_id, field_name="backend_profile_id"),
        )
        object.__setattr__(
            self,
            "adapter_version",
            canonical_optional_version(
                self.adapter_version, field_name="backend_adapter_version"
            ),
        )


@dataclass(frozen=True)
class PropertyNumericRequirements:
    tags: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        object.__setattr__(self, "tags", canonical_tags(self.tags))

    @classmethod
    def from_ir2(cls, requirements: IR2Requirements) -> PropertyNumericRequirements:
        tags: set[str] = set()
        if requirements.requires_numeric_comparisons:
            tags.add("numeric_comparisons")
        if requirements.requires_affine_arithmetic:
            tags.add("affine_arithmetic")
        if requirements.requires_nonlinear_arithmetic:
            tags.add("nonlinear_arithmetic")
        if requirements.requires_symbolic_division:
            tags.add("symbolic_division")
        if requirements.requires_domains:
            tags.add("domains")
        if requirements.requires_neighborhoods:
            tags.add("neighborhoods")
        if requirements.requires_finite_set_membership:
            tags.add("finite_set_membership")
        if requirements.requires_symbolic_categories:
            tags.add("symbolic_categories")
        if requirements.requires_model_assertions:
            tags.add("model_assertions")
        if requirements.requires_model_semantic_quantities:
            tags.add("model_semantic_quantities")
        if requirements.requires_logistic_probability_threshold:
            tags.add("logistic_probability_threshold")
        if requirements.requires_transcendental_threshold_lowering:
            tags.add("transcendental_threshold_lowering")
        tags.update(
            f"scalar_sort:{sort.value}" for sort in requirements.required_scalar_sorts
        )
        return cls(tags=frozenset(tags))
