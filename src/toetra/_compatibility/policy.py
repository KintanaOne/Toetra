from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING

from toetra._backends.diagnostics import (
    BackendDiagnosticSeverity,
    BackendResultDiagnostic,
)
from toetra._backends.results import VerificationResult, VerificationStatus
from toetra._compatibility.enums import ConclusionKind, ConclusionScope
from toetra._compatibility.model import NumericCompatibilityAssessment

NUMERIC_CONCLUSION_NOT_PERMITTED = "NUMERIC_CONCLUSION_NOT_PERMITTED"
NUMERIC_COMPATIBILITY_REPLAY_REQUIRED = "NUMERIC_COMPATIBILITY_REPLAY_REQUIRED"
SEMANTIC_LOWERING_CONCLUSION_NOT_PERMITTED = (
    "SEMANTIC_LOWERING_CONCLUSION_NOT_PERMITTED"
)

if TYPE_CHECKING:
    from toetra._models.semantics.evidence import SemanticLoweringEvidence


def apply_numeric_compatibility_policy(
    result: VerificationResult,
    assessment: NumericCompatibilityAssessment | None,
) -> VerificationResult:
    """Attach compatibility provenance and fail closed on invalid conclusions."""

    if assessment is None:
        return result

    conclusion = _conclusion_kind(result.status)
    diagnostics = list(result.diagnostics)
    status = result.status
    message = result.message

    if conclusion is not None and conclusion not in assessment.permitted_conclusions:
        status = VerificationStatus.UNKNOWN
        message = (
            "Verification inconclusive: the matched numeric compatibility rule "
            f"does not permit the backend conclusion {conclusion.value!r}."
        )
        diagnostics.append(
            BackendResultDiagnostic(
                code=NUMERIC_CONCLUSION_NOT_PERMITTED,
                severity=BackendDiagnosticSeverity.WARNING,
                message=message,
            )
        )
    elif (
        conclusion is not None
        and conclusion in assessment.replay_required_for
        and assessment.conclusion_scope is ConclusionScope.SOURCE_ARTIFACT
    ):
        diagnostics.append(
            BackendResultDiagnostic(
                code=NUMERIC_COMPATIBILITY_REPLAY_REQUIRED,
                severity=BackendDiagnosticSeverity.INFO,
                message=(
                    "This conclusion requires concrete replay before it can be "
                    "promoted from the declared semantic target to the source "
                    "artifact."
                ),
            )
        )

    metadata = dict(result.metadata)
    metadata["numeric_compatibility"] = {
        "matched_rule_id": assessment.matched_rule_id,
        "support_status": assessment.support_status.value,
        "classification": assessment.classification.value,
        "semantic_target": assessment.semantic_target,
        "conclusion_scope": assessment.conclusion_scope.value,
        "evidence_id": assessment.evidence_id,
    }
    if status is not result.status:
        metadata["backend_interpreted_status"] = result.status.value

    return VerificationResult(
        status=status,
        backend=result.backend,
        backend_status=result.backend_status,
        assignments=result.assignments,
        message=message,
        diagnostics=tuple(diagnostics),
        metadata=metadata,
        execution=result.execution,
    )


def apply_semantic_lowering_policy(
    result: VerificationResult,
    evidence: Iterable[SemanticLoweringEvidence],
) -> VerificationResult:
    """Fail closed when an approximate semantic rewrite cannot justify a result."""

    items = tuple(evidence)
    if not items:
        return result

    permitted = set(ConclusionKind)
    for item in items:
        permitted.intersection_update(item.permitted_conclusions)

    conclusion = _conclusion_kind(result.status)
    diagnostics = list(result.diagnostics)
    status = result.status
    message = result.message
    if conclusion is not None and conclusion not in permitted:
        status = VerificationStatus.UNKNOWN
        message = (
            "Verification inconclusive: the semantic probability-threshold "
            f"lowering does not permit the backend conclusion {conclusion.value!r}."
        )
        diagnostics.append(
            BackendResultDiagnostic(
                code=SEMANTIC_LOWERING_CONCLUSION_NOT_PERMITTED,
                severity=BackendDiagnosticSeverity.WARNING,
                message=message,
            )
        )

    metadata = dict(result.metadata)
    metadata["semantic_lowering"] = {
        "permitted_conclusions": tuple(
            conclusion.value for conclusion in ConclusionKind if conclusion in permitted
        ),
        "evidence": tuple(item.to_dict() for item in items),
    }
    if status is not result.status:
        metadata.setdefault("backend_interpreted_status", result.status.value)

    return VerificationResult(
        status=status,
        backend=result.backend,
        backend_status=result.backend_status,
        assignments=result.assignments,
        message=message,
        diagnostics=tuple(diagnostics),
        metadata=metadata,
        execution=result.execution,
    )


def _conclusion_kind(status: VerificationStatus) -> ConclusionKind | None:
    mapping = {
        VerificationStatus.PROVED: ConclusionKind.UNIVERSAL_PROOF,
        VerificationStatus.COUNTEREXAMPLE: ConclusionKind.UNIVERSAL_COUNTEREXAMPLE,
        VerificationStatus.WITNESS: ConclusionKind.EXISTENTIAL_WITNESS,
        VerificationStatus.NO_WITNESS: ConclusionKind.EXISTENTIAL_NO_WITNESS,
    }
    return mapping.get(status)
