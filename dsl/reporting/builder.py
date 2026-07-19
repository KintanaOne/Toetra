from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from dsl.backends.results import VerificationResult
from dsl.backends.router import BackendRoute
from dsl.ir.ir1.nodes import (
    AndIR,
    AtomicIR,
    ComparisonIR,
    LogicalIR,
    NotIR,
    OrIR,
    ProblemIR,
)
from dsl.ir.ir1.scalar import format_scalar_expression
from dsl.ir.ir2.nodes import NNFFormulaIR2, VerificationTaskIR2
from dsl.provenance.builder import build_report_provenance
from dsl.provenance.model import VerificationProvenanceContext
from dsl.reporting.model import (
    ReportAssignment,
    ReportAssignmentKind,
    ReportBackendExecution,
    ReportNumericCompatibility,
    ReportPointEvidence,
    ReportScope,
    ReportScopeVariable,
    VerificationReport,
)


def build_verification_report(
    task: VerificationTaskIR2,
    route: BackendRoute,
    result: VerificationResult,
    *,
    property_index: int,
    provenance_context: VerificationProvenanceContext | None = None,
) -> VerificationReport:
    """Combine an IR2 task, routing decision and backend result into a report."""

    if result.backend is not route.backend:
        raise ValueError(
            "Backend result does not match the selected route: "
            f"result={result.backend.value}, route={route.backend.value}"
        )

    assignments = _build_assignments(
        result.assignments,
        result.metadata.get("assignment_symbol_mapping"),
    )

    return VerificationReport(
        property_index=property_index,
        property_type=task.property_type,
        semantics=task.semantics,
        scope=_build_scope(task),
        specification=_format_specification(task.spec_formula),
        backend=result.backend,
        backend_status=result.backend_status,
        status=result.status,
        summary=_build_summary(route, result),
        assignments=assignments,
        diagnostics=result.diagnostics,
        assumption_count=len(task.assumptions),
        route_reason=route.reason,
        points=_build_point_evidence(task, assignments),
        numeric_compatibility=_build_numeric_compatibility(route),
        backend_execution=_build_backend_execution(result),
        provenance=(
            build_report_provenance(
                provenance_context,
                task=task,
                route=route,
                result=result,
                property_index=property_index,
            )
            if provenance_context is not None
            else None
        ),
    )


def _build_backend_execution(
    result: VerificationResult,
) -> ReportBackendExecution | None:
    execution = result.execution
    if execution is None:
        return None
    policy = execution.policy
    return ReportBackendExecution(
        status=execution.status.value,
        duration_ms=execution.duration_ms,
        reason=execution.reason,
        backend_reason=execution.backend_reason,
        timeout_ms=policy.timeout_ms,
        max_backend_units=policy.max_backend_units,
        max_memory_mb=policy.max_memory_mb,
        deterministic_seed=policy.deterministic_seed,
        backend_options=policy.backend_options,
    )


def _build_summary(route: BackendRoute, result: VerificationResult) -> str:
    assessment = route.numeric_compatibility
    if assessment is None or result.status.value == "unknown":
        return result.message
    if assessment.conclusion_scope.value != "semantic_target_only":
        return result.message

    boundary = (
        "This conclusion applies only to the declared semantic target "
        f"'{assessment.semantic_target}', not automatically to concrete source "
        "execution."
    )
    return f"{result.message} {boundary}".strip()


def _build_numeric_compatibility(
    route: BackendRoute,
) -> ReportNumericCompatibility | None:
    assessment = route.numeric_compatibility
    if assessment is None:
        return None

    query = assessment.query
    return ReportNumericCompatibility(
        matched_rule_id=assessment.matched_rule_id,
        support_status=assessment.support_status.value,
        classification=assessment.classification.value,
        semantic_target=assessment.semantic_target,
        conclusion_scope=assessment.conclusion_scope.value,
        evidence_id=assessment.evidence_id,
        framework_adapter_id=query.framework_adapter_id,
        framework_version=query.framework_version,
        model_family=query.model_family,
        source_execution_profile_id=query.source_execution_profile_id,
        model_encoder_id=query.model_encoder_id,
        model_encoder_version=query.model_encoder_version,
        backend_kind=query.backend_kind,
        backend_adapter_id=query.backend_adapter_id,
        backend_profile_id=query.backend_profile_id,
        backend_version=query.backend_version,
        property_numeric_requirements=tuple(
            sorted(query.property_numeric_requirements.tags)
        ),
        permitted_conclusions=tuple(
            sorted(item.value for item in assessment.permitted_conclusions)
        ),
        replay_required_for=tuple(
            sorted(item.value for item in assessment.replay_required_for)
        ),
        assumptions_and_preconditions=assessment.assumptions_and_preconditions,
        compatibility_diagnostics=assessment.diagnostics,
        documentation_reference=assessment.documentation_reference,
    )


def _build_scope(task: VerificationTaskIR2) -> ReportScope:
    return ReportScope(
        kind=task.scope.kind,
        quantifier=task.scope.quantifier,
        variables=tuple(
            ReportScopeVariable(name=name, role=role)
            for name, role in task.scope.variables.items()
        ),
    )


def _build_assignments(
    assignments: Mapping[str, Any] | None,
    symbol_mapping: object = None,
) -> tuple[ReportAssignment, ...]:
    if not assignments:
        return ()

    mapping = symbol_mapping if isinstance(symbol_mapping, Mapping) else {}
    model_output_count = sum(
        isinstance(item, Mapping)
        and isinstance(item.get("identity"), Mapping)
        and item["identity"].get("kind") == "model_output"
        for item in mapping.values()
    )
    return tuple(
        _build_assignment(
            name, value, mapping.get(name), model_output_count=model_output_count
        )
        for name, value in sorted(assignments.items())
    )


def _build_assignment(
    name: str,
    value: Any,
    symbol: object = None,
    *,
    model_output_count: int = 0,
) -> ReportAssignment:
    identity: Mapping[str, Any] = {}
    if isinstance(symbol, Mapping):
        raw_identity = symbol.get("identity")
        if isinstance(raw_identity, Mapping):
            identity = raw_identity

    kind = identity.get("kind")
    point = identity.get("point")
    point_name = point.get("name") if isinstance(point, Mapping) else None
    binding_kind = point.get("binding_kind") if isinstance(point, Mapping) else None

    if kind == "model_output":
        target_name = str(identity.get("target", name.removeprefix("_model.")))
        display_name = (
            f"{target_name}[{point_name}]"
            if point_name is not None and model_output_count > 1
            else target_name
        )
        return ReportAssignment(
            raw_name=name,
            display_name=display_name,
            value=value,
            kind=ReportAssignmentKind.OUTPUT,
            point_name=point_name,
            binding_kind=str(binding_kind) if binding_kind is not None else None,
            model_identity=(
                str(identity.get("model_identity"))
                if identity.get("model_identity") is not None
                else None
            ),
            target_name=target_name,
        )

    if kind == "point_feature":
        feature = str(identity.get("feature", name.split(".", 1)[-1]))
        display_name = f"{point_name}.{feature}" if point_name else name
        return ReportAssignment(
            raw_name=name,
            display_name=display_name,
            value=value,
            kind=ReportAssignmentKind.INPUT,
            point_name=point_name,
            binding_kind=str(binding_kind) if binding_kind is not None else None,
        )

    if name.startswith("_model."):
        return ReportAssignment(
            raw_name=name,
            display_name=name.removeprefix("_model."),
            value=value,
            kind=ReportAssignmentKind.OUTPUT,
        )

    if "." in name:
        point_name, _feature = name.split(".", 1)
        return ReportAssignment(
            raw_name=name,
            display_name=name,
            value=value,
            kind=ReportAssignmentKind.INPUT,
            point_name=point_name,
        )

    return ReportAssignment(
        raw_name=name,
        display_name=name,
        value=value,
        kind=ReportAssignmentKind.AUXILIARY,
    )


def _build_point_evidence(
    task: VerificationTaskIR2,
    assignments: tuple[ReportAssignment, ...],
) -> tuple[ReportPointEvidence, ...]:
    evidence: list[ReportPointEvidence] = []
    for mapping in task.point_mappings:
        point = mapping.ir_point
        point_inputs = tuple(
            item
            for item in assignments
            if item.kind is ReportAssignmentKind.INPUT and item.point_name == point.name
        )
        point_outputs = tuple(
            item
            for item in assignments
            if item.kind is ReportAssignmentKind.OUTPUT
            and item.point_name == point.name
        )
        evidence.append(
            ReportPointEvidence(
                name=point.name,
                binding_kind=point.binding_kind,
                inputs=point_inputs,
                outputs=point_outputs,
                provenance=_point_provenance(point),
            )
        )
    return tuple(evidence)


def _point_provenance(point: object) -> dict[str, Any] | None:
    resolution = getattr(point, "resolution", None)
    if resolution is not None:
        return {
            "kind": "referenced_anchor",
            "key": resolution.key,
            "lookup_value": resolution.lookup_value.value,
            "source_kind": resolution.source_kind,
            "source_reference": resolution.source_reference,
            "row_index": resolution.row_index,
        }
    concrete_values = getattr(point, "concrete_values", ())
    if concrete_values:
        source_span = getattr(point, "source_span", None)
        return {
            "kind": "inline_anchor",
            "source_span": (
                {
                    "line": source_span.line,
                    "column": source_span.column,
                    "end_line": source_span.end_line,
                    "end_column": source_span.end_column,
                }
                if source_span is not None
                else None
            ),
        }
    return None


def _format_specification(formula: NNFFormulaIR2) -> str:
    return _format_logical(formula.expression)


def _format_logical(node: LogicalIR) -> str:
    if isinstance(node, ComparisonIR):
        left = format_scalar_expression(node.left)
        right = format_scalar_expression(node.right)
        return f"{left} {node.op.value} {right}"

    if isinstance(node, ProblemIR):
        function = getattr(node.function, "value", node.function)
        return f"{node.problem.value}.{function}({node.args or {}})"

    if isinstance(node, NotIR):
        return f"not ({_format_logical(node.operand)})"

    if isinstance(node, AndIR):
        return _join_logical("and", node.operands)

    if isinstance(node, OrIR):
        return _join_logical("or", node.operands)

    if isinstance(node, AtomicIR):
        return repr(node)

    raise TypeError(f"Unsupported report specification node: {type(node).__name__}")


def _join_logical(operator: str, operands: list[LogicalIR]) -> str:
    return f" {operator} ".join(f"({_format_logical(item)})" for item in operands)
