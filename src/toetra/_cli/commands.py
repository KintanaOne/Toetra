"""Command handlers for shipped Toetra CLI application workflows."""

from __future__ import annotations

import sys
from argparse import Namespace
from pathlib import Path
from time import perf_counter
from typing import TYPE_CHECKING

from toetra._backends.execution import BackendExecutionPolicy, BackendResourceLimits
from toetra._cli.output import emit_primary_output, validate_output_paths
from toetra._runtime.preflight import (
    InspectionResult,
    ValidationLevel,
    ValidationResult,
    inspect_request,
    validate_request,
)

if TYPE_CHECKING:
    from toetra._runtime.session import VerificationSession


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


def run_verify(namespace: Namespace) -> int:
    """Execute ``toetra verify`` and emit reports plus optional artifacts."""

    from toetra._cli.artifacts import (
        build_run_manifest,
        build_verification_artifact_set,
        utc_now,
        validate_artifact_stem,
        validate_verification_collection_json,
        verification_artifact_paths,
        write_run_manifest,
        write_verification_report_artifacts,
    )

    if namespace.artifacts_dir is None and namespace.artifact_stem is not None:
        from toetra._runtime.errors import VerificationConfigurationError

        raise VerificationConfigurationError(
            "--artifact-stem requires --artifacts-dir.",
            code="CLI_ARTIFACT_STEM_WITHOUT_DIRECTORY",
            stage="configuration",
            hint="Provide --artifacts-dir or remove --artifact-stem.",
        )

    if namespace.artifacts_dir is None:
        artifact_stem = None
        planned_artifact_paths: tuple[Path, ...] = ()
    else:
        artifact_stem = validate_artifact_stem(
            namespace.artifact_stem or "toetra-verification-report"
        )
        planned_artifact_paths = verification_artifact_paths(
            namespace.artifacts_dir, artifact_stem
        )

    primary_paths = (
        ()
        if namespace.output == "-"
        else (Path(namespace.output).expanduser().resolve(),)
    )
    validate_output_paths(
        (*planned_artifact_paths, *primary_paths),
        consumed_paths=_explicit_input_paths(namespace),
    )

    started_at_utc = utc_now()
    started = perf_counter()
    session = _verify_request(
        _specification_path(namespace.specification),
        model=namespace.model,
        dataset=namespace.dataset,
        anchor_source=namespace.anchor_source,
        target=namespace.target,
        execution_policy=_execution_policy(namespace),
    )
    consumed_paths = _verification_input_paths(session, namespace)

    artifact_set = None
    rendered_json = None
    rendered_html = None
    verification_summary = None
    if namespace.artifacts_dir is not None or namespace.format == "json":
        rendered_json = _render_verification(session, output_format="json")
        verification_summary = validate_verification_collection_json(
            rendered_json,
            expected_report_count=len(session.reports),
        )
    if namespace.artifacts_dir is not None:
        assert artifact_stem is not None
        assert rendered_json is not None
        assert verification_summary is not None
        rendered_html = _render_verification(session, output_format="html")
        artifact_set = build_verification_artifact_set(
            directory=namespace.artifacts_dir,
            stem=artifact_stem,
            json_text=rendered_json,
            html_text=rendered_html,
            verification=verification_summary,
        )

    if namespace.format == "json":
        assert rendered_json is not None
        primary_text = rendered_json
    elif namespace.format == "html" and rendered_html is not None:
        primary_text = rendered_html
    else:
        primary_text = _render_verification(
            session,
            output_format=namespace.format,
        )

    artifact_paths = () if artifact_set is None else artifact_set.paths
    assert artifact_paths == planned_artifact_paths
    validate_output_paths(
        (*artifact_paths, *primary_paths),
        consumed_paths=consumed_paths,
    )

    if artifact_set is not None:
        write_verification_report_artifacts(
            artifact_set,
            consumed_paths=consumed_paths,
            reserved_paths=primary_paths,
        )

    emit_primary_output(
        primary_text,
        destination=namespace.output,
        consumed_paths=consumed_paths,
        reserved_paths=artifact_paths,
        stream=sys.stdout,
    )

    if artifact_set is not None:
        completed_at_utc = utc_now()
        manifest = build_run_manifest(
            session,
            artifacts=artifact_set,
            process_status=session.exit_code,
            primary_format=namespace.format,
            primary_destination=_primary_destination(namespace.output),
            started_at_utc=started_at_utc,
            completed_at_utc=completed_at_utc,
            duration_ms=(perf_counter() - started) * 1000.0,
        )
        write_run_manifest(
            manifest,
            artifact_set=artifact_set,
            consumed_paths=consumed_paths,
            reserved_paths=primary_paths,
        )
    return session.exit_code


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


def _render_verification(
    session: VerificationSession,
    *,
    output_format: str,
) -> str:
    try:
        if output_format == "json":
            rendered = session.to_json()
        elif output_format == "html":
            rendered = session.to_html()
        else:
            rendered = session.to_text()
        if not isinstance(rendered, str):
            raise TypeError("verification renderers must return text")
        return rendered
    except (TypeError, ValueError) as error:
        from toetra._runtime.errors import VerificationRuntimeError

        raise VerificationRuntimeError(
            f"Failed to render verification output as {output_format}.",
            code="CLI_VERIFICATION_RENDER_FAILED",
            stage="output",
            hint="Retry another output format and report reproducible failures.",
        ) from error


def _verify_request(
    specification: Path,
    *,
    model: str | None,
    dataset: str | None,
    anchor_source: str | None,
    target: str | None,
    execution_policy: BackendExecutionPolicy,
) -> VerificationSession:
    from toetra._runtime.api import verify

    return verify(
        specification,
        model=model,
        dataset=dataset,
        anchor_source=anchor_source,
        target=target,
        execution_policy=execution_policy,
    )


def _verification_input_paths(
    session: VerificationSession,
    namespace: Namespace,
) -> tuple[Path, ...]:
    candidates = (
        getattr(session, "specification_path", None),
        getattr(session, "model_path", None),
        getattr(session, "dataset_path", None),
        *_explicit_input_paths(namespace),
    )
    unique: list[Path] = []
    seen: set[Path] = set()
    for candidate in candidates:
        if candidate is None:
            continue
        path = Path(candidate).expanduser().resolve()
        if path not in seen:
            seen.add(path)
            unique.append(path)
    return tuple(unique)


def _primary_destination(destination: str) -> str:
    if destination == "-":
        return "-"
    return str(Path(destination).expanduser().resolve())


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
