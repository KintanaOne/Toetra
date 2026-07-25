from __future__ import annotations

import hashlib
import importlib.metadata
import os
import platform
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dsl.backends.results import VerificationResult
from dsl.backends.router import BackendRoute
from dsl.ir.ir2.context import IR2BuildContext
from dsl.ir.ir2.nodes import VerificationTaskIR2
from dsl.provenance.fingerprint import (
    CanonicalizationError,
    canonical_json_bytes,
    fingerprint_canonical_json,
    fingerprint_file,
    fingerprint_text,
)
from dsl.provenance.model import (
    ArtifactProvenance,
    CompilerProvenance,
    FingerprintStatus,
    ProvenanceCompleteness,
    ReportProvenance,
    SoftwareProvenance,
    VerificationProvenanceContext,
)
from model.schema.model_schema import ModelSchema

_CORE_DISTRIBUTIONS = (
    "lark",
    "joblib",
    "pandas",
    "scikit-learn",
    "z3-solver",
)


def build_provenance_context(
    *,
    specification_source: str,
    specification_path: Path | None,
    model_path: Path | None,
    dataset_path: Path | None,
    anchor_source: Any | None,
    anchor_resolver: object | None,
    anchors_used: bool,
    schema: ModelSchema,
    ir2_context: IR2BuildContext,
    captured_at: datetime | None = None,
) -> VerificationProvenanceContext:
    """Capture immutable invocation evidence before backend execution begins."""

    timestamp = captured_at or datetime.now(timezone.utc)
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    timestamp = timestamp.astimezone(timezone.utc)

    artifacts = {
        "specification": _specification_artifact(
            specification_source,
            path=specification_path,
        ),
        "model": _file_artifact(
            role="model",
            path=model_path,
            absent_status=FingerprintStatus.NOT_PROVIDED,
            absent_kind="schema_only",
        ),
        "dataset": _file_artifact(
            role="dataset",
            path=dataset_path,
            absent_status=FingerprintStatus.NOT_PROVIDED,
            absent_kind="not_provided",
        ),
        "anchor_source": _anchor_artifact(
            anchor_source=anchor_source,
            anchor_resolver=anchor_resolver,
            dataset_path=dataset_path,
            anchors_used=anchors_used,
        ),
        "model_schema": _schema_artifact(schema),
    }

    input_fingerprint = _digest_payload(
        {
            "artifacts": {
                role: _artifact_identity(artifact)
                for role, artifact in artifacts.items()
            },
            "compiler_policy": _compiler_policy_payload(ir2_context),
        }
    )
    unavailable_inputs = tuple(
        role
        for role, artifact in artifacts.items()
        if artifact.status is FingerprintStatus.UNAVAILABLE
    )
    completeness = (
        ProvenanceCompleteness.COMPLETE
        if not unavailable_inputs
        else ProvenanceCompleteness.PARTIAL
    )

    return VerificationProvenanceContext(
        captured_at_utc=timestamp.isoformat().replace("+00:00", "Z"),
        input_fingerprint=input_fingerprint,
        completeness=completeness,
        unavailable_inputs=unavailable_inputs,
        artifacts=artifacts,
        software=_software_provenance(),
        preferred_normal_form=(
            ir2_context.preferred_normal_form.value
            if ir2_context.preferred_normal_form is not None
            else None
        ),
        max_distribution_size=ir2_context.max_distribution_size,
        allow_nnf_fallback=ir2_context.allow_nnf_fallback,
        backend_hint=(
            ir2_context.backend_hint.value
            if ir2_context.backend_hint is not None
            else None
        ),
        strict=ir2_context.strict,
    )


def build_report_provenance(
    context: VerificationProvenanceContext,
    *,
    task: VerificationTaskIR2,
    route: BackendRoute,
    result: VerificationResult,
    property_index: int,
) -> ReportProvenance:
    """Derive property, route and full verification fingerprints."""

    property_fingerprint = _digest_payload(
        {
            "index": property_index,
            "property_type": task.property_type.value,
            "semantics": task.semantics.value,
            "scope": {
                "kind": task.scope.kind,
                "quantifier": task.scope.quantifier,
                "variables": dict(task.scope.variables),
            },
            "normal_form": task.normal_form.value,
            "spec_formula": task.spec_formula,
        }
    )
    route_fingerprint = _digest_payload(_route_payload(route))
    execution_policy_fingerprint = _digest_payload(_execution_policy_payload(result))
    verification_fingerprint = _digest_payload(
        {
            "input_fingerprint": context.input_fingerprint,
            "property_fingerprint": property_fingerprint,
            "route_fingerprint": route_fingerprint,
            "execution_policy_fingerprint": execution_policy_fingerprint,
        }
    )

    return ReportProvenance(
        captured_at_utc=context.captured_at_utc,
        input_fingerprint=context.input_fingerprint,
        completeness=context.completeness,
        unavailable_inputs=context.unavailable_inputs,
        property_fingerprint=property_fingerprint,
        route_fingerprint=route_fingerprint,
        execution_policy_fingerprint=execution_policy_fingerprint,
        verification_fingerprint=verification_fingerprint,
        artifacts=context.artifacts,
        software=context.software,
        compiler=CompilerProvenance(
            preferred_normal_form=context.preferred_normal_form,
            actual_normal_form=task.normal_form.value,
            max_distribution_size=context.max_distribution_size,
            allow_nnf_fallback=context.allow_nnf_fallback,
            backend_hint=context.backend_hint,
            strict=context.strict,
            source_ir=_optional_text(task.metadata.get("source_ir")),
            builder=_optional_text(task.metadata.get("builder")),
        ),
    )


def _specification_artifact(
    source: str,
    *,
    path: Path | None,
) -> ArtifactProvenance:
    return ArtifactProvenance(
        role="specification",
        source_kind="file" if path is not None else "inline_text",
        status=FingerprintStatus.AVAILABLE,
        name=path.name if path is not None else None,
        fingerprint=fingerprint_text(source),
    )


def _file_artifact(
    *,
    role: str,
    path: Path | None,
    absent_status: FingerprintStatus,
    absent_kind: str,
) -> ArtifactProvenance:
    if path is None:
        return ArtifactProvenance(
            role=role,
            source_kind=absent_kind,
            status=absent_status,
        )
    try:
        fingerprint = fingerprint_file(path)
    except OSError as error:
        return ArtifactProvenance(
            role=role,
            source_kind="file",
            status=FingerprintStatus.UNAVAILABLE,
            name=path.name,
            unavailable_reason=f"Unable to fingerprint file: {error}",
        )
    return ArtifactProvenance(
        role=role,
        source_kind="file",
        status=FingerprintStatus.AVAILABLE,
        name=path.name,
        fingerprint=fingerprint,
    )


def _anchor_artifact(
    *,
    anchor_source: Any | None,
    anchor_resolver: object | None,
    dataset_path: Path | None,
    anchors_used: bool,
) -> ArtifactProvenance:
    if not anchors_used:
        return ArtifactProvenance(
            role="anchor_source",
            source_kind="not_used",
            status=FingerprintStatus.NOT_USED,
        )
    if anchor_resolver is not None:
        resolver_type = type(anchor_resolver)
        return ArtifactProvenance(
            role="anchor_source",
            source_kind="custom_resolver",
            status=FingerprintStatus.UNAVAILABLE,
            name=f"{resolver_type.__module__}.{resolver_type.__qualname__}",
            unavailable_reason=(
                "Custom anchor resolvers are opaque unless they expose their own "
                "auditable artifact contract."
            ),
        )
    if anchor_source is None:
        if dataset_path is None:
            return ArtifactProvenance(
                role="anchor_source",
                source_kind="dataset_fallback",
                status=FingerprintStatus.UNAVAILABLE,
                unavailable_reason="Dataset fallback was selected without a path.",
            )
        artifact = _file_artifact(
            role="anchor_source",
            path=dataset_path,
            absent_status=FingerprintStatus.UNAVAILABLE,
            absent_kind="dataset_fallback",
        )
        return ArtifactProvenance(
            role=artifact.role,
            source_kind="dataset_fallback",
            status=artifact.status,
            name=artifact.name,
            fingerprint=artifact.fingerprint,
            unavailable_reason=artifact.unavailable_reason,
        )

    if isinstance(anchor_source, (str, Path)):
        return _file_artifact(
            role="anchor_source",
            path=Path(anchor_source).expanduser().resolve(),
            absent_status=FingerprintStatus.UNAVAILABLE,
            absent_kind="file",
        )

    try:
        payload = {
            "columns": [str(column) for column in anchor_source.columns],
            "dtypes": [str(dtype) for dtype in anchor_source.dtypes],
            "index": anchor_source.index.tolist(),
            "records": anchor_source.to_dict(orient="records"),
        }
        fingerprint = fingerprint_canonical_json(
            payload,
            canonicalization="pandas_dataframe_canonical_json_v1",
        )
    except (CanonicalizationError, AttributeError, TypeError, ValueError) as error:
        return ArtifactProvenance(
            role="anchor_source",
            source_kind="dataframe",
            status=FingerprintStatus.UNAVAILABLE,
            unavailable_reason=f"Unable to canonicalize DataFrame: {error}",
        )
    return ArtifactProvenance(
        role="anchor_source",
        source_kind="dataframe",
        status=FingerprintStatus.AVAILABLE,
        fingerprint=fingerprint,
    )


def _schema_artifact(schema: ModelSchema) -> ArtifactProvenance:
    payload = {
        "framework": schema.framework.value,
        "model_type": schema.model_type,
        "features": [
            {
                "name": feature.name,
                "dtype": feature.dtype.value,
                "nullable": feature.nullable,
                "source_dtype": feature.source_dtype,
            }
            for feature in schema.features.values()
        ],
        "output_name": schema.output_name,
        "task": schema.task,
        "output_schema": _output_schema_payload(schema.output_schema),
        "metadata": schema.metadata,
        "compatibility": schema.compatibility,
    }
    try:
        fingerprint = fingerprint_canonical_json(
            payload,
            canonicalization="toetra_model_schema_canonical_json_v3",
        )
    except CanonicalizationError as error:
        return ArtifactProvenance(
            role="model_schema",
            source_kind="normalized_schema",
            status=FingerprintStatus.UNAVAILABLE,
            unavailable_reason=f"Unable to canonicalize model schema: {error}",
        )
    return ArtifactProvenance(
        role="model_schema",
        source_kind="normalized_schema",
        status=FingerprintStatus.AVAILABLE,
        fingerprint=fingerprint,
    )


def _output_schema_payload(output_schema: object) -> dict[str, object]:
    kind = getattr(getattr(output_schema, "kind", None), "value", "unknown")
    observables = [
        getattr(value, "value", str(value))
        for value in getattr(output_schema, "available_observables", ())
    ]
    payload: dict[str, object] = {
        "kind": kind,
        "available_observables": observables,
        "primary_dtype": getattr(
            getattr(output_schema, "primary_dtype", None), "value", None
        ),
        "source_dtype": getattr(output_schema, "source_dtype", None),
    }
    labels = getattr(output_schema, "labels", None)
    if labels is not None:
        payload["labels"] = list(labels)
    probability_available = getattr(output_schema, "probability_available", None)
    if probability_available is not None:
        payload["probability_available"] = bool(probability_available)
    policy = getattr(output_schema, "decision_policy", None)
    if policy is not None:
        payload["decision_policy"] = {
            "negative_label": policy.negative_label,
            "positive_label": policy.positive_label,
            "probability_threshold": policy.probability_threshold,
            "oriented_decision_threshold": (policy.oriented_decision_threshold),
            "positive_when_strictly_greater": (policy.positive_when_strictly_greater),
            "equality_label": policy.equality_label,
            "policy_source": policy.policy_source,
            "semantic_profile_id": policy.semantic_profile_id,
        }
    return payload


def _software_provenance() -> SoftwareProvenance:
    components: dict[str, str] = {}
    for distribution in _CORE_DISTRIBUTIONS:
        try:
            components[distribution] = importlib.metadata.version(distribution)
        except importlib.metadata.PackageNotFoundError:
            continue
    return SoftwareProvenance(
        toetra_version=_distribution_version("toetra"),
        toetra_build_id=_toetra_build_id(),
        python_version=platform.python_version(),
        python_implementation=platform.python_implementation(),
        platform=f"{platform.system()}-{platform.release()}-{platform.machine()}",
        components=components,
    )


def _toetra_build_id() -> str | None:
    explicit = os.environ.get("TOETRA_BUILD_ID")
    if explicit:
        return explicit.strip() or None

    repository_root = Path(__file__).resolve().parents[2]
    git_directory = repository_root / ".git"
    head_path = git_directory / "HEAD"
    try:
        head = head_path.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    if not head.startswith("ref: "):
        return f"git:{head}" if head else None

    reference = head.removeprefix("ref: ").strip()
    try:
        commit = (git_directory / reference).read_text(encoding="utf-8").strip()
    except OSError:
        commit = _packed_git_reference(git_directory, reference)
    return f"git:{commit}" if commit else None


def _packed_git_reference(git_directory: Path, reference: str) -> str | None:
    try:
        lines = (git_directory / "packed-refs").read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    for line in lines:
        if not line or line.startswith(("#", "^")):
            continue
        commit, separator, candidate = line.partition(" ")
        if separator and candidate == reference:
            return commit
    return None


def _distribution_version(name: str) -> str:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        if name == "toetra":
            return "source-checkout"
        return "unknown"


def _compiler_policy_payload(context: IR2BuildContext) -> dict[str, Any]:
    return {
        "preferred_normal_form": (
            context.preferred_normal_form.value
            if context.preferred_normal_form is not None
            else None
        ),
        "max_distribution_size": context.max_distribution_size,
        "allow_nnf_fallback": context.allow_nnf_fallback,
        "backend_hint": (
            context.backend_hint.value if context.backend_hint is not None else None
        ),
        "strict": context.strict,
    }


def _route_payload(route: BackendRoute) -> dict[str, Any]:
    assessment = route.numeric_compatibility
    compatibility: dict[str, Any] | None = None
    if assessment is not None:
        query = assessment.query
        compatibility = {
            "rule_id": assessment.matched_rule_id,
            "support_status": assessment.support_status.value,
            "classification": assessment.classification.value,
            "semantic_target": assessment.semantic_target,
            "conclusion_scope": assessment.conclusion_scope.value,
            "evidence_id": assessment.evidence_id,
            "permitted_conclusions": sorted(
                item.value for item in assessment.permitted_conclusions
            ),
            "assumptions_and_preconditions": list(
                assessment.assumptions_and_preconditions
            ),
            "diagnostics": list(assessment.diagnostics),
            "query": {
                "framework_adapter_id": query.framework_adapter_id,
                "framework_version": query.framework_version,
                "model_family": query.model_family,
                "source_execution_profile_id": query.source_execution_profile_id,
                "model_encoder_id": query.model_encoder_id,
                "model_encoder_version": query.model_encoder_version,
                "backend_kind": query.backend_kind,
                "backend_adapter_id": query.backend_adapter_id,
                "backend_profile_id": query.backend_profile_id,
                "backend_version": query.backend_version,
                "property_numeric_requirements": sorted(
                    query.property_numeric_requirements.tags
                ),
                "contains_non_finite_values": query.contains_non_finite_values,
            },
        }
    numeric_profile = route.capabilities.numeric_profile
    return {
        "backend": route.backend.value,
        "numeric_profile": numeric_profile,
        "numeric_compatibility": compatibility,
    }


def _execution_policy_payload(result: VerificationResult) -> dict[str, Any] | None:
    execution = result.execution
    if execution is None:
        return None
    policy = execution.policy
    return {
        "timeout_ms": policy.timeout_ms,
        "max_backend_units": policy.max_backend_units,
        "max_memory_mb": policy.max_memory_mb,
        "deterministic_seed": policy.deterministic_seed,
        "backend_options": dict(policy.backend_options),
    }


def _artifact_identity(artifact: ArtifactProvenance) -> dict[str, Any]:
    fingerprint = artifact.fingerprint
    return {
        "role": artifact.role,
        "source_kind": artifact.source_kind,
        "status": artifact.status.value,
        "fingerprint": (
            {
                "algorithm": fingerprint.algorithm,
                "digest": fingerprint.digest,
                "size_bytes": fingerprint.size_bytes,
                "canonicalization": fingerprint.canonicalization,
            }
            if fingerprint is not None
            else None
        ),
    }


def _digest_payload(payload: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def _optional_text(value: object) -> str | None:
    return str(value) if value is not None else None
