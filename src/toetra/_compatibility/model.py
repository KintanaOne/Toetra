from __future__ import annotations

from dataclasses import dataclass

from toetra._compatibility.descriptors import (
    BackendProfileDescriptor,
    FrameworkModelDescriptor,
    ModelEncoderDescriptor,
    PropertyNumericRequirements,
)
from toetra._compatibility.enums import (
    CompatibilityClassification,
    ConclusionKind,
    ConclusionScope,
    SupportStatus,
)
from toetra._compatibility.errors import InvalidCompatibilityRuleError
from toetra._compatibility.identifiers import (
    canonical_identifier,
    canonical_optional_identifier,
    canonical_optional_version,
    canonical_tags,
    canonical_version,
)


@dataclass(frozen=True)
class NumericCompatibilityContext:
    source_model: FrameworkModelDescriptor
    model_encoder: ModelEncoderDescriptor


@dataclass(frozen=True)
class NumericCompatibilityQuery:
    framework_adapter_id: str
    framework_version: str | None
    model_family: str
    source_execution_profile_id: str
    model_encoder_id: str
    model_encoder_version: str
    backend_kind: str
    backend_adapter_id: str
    backend_profile_id: str
    backend_version: str | None
    property_numeric_requirements: PropertyNumericRequirements
    contains_non_finite_values: bool = False

    def __post_init__(self) -> None:
        identifier_fields = (
            "framework_adapter_id",
            "model_family",
            "source_execution_profile_id",
            "model_encoder_id",
            "backend_kind",
            "backend_adapter_id",
            "backend_profile_id",
        )
        for field_name in identifier_fields:
            object.__setattr__(
                self,
                field_name,
                canonical_identifier(getattr(self, field_name), field_name=field_name),
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
            "model_encoder_version",
            canonical_version(
                self.model_encoder_version, field_name="model_encoder_version"
            ),
        )
        object.__setattr__(
            self,
            "backend_version",
            canonical_optional_version(
                self.backend_version, field_name="backend_version"
            ),
        )

    @classmethod
    def build(
        cls,
        *,
        context: NumericCompatibilityContext,
        backend: BackendProfileDescriptor,
        requirements: PropertyNumericRequirements,
        contains_non_finite_values: bool,
    ) -> NumericCompatibilityQuery:
        source = context.source_model
        encoder = context.model_encoder
        return cls(
            framework_adapter_id=source.framework_adapter_id,
            framework_version=source.framework_version,
            model_family=source.model_family,
            source_execution_profile_id=source.source_execution_profile_id,
            model_encoder_id=encoder.encoder_id,
            model_encoder_version=encoder.version,
            backend_kind=backend.backend_kind.value,
            backend_adapter_id=backend.adapter_id,
            backend_profile_id=backend.profile_id,
            backend_version=backend.adapter_version,
            property_numeric_requirements=requirements,
            contains_non_finite_values=contains_non_finite_values,
        )


@dataclass(frozen=True)
class CompatibilityRulePattern:
    framework_adapter_id: str | None = None
    framework_version: str | None = None
    model_family: str | None = None
    source_execution_profile_id: str | None = None
    model_encoder_id: str | None = None
    model_encoder_version: str | None = None
    backend_kind: str | None = None
    backend_adapter_id: str | None = None
    backend_profile_id: str | None = None
    backend_version: str | None = None
    required_property_tags: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        identifier_fields = (
            "framework_adapter_id",
            "model_family",
            "source_execution_profile_id",
            "model_encoder_id",
            "backend_kind",
            "backend_adapter_id",
            "backend_profile_id",
        )
        for field_name in identifier_fields:
            object.__setattr__(
                self,
                field_name,
                canonical_optional_identifier(
                    getattr(self, field_name), field_name=field_name
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
            "model_encoder_version",
            canonical_optional_version(
                self.model_encoder_version, field_name="model_encoder_version"
            ),
        )
        object.__setattr__(
            self,
            "backend_version",
            canonical_optional_version(
                self.backend_version, field_name="backend_version"
            ),
        )
        object.__setattr__(
            self,
            "required_property_tags",
            canonical_tags(self.required_property_tags),
        )

    def matches(self, query: NumericCompatibilityQuery) -> bool:
        scalar_fields = (
            "framework_adapter_id",
            "framework_version",
            "model_family",
            "source_execution_profile_id",
            "model_encoder_id",
            "model_encoder_version",
            "backend_kind",
            "backend_adapter_id",
            "backend_profile_id",
            "backend_version",
        )
        for field_name in scalar_fields:
            expected = getattr(self, field_name)
            if expected is not None and expected != getattr(query, field_name):
                return False
        return self.required_property_tags.issubset(
            query.property_numeric_requirements.tags
        )

    @property
    def specificity(self) -> int:
        scalar_values = (
            self.framework_adapter_id,
            self.framework_version,
            self.model_family,
            self.source_execution_profile_id,
            self.model_encoder_id,
            self.model_encoder_version,
            self.backend_kind,
            self.backend_adapter_id,
            self.backend_profile_id,
            self.backend_version,
        )
        return sum(value is not None for value in scalar_values) + len(
            self.required_property_tags
        )


@dataclass(frozen=True)
class CompatibilityRule:
    rule_id: str
    pattern: CompatibilityRulePattern
    support_status: SupportStatus
    classification: CompatibilityClassification
    semantic_target: str
    evidence_id: str
    permitted_conclusions: frozenset[ConclusionKind]
    conclusion_scope: ConclusionScope
    assumptions_and_preconditions: tuple[str, ...] = ()
    replay_required_for: frozenset[ConclusionKind] = frozenset()
    diagnostics: tuple[str, ...] = ()
    documentation_reference: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "rule_id",
            canonical_identifier(self.rule_id, field_name="rule_id"),
        )
        object.__setattr__(
            self,
            "semantic_target",
            canonical_identifier(self.semantic_target, field_name="semantic_target"),
        )
        if self.replay_required_for - self.permitted_conclusions:
            raise InvalidCompatibilityRuleError(
                f"Rule {self.rule_id!r} requires replay for conclusions it does "
                "not permit."
            )
        non_candidate_replay = self.replay_required_for - {
            ConclusionKind.UNIVERSAL_COUNTEREXAMPLE,
            ConclusionKind.EXISTENTIAL_WITNESS,
        }
        if non_candidate_replay:
            raise InvalidCompatibilityRuleError(
                f"Rule {self.rule_id!r} declares replay for non-candidate "
                "conclusions."
            )

        if self.conclusion_scope is not ConclusionScope.SOURCE_ARTIFACT:
            return

        source_allowed = {
            CompatibilityClassification.EXACT: frozenset(ConclusionKind),
            CompatibilityClassification.SOUND_OVER_APPROXIMATION: frozenset(
                {
                    ConclusionKind.UNIVERSAL_PROOF,
                    ConclusionKind.EXISTENTIAL_NO_WITNESS,
                }
            ),
            CompatibilityClassification.SOUND_UNDER_APPROXIMATION: frozenset(
                {
                    ConclusionKind.UNIVERSAL_COUNTEREXAMPLE,
                    ConclusionKind.EXISTENTIAL_WITNESS,
                }
            ),
            CompatibilityClassification.LOSSY: frozenset(),
            CompatibilityClassification.INCOMPATIBLE: frozenset(),
            CompatibilityClassification.UNKNOWN: frozenset(),
        }
        invalid = self.permitted_conclusions - source_allowed[self.classification]
        if invalid:
            values = ", ".join(sorted(item.value for item in invalid))
            raise InvalidCompatibilityRuleError(
                f"Rule {self.rule_id!r} permits source-artifact conclusions "
                f"not justified by {self.classification.value}: {values}."
            )


@dataclass(frozen=True)
class NumericCompatibilityAssessment:
    query: NumericCompatibilityQuery
    support_status: SupportStatus
    classification: CompatibilityClassification
    semantic_target: str
    permitted_conclusions: frozenset[ConclusionKind]
    conclusion_scope: ConclusionScope
    matched_rule_id: str | None = None
    evidence_id: str | None = None
    assumptions_and_preconditions: tuple[str, ...] = ()
    replay_required_for: frozenset[ConclusionKind] = frozenset()
    diagnostics: tuple[str, ...] = ()
    documentation_reference: str | None = None

    @property
    def is_executable(self) -> bool:
        return self.support_status in {
            SupportStatus.SUPPORTED,
            SupportStatus.EXPERIMENTAL,
        } and self.classification not in {
            CompatibilityClassification.INCOMPATIBLE,
            CompatibilityClassification.UNKNOWN,
        }

    @property
    def summary(self) -> str:
        rule = self.matched_rule_id or "<no matching rule>"
        return (
            f"numeric compatibility {self.classification.value} via {rule}; "
            f"semantic target={self.semantic_target}; "
            f"conclusion scope={self.conclusion_scope.value}"
        )
