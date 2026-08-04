"""Command handlers for shipped Toetra CLI application workflows."""

from __future__ import annotations

import sys
from argparse import Namespace
from pathlib import Path

from toetra._backends.execution import BackendExecutionPolicy, BackendResourceLimits
from toetra._cli.output import emit_primary_output
from toetra._runtime.preflight import (
    InspectionResult,
    ValidationLevel,
    ValidationResult,
    inspect_request,
    validate_request,
)


def run_validate(namespace: Namespace) -> int:
    """Execute ``toetra validate`` and emit its completed result."""

    level = ValidationLevel(namespace.level)
    _reject_inapplicable_execution_options(namespace, level=level)
    policy = (
        _execution_policy(namespace) if level is ValidationLevel.EXECUTABLE else None
    )
    result = validate_request(
        _specification_path(namespace.specification),
        level=level,
        model=namespace.model,
        dataset=namespace.dataset,
        anchor_source=namespace.anchor_source,
        target=namespace.target,
        execution_policy=policy,
    )
    emit_primary_output(
        _render_validation(result, output_format=namespace.format),
        destination=namespace.output,
        consumed_paths=(*result.consumed_paths, *_explicit_input_paths(namespace)),
        stream=sys.stdout,
    )
    return result.exit_code


def run_inspect(namespace: Namespace) -> int:
    """Execute ``toetra inspect`` and emit one executable-plan description."""

    result = inspect_request(
        _specification_path(namespace.specification),
        model=namespace.model,
        dataset=namespace.dataset,
        anchor_source=namespace.anchor_source,
        target=namespace.target,
        execution_policy=_execution_policy(namespace),
    )
    emit_primary_output(
        _render_inspection(result, output_format=namespace.format),
        destination=namespace.output,
        consumed_paths=(*result.consumed_paths, *_explicit_input_paths(namespace)),
        stream=sys.stdout,
    )
    return 0


def _specification_path(raw_path: str) -> Path:
    path = Path(raw_path).expanduser()
    if path.suffix.lower() != ".toetra":
        from toetra._runtime.errors import VerificationConfigurationError

        raise VerificationConfigurationError(
            "CLI specifications must use the canonical '.toetra' extension.",
            code="SPECIFICATION_EXTENSION_INVALID",
            stage="configuration",
            hint="Provide one .toetra file. Inline source and stdin are not accepted.",
            path=str(path),
        )
    return path


def _explicit_input_paths(namespace: Namespace) -> tuple[Path, ...]:
    return tuple(
        Path(value).expanduser()
        for value in (
            namespace.specification,
            namespace.model,
            namespace.dataset,
            namespace.anchor_source,
        )
        if value is not None
    )


def _render_validation(result: ValidationResult, *, output_format: str) -> str:
    if output_format == "json":
        return result.to_json()
    return result.to_text()


def _render_inspection(result: InspectionResult, *, output_format: str) -> str:
    if output_format == "json":
        return result.to_json()
    return result.to_text()


def _execution_policy(namespace: Namespace) -> BackendExecutionPolicy:
    timeout_ms = (
        None
        if namespace.no_timeout
        else (namespace.timeout_ms if namespace.timeout_ms is not None else 30_000)
    )
    return BackendExecutionPolicy(
        timeout_ms=timeout_ms,
        resources=BackendResourceLimits(
            max_backend_units=namespace.max_backend_units,
            max_memory_mb=namespace.max_memory_mb,
        ),
        deterministic_seed=namespace.seed,
    )


def _reject_inapplicable_execution_options(
    namespace: Namespace,
    *,
    level: ValidationLevel,
) -> None:
    if level is ValidationLevel.EXECUTABLE:
        return
    supplied = (
        namespace.timeout_ms is not None
        or namespace.no_timeout
        or namespace.max_backend_units is not None
        or namespace.max_memory_mb is not None
        or namespace.seed is not None
    )
    if supplied:
        from toetra._runtime.errors import VerificationConfigurationError

        raise VerificationConfigurationError(
            "Execution-policy options require '--level executable'.",
            code="CLI_EXECUTION_OPTIONS_INAPPLICABLE",
            stage="configuration",
            hint="Remove execution options or select executable validation.",
        )
