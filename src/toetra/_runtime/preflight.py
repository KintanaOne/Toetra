"""Shared pre-execution planning for validation, inspection, and verification."""

from __future__ import annotations

import json
import platform
import sys
from dataclasses import dataclass, field
from importlib.metadata import PackageNotFoundError, version
from enum import Enum
from pathlib import Path
from typing import Any, Mapping, Sequence

from toetra._backends.base import BackendRunner
from toetra._backends.defaults import create_default_backend_registry
from toetra._backends.errors import (
    BackendExecutionPolicyError,
    BackendRoutingError,
    BackendTranslationError,
)
from toetra._backends.execution import BackendExecutionPolicy
from toetra._backends.registry import BackendRegistry
from toetra._backends.router import BackendRoute
from toetra._compatibility.errors import NumericCompatibilityError
from toetra._compatibility.model import NumericCompatibilityContext
from toetra._compatibility.registry import NumericCompatibilityRegistry
from toetra._compiler.ast.nodes.anchors import (
    AnchorReferenceBindingNode,
    InlineAnchorBindingNode,
)
from toetra._compiler.ast.nodes.primitives import PrimitiveValue
from toetra._compiler.ast.nodes.program import ProgramNode
from toetra._compiler.builder.errors import BuilderError
from toetra._compiler.ir.ir1.run_ir1 import run_ir_from_program
from toetra._compiler.ir.ir2.context import IR2BuildContext
from toetra._compiler.ir.ir2.dsl.nodes import VerificationTaskIR2
from toetra._compiler.ir.ir2.enums import NormalFormKind
from toetra._compiler.parser.errors import ParserError
from toetra._compiler.semantic.errors.errors import SemanticError
from toetra._compiler.semantic.symbols.point import ResolvedAnchorBinding
from toetra._models.compatibility import framework_model_descriptor
from toetra._models.encoder.context import ModelEncodingContext
from toetra._models.encoder.errors import ModelEncoderError
from toetra._models.encoder.factory import ModelEncoderFactory
from toetra._models.encoder.profile import model_encoder_descriptor
from toetra._models.schema.model_schema import ModelSchema
from toetra._models.semantics.errors import ModelSemanticLoweringError
from toetra._provenance.builder import build_provenance_context
from toetra._provenance.fingerprint import fingerprint_file
from toetra._provenance.model import (
    ArtifactProvenance,
    FingerprintStatus,
    VerificationProvenanceContext,
)
from toetra._runtime import api as runtime_api
from toetra._runtime.anchors import AnchorResolver, AnchorSource
from toetra._runtime.backends import (
    BackendRunnerRegistry,
    create_default_backend_runner_registry,
)
from toetra._runtime.execution_context import (
    ExecutionContext,
    resolve_execution_context,
)
from toetra._runtime.errors import (
    BackendRunnerNotRegisteredError,
    VerificationConfigurationError,
    VerificationRuntimeError,
)

VALIDATION_SCHEMA = "toetra.validation-result"
VALIDATION_SCHEMA_VERSION = 1
INSPECTION_SCHEMA = "toetra.inspection"
INSPECTION_SCHEMA_VERSION = 1


class ValidationLevel(str, Enum):
    """Supported pre-execution validation depths."""

    SYNTAX = "syntax"
    SEMANTIC = "semantic"
    EXECUTABLE = "executable"


@dataclass(frozen=True)
class ValidationDiagnostic:
    """Stable diagnostic embedded in a completed validation result."""

    category: str
    code: str
    stage: str
    message: str
    hint: str | None = None
    path: str | None = None
    line: int | None = None
    column: int | None = None

    @classmethod
    def from_error(
        cls,
        error: VerificationRuntimeError,
    ) -> ValidationDiagnostic:
        category = (
            "configuration"
            if isinstance(error, VerificationConfigurationError)
            else "runtime"
        )
        return cls(
            category=category,
            code=error.code,
            stage=error.stage,
            message=error.message,
            hint=error.hint,
            path=error.path,
            line=error.line,
            column=error.column,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "category": self.category,
            "code": self.code,
            "stage": self.stage,
            "message": self.message,
            "hint": self.hint,
            "location": {
                "path": self.path,
                "line": self.line,
                "column": self.column,
            },
        }


@dataclass(frozen=True)
class ValidationResult:
    """Completed validation outcome suitable for text or JSON rendering."""

    requested_level: ValidationLevel
    completed_level: ValidationLevel | None
    valid: bool
    checks: tuple[str, ...]
    property_count: int | None = None
    declared_model_reference: str | None = None
    declared_target: str | None = None
    declared_dataset_reference: str | None = None
    effective_model_reference: str | None = None
    effective_target: str | None = None
    effective_dataset_reference: str | None = None
    model_overridden: bool = False
    target_overridden: bool = False
    dataset_overridden: bool = False
    specification_path: Path | None = field(default=None, repr=False)
    model_path: Path | None = field(default=None, repr=False)
    dataset_path: Path | None = field(default=None, repr=False)
    anchor_source_path: Path | None = field(default=None, repr=False)
    diagnostic: ValidationDiagnostic | None = None
    provenance: VerificationProvenanceContext | None = field(
        default=None,
        repr=False,
    )

    @property
    def exit_code(self) -> int:
        if self.valid:
            return 0
        if self.diagnostic is not None and self.diagnostic.category == "configuration":
            return 3
        return 4

    @property
    def consumed_paths(self) -> tuple[Path, ...]:
        return tuple(
            path
            for path in (
                self.specification_path,
                self.model_path,
                self.dataset_path,
                self.anchor_source_path,
            )
            if path is not None
        )

    def to_dict(self) -> dict[str, Any]:
        artifacts = (
            {
                role: _artifact_to_dict(artifact)
                for role, artifact in self.provenance.artifacts.items()
            }
            if self.provenance is not None
            else _validation_artifacts(self)
        )
        software = (
            _software_to_dict(self.provenance)
            if self.provenance is not None
            else _standalone_software_payload()
        )
        return {
            "schema": VALIDATION_SCHEMA,
            "schema_version": VALIDATION_SCHEMA_VERSION,
            "requested_level": self.requested_level.value,
            "completed_level": (
                self.completed_level.value if self.completed_level is not None else None
            ),
            "valid": self.valid,
            "checks": list(self.checks),
            "property_count": self.property_count,
            "declarations": {
                "model": self.declared_model_reference,
                "target": self.declared_target,
                "dataset": self.declared_dataset_reference,
            },
            "effective": {
                "model": self.effective_model_reference,
                "target": self.effective_target,
                "dataset": self.effective_dataset_reference,
            },
            "overrides": {
                "model": self.model_overridden,
                "target": self.target_overridden,
                "dataset": self.dataset_overridden,
            },
            "artifacts": artifacts,
            "diagnostics": (
                [self.diagnostic.to_dict()] if self.diagnostic is not None else []
            ),
            "software": software,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def to_text(self) -> str:
        status = "VALID" if self.valid else "INVALID"
        lines = [f"{status} ({self.requested_level.value})"]
        if self.completed_level is not None:
            lines.append(f"completed level: {self.completed_level.value}")
        if self.property_count is not None:
            lines.append(f"properties: {self.property_count}")
        if self.effective_target is not None:
            lines.append(f"effective target: {self.effective_target}")
            lines.append(f"target overridden: {str(self.target_overridden).lower()}")
        if self.checks:
            lines.append("checks:")
            lines.extend(f"  - {check}" for check in self.checks)
        if self.diagnostic is not None:
            lines.append(
                f"diagnostic: {self.diagnostic.code}: {self.diagnostic.message}"
            )
            if self.diagnostic.hint:
                lines.append(f"hint: {self.diagnostic.hint}")
        return "\n".join(lines)


@dataclass(frozen=True)
class SpecificationConstantSummary:
    """Public normalized description of one specification constant."""

    name: str
    dtype: str
    value: PrimitiveValue

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "dtype": self.dtype,
            "value": self.value,
        }


@dataclass(frozen=True)
class AnchorSummary:
    """Public normalized description of one declared anchor."""

    name: str
    binding_kind: str
    features: tuple[str, ...]
    reference_arguments: tuple[str, ...] = ()
    resolved: bool = False
    source_kind: str | None = None
    source_reference: str | None = None
    row_index: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "binding_kind": self.binding_kind,
            "features": list(self.features),
            "reference_arguments": list(self.reference_arguments),
            "resolved": self.resolved,
            "resolution": (
                {
                    "source_kind": self.source_kind,
                    "source_reference": self.source_reference,
                    "row_index": self.row_index,
                }
                if self.resolved
                else None
            ),
        }


@dataclass(frozen=True)
class PlannedProperty:
    """One translated property in an executable preflight plan."""

    index: int
    task: VerificationTaskIR2 = field(repr=False)
    route: BackendRoute
    runner: BackendRunner = field(repr=False, compare=False)
    translation: object | None = field(repr=False, compare=False)


@dataclass(frozen=True)
class ExecutablePlan:
    """Complete plan built before solver execution begins."""

    source: str = field(repr=False)
    specification_path: Path | None
    execution_context: ExecutionContext
    schema: ModelSchema
    model: object | None = field(repr=False, compare=False)
    model_path: Path | None
    dataset_path: Path | None
    anchor_source_path: Path | None
    anchor_resolutions: Mapping[str, ResolvedAnchorBinding] = field(
        repr=False,
        compare=False,
    )
    constants: tuple[SpecificationConstantSummary, ...]
    anchors: tuple[AnchorSummary, ...]
    execution_policy: BackendExecutionPolicy
    provenance: VerificationProvenanceContext
    properties: tuple[PlannedProperty, ...]

    @property
    def declared_model_reference(self) -> str:
        return self.execution_context.declared_model_reference

    @property
    def declared_target(self) -> str:
        return self.execution_context.declared_target

    @property
    def declared_dataset_reference(self) -> str | None:
        return self.execution_context.declared_dataset_reference

    @property
    def effective_model_reference(self) -> str:
        return self.execution_context.effective_model_reference

    @property
    def effective_target(self) -> str:
        return self.execution_context.effective_target

    @property
    def effective_dataset_reference(self) -> str | None:
        return self.execution_context.effective_dataset_reference

    @property
    def model_overridden(self) -> bool:
        return self.execution_context.model_overridden

    @property
    def target_overridden(self) -> bool:
        return self.execution_context.target_overridden

    @property
    def dataset_overridden(self) -> bool:
        return self.execution_context.dataset_overridden

    @property
    def consumed_paths(self) -> tuple[Path, ...]:
        return tuple(
            path
            for path in (
                self.specification_path,
                self.model_path,
                self.dataset_path,
                self.anchor_source_path,
            )
            if path is not None
        )


@dataclass(frozen=True)
class InspectionResult:
    """Public normalized description of one executable verification plan."""

    plan: ExecutablePlan = field(repr=False)

    @property
    def consumed_paths(self) -> tuple[Path, ...]:
        return self.plan.consumed_paths

    def to_dict(self) -> dict[str, Any]:
        plan = self.plan
        schema = plan.schema
        output = schema.output_schema
        fallback_observables = tuple(
            observable.value for observable in output.available_observables
        )
        properties = [
            _property_to_dict(
                item,
                fallback_observables=fallback_observables,
            )
            for item in plan.properties
        ]
        return {
            "schema": INSPECTION_SCHEMA,
            "schema_version": INSPECTION_SCHEMA_VERSION,
            "specification": {
                "path": (
                    str(plan.specification_path)
                    if plan.specification_path is not None
                    else None
                ),
                "declarations": {
                    "model": plan.declared_model_reference,
                    "target": plan.declared_target,
                    "dataset": plan.declared_dataset_reference,
                },
                "effective": {
                    "model": plan.effective_model_reference,
                    "target": plan.effective_target,
                    "dataset": plan.effective_dataset_reference,
                },
                "overrides": {
                    "model": plan.model_overridden,
                    "target": plan.target_overridden,
                    "dataset": plan.dataset_overridden,
                },
                "target": schema.output_name,
                "property_count": len(properties),
                "constant_count": len(plan.constants),
                "constants": [item.to_dict() for item in plan.constants],
                "anchor_count": len(plan.anchors),
                "anchors": [item.to_dict() for item in plan.anchors],
                "fingerprint": _artifact_fingerprint_identifier(
                    plan.provenance.artifacts["specification"]
                ),
            },
            "model": {
                "declared_reference": plan.declared_model_reference,
                "effective_reference": plan.effective_model_reference,
                "path": str(plan.model_path) if plan.model_path is not None else None,
                "overridden": plan.model_overridden,
                "framework": schema.framework.value,
                "family": schema.model_type,
                "task": schema.task,
                "features": [
                    {
                        "name": feature.name,
                        "dtype": feature.dtype.value,
                        "nullable": feature.nullable,
                        "source_dtype": feature.source_dtype,
                    }
                    for feature in schema.features.values()
                ],
                "output": {
                    "declared_name": plan.declared_target,
                    "name": schema.output_name,
                    "overridden": plan.target_overridden,
                    "kind": output.kind.value,
                    "dtype": (
                        output.primary_dtype.value
                        if output.primary_dtype is not None
                        else None
                    ),
                    "source_dtype": output.source_dtype,
                    "observables": [
                        observable.value for observable in output.available_observables
                    ],
                },
                "dataset": {
                    "declared_reference": plan.declared_dataset_reference,
                    "effective_reference": plan.effective_dataset_reference,
                    "path": (
                        str(plan.dataset_path)
                        if plan.dataset_path is not None
                        else None
                    ),
                    "overridden": plan.dataset_overridden,
                    "provided": plan.dataset_path is not None,
                },
            },
            "properties": properties,
            "execution": {
                "policy": _execution_policy_to_dict(plan.execution_policy),
                "backend_count": len({item.route.backend for item in plan.properties}),
                "translated_property_count": sum(
                    item.translation is not None for item in plan.properties
                ),
                "translation_ready": all(
                    item.translation is not None for item in plan.properties
                ),
            },
            "provenance": {
                "captured_at_utc": plan.provenance.captured_at_utc,
                "completeness": plan.provenance.completeness.value,
                "unavailable_inputs": list(plan.provenance.unavailable_inputs),
                "input_fingerprint": plan.provenance.input_fingerprint,
                "artifacts": {
                    role: _artifact_to_dict(artifact)
                    for role, artifact in plan.provenance.artifacts.items()
                },
                "execution_context": plan.provenance.execution_context.to_dict(),
                "compiler_policy": {
                    "preferred_normal_form": (plan.provenance.preferred_normal_form),
                    "max_distribution_size": (plan.provenance.max_distribution_size),
                    "allow_nnf_fallback": plan.provenance.allow_nnf_fallback,
                    "backend_hint": plan.provenance.backend_hint,
                    "strict": plan.provenance.strict,
                },
            },
            "software": _software_to_dict(plan.provenance),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def to_text(self) -> str:
        payload = self.to_dict()
        model = payload["model"]
        execution = payload["execution"]
        dataset = model["dataset"]
        lines = [
            "EXECUTABLE PLAN",
            f"specification: {payload['specification']['path'] or '<inline>'}",
            f"target: {payload['specification']['target']}",
            (
                "target overridden: "
                f"{str(payload['specification']['overrides']['target']).lower()}"
            ),
            f"properties: {payload['specification']['property_count']}",
            ("model: " f"{model['framework']} / {model['family']} / {model['task']}"),
            f"model path: {model['path'] or '<schema-only>'}",
            f"model overridden: {str(model['overridden']).lower()}",
            f"dataset: {dataset['path'] or '<not provided>'}",
            f"dataset overridden: {str(dataset['overridden']).lower()}",
            f"translation ready: {str(execution['translation_ready']).lower()}",
            "routes:",
        ]
        for item in payload["properties"]:
            lines.append(
                "  - "
                f"[{item['index']}] {item['type']} -> {item['backend']} "
                f"({item['numeric_compatibility']['classification']})"
            )
        return "\n".join(lines)


def validate_request(
    specification: str | Path,
    *,
    level: ValidationLevel | str = ValidationLevel.EXECUTABLE,
    model: str | Path | None = None,
    dataset: str | Path | None = None,
    target: str | None = None,
    anchor_source: AnchorSource | None = None,
    anchor_resolver: AnchorResolver | None = None,
    execution_policy: BackendExecutionPolicy | None = None,
    model_context: ModelEncodingContext | None = None,
    model_encoder_factory: ModelEncoderFactory | None = None,
    ir2_context: IR2BuildContext | None = None,
    backend_registry: BackendRegistry | None = None,
    numeric_compatibility_registry: NumericCompatibilityRegistry | None = None,
    runner_registry: BackendRunnerRegistry | None = None,
) -> ValidationResult:
    """Validate a request at one documented pre-execution boundary."""

    requested = ValidationLevel(level)
    checks: list[str] = []
    completed: ValidationLevel | None = None
    specification_path = _input_specification_path(specification)
    model_path = _optional_resolved_path(model)
    dataset_path = _optional_resolved_path(dataset)
    anchor_source_path = _path_from_source(anchor_source)
    declared_model_reference: str | None = None
    declared_target: str | None = None
    declared_dataset_reference: str | None = None
    effective_model_reference: str | None = None
    effective_target: str | None = None
    effective_dataset_reference: str | None = None
    try:
        loaded = _load_specification(specification)
        declared_model_reference = loaded.model_reference
        declared_target = loaded.target
        declared_dataset_reference = loaded.dataset_reference
        syntax_context = resolve_execution_context(
            declared_model_reference=loaded.model_reference,
            declared_target=loaded.target,
            declared_dataset_reference=loaded.dataset_reference,
            model=model,
            target=target,
            dataset=dataset,
        )
        effective_model_reference = syntax_context.effective_model_reference
        effective_target = syntax_context.effective_target
        effective_dataset_reference = syntax_context.effective_dataset_reference
        checks.extend(("source_loaded", "syntax_parsed", "ast_built"))
        completed = ValidationLevel.SYNTAX
        if requested is ValidationLevel.SYNTAX:
            return ValidationResult(
                requested_level=requested,
                completed_level=completed,
                valid=True,
                checks=tuple(checks),
                property_count=len(loaded.program.body),
                declared_model_reference=declared_model_reference,
                declared_target=declared_target,
                declared_dataset_reference=declared_dataset_reference,
                effective_model_reference=effective_model_reference,
                effective_target=effective_target,
                effective_dataset_reference=effective_dataset_reference,
                model_overridden=model is not None,
                target_overridden=target is not None,
                dataset_overridden=dataset is not None,
                specification_path=loaded.path,
                anchor_source_path=anchor_source_path,
            )

        if model is None:
            model_path = runtime_api._resolve_header_model_path(loaded).resolve()
        if dataset is None:
            header_dataset = runtime_api._resolve_header_dataset_path(loaded)
            dataset_path = (
                header_dataset.resolve() if header_dataset is not None else None
            )

        resolved = runtime_api._resolve_model(
            loaded,
            model=model,
            dataset=dataset,
            target=target,
            schema=None,
        )
        anchors = runtime_api._resolve_anchor_bindings(
            resolved.program,
            schema=resolved.schema,
            anchor_source=anchor_source,
            anchor_resolver=anchor_resolver,
            dataset_fallback=resolved.dataset_path,
        )
        _run_semantic_ir1(
            resolved.program,
            schema=resolved.schema,
            resolved_anchors=anchors,
            specification=specification,
        )
        checks.extend(
            (
                "model_resolved",
                "target_validated",
                "anchors_resolved",
                "semantic_validated",
                "ir1_built",
            )
        )
        completed = ValidationLevel.SEMANTIC
        if requested is ValidationLevel.SEMANTIC:
            return ValidationResult(
                requested_level=requested,
                completed_level=completed,
                valid=True,
                checks=tuple(checks),
                property_count=len(loaded.program.body),
                declared_model_reference=declared_model_reference,
                declared_target=declared_target,
                declared_dataset_reference=declared_dataset_reference,
                effective_model_reference=(
                    resolved.execution_context.effective_model_reference
                ),
                effective_target=resolved.execution_context.effective_target,
                effective_dataset_reference=(
                    resolved.execution_context.effective_dataset_reference
                ),
                model_overridden=resolved.execution_context.model_overridden,
                target_overridden=resolved.execution_context.target_overridden,
                dataset_overridden=resolved.execution_context.dataset_overridden,
                specification_path=loaded.path,
                model_path=resolved.model_path,
                dataset_path=resolved.dataset_path,
                anchor_source_path=anchor_source_path,
            )

        plan = _build_executable_plan_from_resolved(
            loaded,
            resolved,
            anchors=anchors,
            anchor_source=anchor_source,
            anchor_resolver=anchor_resolver,
            execution_policy=execution_policy,
            model_context=model_context,
            model_encoder_factory=model_encoder_factory,
            ir2_context=ir2_context,
            backend_registry=backend_registry,
            numeric_compatibility_registry=numeric_compatibility_registry,
            runner_registry=runner_registry,
            require_translation=True,
        )
        checks.extend(
            (
                "model_semantics_lowered",
                "model_encoded",
                "ir2_built",
                "numeric_compatibility_validated",
                "backend_routed",
                "runner_resolved",
                "backend_translated",
            )
        )
        completed = ValidationLevel.EXECUTABLE
        return ValidationResult(
            requested_level=requested,
            completed_level=completed,
            valid=True,
            checks=tuple(checks),
            property_count=len(plan.properties),
            declared_model_reference=plan.declared_model_reference,
            declared_target=plan.declared_target,
            declared_dataset_reference=plan.declared_dataset_reference,
            effective_model_reference=plan.effective_model_reference,
            effective_target=plan.effective_target,
            effective_dataset_reference=plan.effective_dataset_reference,
            model_overridden=plan.model_overridden,
            target_overridden=plan.target_overridden,
            dataset_overridden=plan.dataset_overridden,
            specification_path=plan.specification_path,
            model_path=plan.model_path,
            dataset_path=plan.dataset_path,
            anchor_source_path=plan.anchor_source_path,
            provenance=plan.provenance,
        )
    except VerificationRuntimeError as error:
        return ValidationResult(
            requested_level=requested,
            completed_level=completed,
            valid=False,
            checks=tuple(checks),
            property_count=None,
            declared_model_reference=declared_model_reference,
            declared_target=declared_target,
            declared_dataset_reference=declared_dataset_reference,
            effective_model_reference=effective_model_reference,
            effective_target=effective_target,
            effective_dataset_reference=effective_dataset_reference,
            model_overridden=model is not None,
            target_overridden=target is not None,
            dataset_overridden=dataset is not None,
            specification_path=(
                specification_path.resolve()
                if specification_path is not None and specification_path.exists()
                else specification_path
            ),
            model_path=model_path,
            dataset_path=dataset_path,
            anchor_source_path=anchor_source_path,
            diagnostic=ValidationDiagnostic.from_error(error),
        )


def inspect_request(
    specification: str | Path,
    *,
    model: str | Path | None = None,
    dataset: str | Path | None = None,
    target: str | None = None,
    anchor_source: AnchorSource | None = None,
    anchor_resolver: AnchorResolver | None = None,
    execution_policy: BackendExecutionPolicy | None = None,
    model_context: ModelEncodingContext | None = None,
    model_encoder_factory: ModelEncoderFactory | None = None,
    ir2_context: IR2BuildContext | None = None,
    backend_registry: BackendRegistry | None = None,
    numeric_compatibility_registry: NumericCompatibilityRegistry | None = None,
    runner_registry: BackendRunnerRegistry | None = None,
) -> InspectionResult:
    """Build and describe a complete executable plan without solving."""

    loaded = _load_specification(specification)
    resolved = runtime_api._resolve_model(
        loaded,
        model=model,
        dataset=dataset,
        target=target,
        schema=None,
    )
    anchors = runtime_api._resolve_anchor_bindings(
        resolved.program,
        schema=resolved.schema,
        anchor_source=anchor_source,
        anchor_resolver=anchor_resolver,
        dataset_fallback=resolved.dataset_path,
    )
    plan = _build_executable_plan_from_resolved(
        loaded,
        resolved,
        anchors=anchors,
        anchor_source=anchor_source,
        anchor_resolver=anchor_resolver,
        execution_policy=execution_policy,
        model_context=model_context,
        model_encoder_factory=model_encoder_factory,
        ir2_context=ir2_context,
        backend_registry=backend_registry,
        numeric_compatibility_registry=numeric_compatibility_registry,
        runner_registry=runner_registry,
        require_translation=True,
    )
    return InspectionResult(plan=plan)


def build_executable_plan(
    specification: str | Path,
    *,
    model: str | Path | None = None,
    dataset: str | Path | None = None,
    target: str | None = None,
    schema: ModelSchema | None = None,
    anchor_source: AnchorSource | None = None,
    anchor_resolver: AnchorResolver | None = None,
    execution_policy: BackendExecutionPolicy | None = None,
    model_context: ModelEncodingContext | None = None,
    model_encoder_factory: ModelEncoderFactory | None = None,
    ir2_context: IR2BuildContext | None = None,
    backend_registry: BackendRegistry | None = None,
    numeric_compatibility_registry: NumericCompatibilityRegistry | None = None,
    runner_registry: BackendRunnerRegistry | None = None,
    require_translation: bool = True,
    execution_context: ExecutionContext | None = None,
) -> ExecutablePlan:
    """Build one routed plan, optionally translating without solver execution."""

    loaded = _load_specification(specification)
    resolved = runtime_api._resolve_model(
        loaded,
        model=model,
        dataset=dataset,
        target=target,
        schema=schema,
        execution_context=execution_context,
    )
    anchors = runtime_api._resolve_anchor_bindings(
        resolved.program,
        schema=resolved.schema,
        anchor_source=anchor_source,
        anchor_resolver=anchor_resolver,
        dataset_fallback=resolved.dataset_path,
    )
    return _build_executable_plan_from_resolved(
        loaded,
        resolved,
        anchors=anchors,
        anchor_source=anchor_source,
        anchor_resolver=anchor_resolver,
        execution_policy=execution_policy,
        model_context=model_context,
        model_encoder_factory=model_encoder_factory,
        ir2_context=ir2_context,
        backend_registry=backend_registry,
        numeric_compatibility_registry=numeric_compatibility_registry,
        runner_registry=runner_registry,
        require_translation=require_translation,
    )


def _build_executable_plan_from_resolved(
    loaded: Any,
    resolved: Any,
    *,
    anchors: Mapping[str, ResolvedAnchorBinding],
    anchor_source: AnchorSource | None,
    anchor_resolver: AnchorResolver | None,
    execution_policy: BackendExecutionPolicy | None,
    model_context: ModelEncodingContext | None,
    model_encoder_factory: ModelEncoderFactory | None,
    ir2_context: IR2BuildContext | None,
    backend_registry: BackendRegistry | None,
    numeric_compatibility_registry: NumericCompatibilityRegistry | None,
    runner_registry: BackendRunnerRegistry | None,
    require_translation: bool,
) -> ExecutablePlan:
    context = ir2_context or IR2BuildContext(preferred_normal_form=NormalFormKind.NNF)
    encoder_factory = model_encoder_factory or ModelEncoderFactory()
    try:
        selected_encoder = encoder_factory.create(resolved.schema)
        compatibility_context = NumericCompatibilityContext(
            source_model=framework_model_descriptor(resolved.schema),
            model_encoder=model_encoder_descriptor(selected_encoder),
        )
        tasks = runtime_api.run_ir2_with_model_schema(
            loaded.source,
            schema=resolved.schema,
            model_context=model_context,
            ir2_context=context,
            encoder_factory=encoder_factory,
            resolved_anchors=anchors,
            program=resolved.program,
        )
    except (ParserError, BuilderError, SemanticError) as error:
        raise _compiler_error(error, specification=loaded.path) from error
    except ModelEncoderError as error:
        raise runtime_api._public_model_encoder_error(
            error,
            model_path=resolved.model_path,
        ) from error
    except ModelSemanticLoweringError as error:
        raise runtime_api._public_model_semantic_error(
            error,
            model_path=resolved.model_path,
        ) from error
    except NumericCompatibilityError as error:
        raise runtime_api._public_numeric_compatibility_error(
            error,
            model_path=resolved.model_path,
        ) from error

    router = runtime_api.BackendRouter(
        backend_registry or create_default_backend_registry(),
        numeric_compatibility_registry=numeric_compatibility_registry,
    )
    runners = runner_registry or create_default_backend_runner_registry()
    policy = execution_policy or BackendExecutionPolicy()
    provenance = build_provenance_context(
        specification_source=loaded.source,
        specification_path=loaded.path,
        model_path=resolved.model_path,
        dataset_path=resolved.dataset_path,
        anchor_source=anchor_source,
        anchor_resolver=anchor_resolver,
        anchors_used=bool(anchors),
        schema=resolved.schema,
        ir2_context=context,
        execution_context=resolved.execution_context,
    )

    planned: list[PlannedProperty] = []
    for index, task in enumerate(tasks):
        try:
            route = router.route(
                task,
                numeric_compatibility_context=compatibility_context,
                execution_policy=policy,
            )
        except NumericCompatibilityError as error:
            raise runtime_api._public_numeric_compatibility_error(
                error,
                model_path=resolved.model_path,
            ) from error
        except BackendRoutingError as error:
            raise runtime_api._public_backend_routing_error(
                error,
                model_path=resolved.model_path,
            ) from error
        try:
            runner = runners.require(route.backend)
            translation = (
                _translate_without_solving(runner, task)
                if require_translation
                else None
            )
        except BackendRunnerNotRegisteredError as error:
            raise runtime_api._public_backend_runner_error(error) from error
        except BackendExecutionPolicyError as error:
            raise runtime_api._public_backend_policy_error(error) from error
        except BackendTranslationError as error:
            raise runtime_api._public_backend_translation_error(error) from error
        planned.append(
            PlannedProperty(
                index=index,
                task=task,
                route=route,
                runner=runner,
                translation=translation,
            )
        )

    return ExecutablePlan(
        source=loaded.source,
        specification_path=loaded.path,
        execution_context=resolved.execution_context,
        schema=resolved.schema,
        model=resolved.model,
        model_path=resolved.model_path,
        dataset_path=resolved.dataset_path,
        anchor_source_path=_path_from_source(anchor_source),
        anchor_resolutions=anchors,
        execution_policy=policy,
        constants=_constant_summaries(loaded),
        anchors=_anchor_summaries(loaded, resolved_anchors=anchors),
        provenance=provenance,
        properties=tuple(planned),
    )


def _translate_without_solving(
    runner: BackendRunner,
    task: VerificationTaskIR2,
) -> object:
    translate = getattr(runner, "translate", None)
    if not callable(translate):
        raise VerificationRuntimeError(
            "The selected backend runner does not expose pre-execution translation.",
            code="BACKEND_TRANSLATION_PREFLIGHT_UNAVAILABLE",
            stage="backend",
            hint=(
                "Use a backend integration that supports executable validation "
                "and inspection without invoking its solver."
            ),
        )
    return translate(task)


def _load_specification(specification: str | Path) -> Any:
    try:
        return runtime_api._load_specification(specification)
    except (ParserError, BuilderError, SemanticError) as error:
        raise _compiler_error(error, specification=specification) from error


def _run_semantic_ir1(
    program: ProgramNode,
    *,
    schema: ModelSchema,
    resolved_anchors: Mapping[str, ResolvedAnchorBinding],
    specification: str | Path,
) -> Sequence[object]:
    try:
        return run_ir_from_program(
            program,
            model_schema=schema,
            resolved_anchors=resolved_anchors,
        )
    except (ParserError, BuilderError, SemanticError) as error:
        raise _compiler_error(error, specification=specification) from error


def _compiler_error(
    error: ParserError | BuilderError | SemanticError,
    *,
    specification: str | Path | None,
) -> VerificationConfigurationError:
    if isinstance(error, ParserError):
        stage = "syntax"
    elif isinstance(error, BuilderError):
        stage = "builder"
    else:
        stage = "semantic"
    return runtime_api._public_compiler_error(
        error,
        stage=stage,
        path=(
            runtime_api._diagnostic_specification_path(specification)
            if specification is not None
            else None
        ),
    )


def _property_to_dict(
    item: PlannedProperty,
    *,
    fallback_observables: tuple[str, ...],
) -> dict[str, Any]:
    task = item.task
    route = item.route
    requirements = task.requirements
    compatibility = route.numeric_compatibility
    return {
        "index": item.index,
        "type": task.property_type.value,
        "semantics": task.semantics.value,
        "normal_form": task.normal_form.value,
        "requested_backend": task.backend.value if task.backend is not None else None,
        "backend": route.backend.value,
        "route_reason": _public_route_reason(route.reason),
        "requested_observables": _requested_observables(
            task,
            fallback_observables=fallback_observables,
        ),
        "requirements": {
            "tags": sorted(_requirement_tags(requirements)),
            "point_count": requirements.point_count,
            "anchor_count": requirements.anchor_count,
            "model_evaluation_count": requirements.model_evaluation_count,
            "binder_sequence": list(requirements.binder_sequence),
            "alternation_depth": requirements.alternation_depth,
        },
        "numeric_compatibility": {
            "support_status": (
                compatibility.support_status.value
                if compatibility is not None
                else "not_assessed"
            ),
            "classification": (
                compatibility.classification.value
                if compatibility is not None
                else "not_assessed"
            ),
            "semantic_target": (
                compatibility.semantic_target if compatibility is not None else None
            ),
            "conclusion_scope": (
                compatibility.conclusion_scope.value
                if compatibility is not None
                else None
            ),
            "matched_rule_id": (
                compatibility.matched_rule_id if compatibility is not None else None
            ),
            "evidence_id": (
                compatibility.evidence_id if compatibility is not None else None
            ),
            "summary": compatibility.summary if compatibility is not None else None,
        },
        "backend_runner_available": True,
        "execution_policy_compatible": True,
        "translation_ready": item.translation is not None,
    }


def _requested_observables(
    task: VerificationTaskIR2,
    *,
    fallback_observables: tuple[str, ...],
) -> list[str]:
    observables: set[str] = set()
    for evidence in task.lowering_evidence:
        source_intent = evidence.source_intent
        observables.add(source_intent.observable.value)
        related = getattr(source_intent, "related_observable", None)
        if related is not None:
            observables.add(related.value)
    if not observables and task.model_evaluations and len(fallback_observables) == 1:
        observables.add(fallback_observables[0])
    return sorted(observables)


def _constant_summaries(loaded: Any) -> tuple[SpecificationConstantSummary, ...]:
    return tuple(
        SpecificationConstantSummary(
            name=declaration.name,
            dtype=declaration.value.dtype.value,
            value=declaration.value.value,
        )
        for declaration in loaded.program.header.specification_constants
    )


def _anchor_summaries(
    loaded: Any,
    *,
    resolved_anchors: Mapping[str, ResolvedAnchorBinding],
) -> tuple[AnchorSummary, ...]:
    summaries: list[AnchorSummary] = []
    for declaration in loaded.program.anchors:
        binding = declaration.binding
        resolution = resolved_anchors.get(declaration.name)
        if isinstance(binding, InlineAnchorBindingNode):
            summaries.append(
                AnchorSummary(
                    name=declaration.name,
                    binding_kind="inline",
                    features=tuple(entry.feature for entry in binding.entries),
                )
            )
            continue
        if isinstance(binding, AnchorReferenceBindingNode):
            provenance = resolution.provenance if resolution is not None else None
            summaries.append(
                AnchorSummary(
                    name=declaration.name,
                    binding_kind="reference",
                    features=(
                        tuple(resolution.concrete_values)
                        if resolution is not None
                        else ()
                    ),
                    reference_arguments=tuple(
                        argument.name for argument in binding.arguments
                    ),
                    resolved=resolution is not None,
                    source_kind=(
                        provenance.source_kind if provenance is not None else None
                    ),
                    source_reference=(
                        provenance.source_reference if provenance is not None else None
                    ),
                    row_index=(
                        provenance.row_index if provenance is not None else None
                    ),
                )
            )
            continue
        raise TypeError(
            "Unsupported anchor binding while building inspection: "
            f"{type(binding).__name__}"
        )
    return tuple(summaries)


def _public_route_reason(reason: str) -> str:
    return reason.replace("IR2 requirements", "property requirements")


def _artifact_fingerprint_identifier(artifact: ArtifactProvenance) -> str | None:
    fingerprint = artifact.fingerprint
    return fingerprint.identifier if fingerprint is not None else None


def _requirement_tags(requirements: Any) -> set[str]:
    flags = {
        "boolean_logic": requirements.requires_boolean_logic,
        "numeric_comparisons": requirements.requires_numeric_comparisons,
        "problem_predicates": requirements.requires_problem_predicates,
        "model_assertions": requirements.requires_model_assertions,
        "model_semantic_quantities": requirements.requires_model_semantic_quantities,
        "domains": requirements.requires_domains,
        "neighborhoods": requirements.requires_neighborhoods,
        "native_quantifiers": requirements.requires_native_quantifiers,
        "quantifier_alternation": requirements.requires_quantifier_alternation,
        "affine_arithmetic": requirements.requires_affine_arithmetic,
        "nonlinear_arithmetic": requirements.requires_nonlinear_arithmetic,
        "symbolic_division": requirements.requires_symbolic_division,
        "finite_set_membership": requirements.requires_finite_set_membership,
        "symbolic_categories": requirements.requires_symbolic_categories,
        "domain_assumptions": requirements.requires_domain_assumptions,
    }
    tags = {name for name, enabled in flags.items() if enabled}
    tags.update(
        f"scalar_sort:{item.value}" for item in requirements.required_scalar_sorts
    )
    return tags


def _execution_policy_to_dict(policy: BackendExecutionPolicy) -> dict[str, Any]:
    snapshot = policy.snapshot()
    return {
        "timeout_ms": snapshot.timeout_ms,
        "max_backend_units": snapshot.max_backend_units,
        "max_memory_mb": snapshot.max_memory_mb,
        "deterministic_seed": snapshot.deterministic_seed,
        "backend_options": dict(snapshot.backend_options),
    }


def _artifact_to_dict(artifact: ArtifactProvenance) -> dict[str, Any]:
    fingerprint = artifact.fingerprint
    return {
        "role": artifact.role,
        "source_kind": artifact.source_kind,
        "status": artifact.status.value,
        "name": artifact.name,
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
        "unavailable_reason": artifact.unavailable_reason,
    }


def _software_to_dict(
    provenance: VerificationProvenanceContext,
) -> dict[str, Any]:
    software = provenance.software
    return {
        "toetra_version": software.toetra_version,
        "toetra_build_id": software.toetra_build_id,
        "python_version": software.python_version,
        "python_implementation": software.python_implementation,
        "platform": software.platform,
        "components": dict(software.components),
    }


def _validation_artifacts(result: ValidationResult) -> dict[str, Any]:
    paths = {
        "specification": result.specification_path,
        "model": result.model_path,
        "dataset": result.dataset_path,
        "anchor_source": result.anchor_source_path,
    }
    return {
        role: _artifact_to_dict(_path_artifact(role, path))
        for role, path in paths.items()
    }


def _path_artifact(role: str, path: Path | None) -> ArtifactProvenance:
    if path is None:
        return ArtifactProvenance(
            role=role,
            source_kind="not_provided",
            status=FingerprintStatus.NOT_PROVIDED,
        )
    resolved = path.expanduser().resolve()
    try:
        fingerprint = fingerprint_file(resolved)
    except OSError as error:
        return ArtifactProvenance(
            role=role,
            source_kind="file",
            status=FingerprintStatus.UNAVAILABLE,
            name=resolved.name,
            unavailable_reason=str(error),
        )
    return ArtifactProvenance(
        role=role,
        source_kind="file",
        status=FingerprintStatus.AVAILABLE,
        name=resolved.name,
        fingerprint=fingerprint,
    )


def _path_from_source(source: AnchorSource | None) -> Path | None:
    if isinstance(source, (str, Path)):
        return Path(source).expanduser().resolve()
    return None


def _optional_resolved_path(value: str | Path | None) -> Path | None:
    if value is None:
        return None
    return Path(value).expanduser().resolve()


def _standalone_software_payload() -> dict[str, Any]:
    try:
        toetra_version = version("toetra")
    except PackageNotFoundError:
        toetra_version = "unknown"
    return {
        "toetra_version": toetra_version,
        "toetra_build_id": None,
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "platform": sys.platform,
        "components": {},
    }


def _input_specification_path(specification: str | Path) -> Path | None:
    if isinstance(specification, Path):
        return specification.expanduser()
    if "\n" in specification or "\r" in specification:
        return None
    candidate = Path(specification).expanduser()
    if candidate.suffix:
        return candidate
    return None
