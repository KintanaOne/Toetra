from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Mapping


class FingerprintStatus(str, Enum):
    """Availability state of one auditable artifact fingerprint."""

    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    NOT_PROVIDED = "not_provided"
    NOT_USED = "not_used"


class ProvenanceCompleteness(str, Enum):
    """Whether every artifact actually consumed can be reproduced."""

    COMPLETE = "complete"
    PARTIAL = "partial"


@dataclass(frozen=True)
class ContentFingerprint:
    """Portable digest of the exact or canonical content consumed by Toetra."""

    algorithm: str
    digest: str
    size_bytes: int
    canonicalization: str

    def __post_init__(self) -> None:
        algorithm = self.algorithm.strip().lower()
        digest = self.digest.strip().lower()
        canonicalization = self.canonicalization.strip()
        if not algorithm:
            raise ValueError("Fingerprint algorithm must not be empty")
        if not digest:
            raise ValueError("Fingerprint digest must not be empty")
        if self.size_bytes < 0:
            raise ValueError("Fingerprint size_bytes must be non-negative")
        if not canonicalization:
            raise ValueError("Fingerprint canonicalization must not be empty")
        object.__setattr__(self, "algorithm", algorithm)
        object.__setattr__(self, "digest", digest)
        object.__setattr__(self, "canonicalization", canonicalization)

    @property
    def identifier(self) -> str:
        return f"{self.algorithm}:{self.digest}"

    @property
    def short_identifier(self) -> str:
        return f"{self.algorithm}:{self.digest[:12]}"


@dataclass(frozen=True)
class ArtifactProvenance:
    """Identity and fingerprint evidence for one verification input artifact."""

    role: str
    source_kind: str
    status: FingerprintStatus
    name: str | None = None
    fingerprint: ContentFingerprint | None = None
    unavailable_reason: str | None = None

    def __post_init__(self) -> None:
        role = self.role.strip()
        source_kind = self.source_kind.strip()
        name = self.name.strip() if self.name is not None else None
        reason = (
            self.unavailable_reason.strip()
            if self.unavailable_reason is not None
            else None
        )
        if not role:
            raise ValueError("Artifact role must not be empty")
        if not source_kind:
            raise ValueError("Artifact source_kind must not be empty")
        if self.status is FingerprintStatus.AVAILABLE and self.fingerprint is None:
            raise ValueError("Available artifact provenance requires a fingerprint")
        if (
            self.status is not FingerprintStatus.AVAILABLE
            and self.fingerprint is not None
        ):
            raise ValueError(
                "Unavailable artifact provenance must not carry a fingerprint"
            )
        if self.status is FingerprintStatus.UNAVAILABLE and reason is None:
            raise ValueError("Unavailable artifact provenance requires a reason")
        object.__setattr__(self, "role", role)
        object.__setattr__(self, "source_kind", source_kind)
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "unavailable_reason", reason)


@dataclass(frozen=True)
class SoftwareProvenance:
    """Minimal runtime identity needed to interpret a verification report."""

    toetra_version: str
    toetra_build_id: str | None
    python_version: str
    python_implementation: str
    platform: str
    components: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "components", MappingProxyType(dict(self.components)))


@dataclass(frozen=True)
class CompilerProvenance:
    """Compiler configuration and the actual IR2 form used for one property."""

    preferred_normal_form: str | None
    actual_normal_form: str
    max_distribution_size: int
    allow_nnf_fallback: bool
    backend_hint: str | None
    strict: bool
    source_ir: str | None
    builder: str | None


@dataclass(frozen=True)
class VerificationProvenanceContext:
    """Invocation-level evidence shared by every property in one session."""

    captured_at_utc: str
    input_fingerprint: str
    completeness: ProvenanceCompleteness
    unavailable_inputs: tuple[str, ...]
    artifacts: Mapping[str, ArtifactProvenance]
    software: SoftwareProvenance
    preferred_normal_form: str | None
    max_distribution_size: int
    allow_nnf_fallback: bool
    backend_hint: str | None
    strict: bool

    def __post_init__(self) -> None:
        object.__setattr__(self, "artifacts", MappingProxyType(dict(self.artifacts)))


@dataclass(frozen=True)
class ReportProvenance:
    """Auditable identity of one concrete property verification."""

    captured_at_utc: str
    input_fingerprint: str
    completeness: ProvenanceCompleteness
    unavailable_inputs: tuple[str, ...]
    property_fingerprint: str
    route_fingerprint: str
    execution_policy_fingerprint: str
    verification_fingerprint: str
    artifacts: Mapping[str, ArtifactProvenance]
    software: SoftwareProvenance
    compiler: CompilerProvenance

    def __post_init__(self) -> None:
        object.__setattr__(self, "artifacts", MappingProxyType(dict(self.artifacts)))
