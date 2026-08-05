"""Model-aware starter specification generation for ``toetra init``."""

from __future__ import annotations

import json
import os
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from toetra._models.errors.base import ModelError
from toetra._models.runtime.manager import ModelManager
from toetra._models.schema.model_schema import ModelSchema
from toetra._models.schema.output_schema import EnumModelOutputKind
from toetra._runtime import api as runtime_api
from toetra._runtime.errors import (
    VerificationConfigurationError,
    VerificationRuntimeError,
)
from toetra._runtime.preflight import (
    ValidationLevel,
    ValidationResult,
    validate_request,
)

_IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\Z")
_RESERVED_IDENTIFIERS = {
    "anchor",
    "and",
    "at",
    "check_at",
    "dataset",
    "domain",
    "exists",
    "false",
    "forall",
    "in",
    "model",
    "neighborhood",
    "not",
    "or",
    "ref",
    "target",
    "true",
    "using",
    "where",
    "with",
    "xor",
    "z3",
    "eran",
    "zonotope",
    "box",
    "robustness",
    "stability",
    "fairness",
    "monotonicity",
    "bound",
    "logic",
    "classification",
    "prediction",
    "regression",
    "clustering",
    "anomaly_detection",
    "reinforcement_learning",
    "equal",
    "equity",
    "between",
    "increasing",
    "decreasing",
    "label",
    "probability",
    "hyperball",
    "levenshtein",
    "euclidian",
}


@dataclass(frozen=True)
class InitializationResult:
    """Completed starter-specification generation."""

    destination: Path
    model_path: Path
    dataset_path: Path | None
    schema: ModelSchema
    source: str


ValidationFunction = Callable[..., ValidationResult]


def initialize_specification(
    destination: str | Path,
    *,
    model: str | Path,
    target: str,
    dataset: str | Path | None = None,
    force: bool = False,
    validation_function: ValidationFunction = validate_request,
) -> InitializationResult:
    """Create one executable smoke specification and commit it atomically."""

    destination_path = _destination_path(destination)
    _require_identifier(target, role="target")
    model_path = _required_input_file(
        model,
        role="model",
        missing_code="MODEL_ARTIFACT_NOT_FOUND",
        missing_message="Serialized model not found",
    )
    dataset_path = (
        _required_input_file(
            dataset,
            role="dataset",
            missing_code="MODEL_DATASET_NOT_FOUND",
            missing_message="Reference dataset not found",
        )
        if dataset is not None
        else None
    )
    _reject_destination_shape(destination_path)
    _reject_input_collision(
        destination_path,
        model_path=model_path,
        dataset_path=dataset_path,
    )
    _reject_existing_destination(destination_path, force=force)

    schema = _build_schema(
        model_path=model_path,
        dataset_path=dataset_path,
        target=target,
    )
    _validate_schema_identifiers(schema)
    destination_directory = destination_path.parent.resolve(strict=False)
    source = render_starter_specification(
        schema,
        model_reference=_artifact_reference(
            model_path,
            destination_directory=destination_directory,
        ),
        dataset_reference=(
            _artifact_reference(
                dataset_path,
                destination_directory=destination_directory,
            )
            if dataset_path is not None
            else None
        ),
    )

    temporary = _write_temporary_specification(destination_path, source)
    try:
        # The staged file lives beside the final destination, so its header-relative
        # model and dataset references already exercise the generated contract.
        validation = validation_function(
            temporary,
            level=ValidationLevel.EXECUTABLE,
        )
        _require_valid_generated_specification(validation)
        _commit_temporary_specification(
            temporary,
            destination_path,
            force=force,
        )
    finally:
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass

    return InitializationResult(
        destination=destination_path,
        model_path=model_path,
        dataset_path=dataset_path,
        schema=schema,
        source=source,
    )


def render_starter_specification(
    schema: ModelSchema,
    *,
    model_reference: str,
    dataset_reference: str | None = None,
) -> str:
    """Render one deterministic, model-aware smoke specification."""

    _validate_schema_identifiers(schema)
    feature_lines = [
        (
            f"#   - {feature.name}: {feature.dtype.value}"
            + (
                f" (source: {feature.source_dtype})"
                if feature.source_dtype is not None
                else ""
            )
        )
        for feature in schema.features.values()
    ]
    declarations = [
        f"model := {json.dumps(model_reference, ensure_ascii=False)}",
        f"target := {schema.output_name}",
    ]
    if dataset_reference is not None:
        declarations.append(
            f"dataset := {json.dumps(dataset_reference, ensure_ascii=False)}"
        )

    lines = [
        "# Generated by `toetra init`.",
        "# This smoke property checks integration only; it is not business,",
        "# quality, robustness, fairness, or safety evidence.",
        ("# Model: " f"{schema.framework.value} / {schema.model_type} / {schema.task}"),
        "# Normalized input features:",
        *feature_lines,
        "# Replace the smoke property with a meaningful Toetra requirement.",
        "# Consider a bound, witness, monotonicity, robustness, or",
        "# label/probability requirement appropriate to the model use case.",
        *declarations,
        "",
        "# SMOKE PROPERTY — deterministic model wiring only.",
        "[LOGIC]:",
        _smoke_property(schema),
    ]
    return "\n".join(lines).rstrip("\r\n") + "\n"


def _destination_path(value: str | Path) -> Path:
    path = Path(value).expanduser()
    if path.suffix.lower() != ".toetra":
        raise VerificationConfigurationError(
            "Generated specifications must use the canonical '.toetra' extension.",
            code="INIT_DESTINATION_EXTENSION_INVALID",
            stage="configuration",
            hint="Choose a destination path ending in .toetra.",
            path=str(path),
        )
    return Path(os.path.abspath(path))


def _required_input_file(
    value: str | Path,
    *,
    role: str,
    missing_code: str,
    missing_message: str,
) -> Path:
    path = Path(value).expanduser().resolve()
    if not path.is_file():
        raise VerificationConfigurationError(
            f"{missing_message}: {path}",
            code=missing_code,
            stage="model",
            hint=f"Provide an existing readable {role} artifact.",
            path=str(path),
        )
    return path


def _reject_destination_shape(destination: Path) -> None:
    if not os.path.lexists(destination):
        return
    if destination.is_symlink():
        raise VerificationConfigurationError(
            f"Init destination cannot be a symbolic link: {destination}",
            code="INIT_DESTINATION_SYMLINK_UNSUPPORTED",
            stage="output",
            hint="Choose a regular .toetra destination path.",
            path=str(destination),
        )
    if destination.is_dir():
        raise VerificationConfigurationError(
            f"Init destination is a directory: {destination}",
            code="INIT_DESTINATION_NOT_FILE",
            stage="output",
            hint="Choose a .toetra file path.",
            path=str(destination),
        )


def _reject_existing_destination(destination: Path, *, force: bool) -> None:
    _reject_destination_shape(destination)
    if os.path.lexists(destination) and not force:
        raise VerificationConfigurationError(
            f"Init destination already exists: {destination}",
            code="INIT_DESTINATION_EXISTS",
            stage="output",
            hint="Choose another destination or pass --force explicitly.",
            path=str(destination),
        )


def _reject_input_collision(
    destination: Path,
    *,
    model_path: Path,
    dataset_path: Path | None,
) -> None:
    consumed = {model_path}
    if dataset_path is not None:
        consumed.add(dataset_path)
    destination_identity = destination.resolve(strict=False)
    if destination_identity in consumed:
        raise VerificationConfigurationError(
            f"Init destination collides with an input artifact: {destination}",
            code="INIT_DESTINATION_INPUT_COLLISION",
            stage="output",
            hint="Choose a new .toetra destination distinct from model and dataset.",
            path=str(destination),
        )


def _build_schema(
    *,
    model_path: Path,
    dataset_path: Path | None,
    target: str,
) -> ModelSchema:
    manager = ModelManager(
        model_path=model_path,
        dataset_path=dataset_path,
        output_name=target,
    )
    try:
        return manager.build_schema()
    except ModelError as error:
        raise runtime_api._public_model_error(
            error,
            model_path=model_path,
            dataset_path=dataset_path,
        ) from error


def _validate_schema_identifiers(schema: ModelSchema) -> None:
    _require_identifier(schema.output_name, role="target")
    if not schema.features:
        raise VerificationRuntimeError(
            "The selected model exposes no normalized input feature.",
            code="INIT_MODEL_FEATURES_EMPTY",
            stage="model",
            hint="Provide a fitted model and reference dataset with named inputs.",
        )
    for feature in schema.features.values():
        _require_identifier(feature.name, role="feature")


def _require_identifier(value: str, *, role: str) -> None:
    candidate = value.strip()
    if (
        candidate == value
        and _IDENTIFIER.fullmatch(candidate)
        and candidate.lower() not in _RESERVED_IDENTIFIERS
    ):
        return
    raise VerificationConfigurationError(
        f"Model {role} name cannot be represented in Toetra syntax: {value!r}",
        code=f"INIT_{role.upper()}_IDENTIFIER_UNSUPPORTED",
        stage="model",
        hint=(
            "Use canonical names matching [A-Za-z_][A-Za-z0-9_]* and avoid "
            "Toetra reserved words."
        ),
    )


def _smoke_property(schema: ModelSchema) -> str:
    output_kind = schema.output_schema.kind
    if output_kind is EnumModelOutputKind.REGRESSION:
        return "forall sample => target[sample] <= target[sample] using Z3"
    if output_kind is EnumModelOutputKind.CLASSIFICATION:
        restrictions = "\n    and ".join(
            f"duplicate.{name} == sample.{name}" for name in schema.features
        )
        return (
            "forall sample, duplicate\n"
            f"where {restrictions}\n"
            "=> target[sample].label == target[duplicate].label using Z3"
        )
    raise VerificationRuntimeError(
        f"Cannot generate a smoke property for model task {schema.task!r}.",
        code="INIT_MODEL_TASK_UNSUPPORTED",
        stage="model",
        hint="Use a supported regression or binary-classification model route.",
    )


def _artifact_reference(path: Path, *, destination_directory: Path) -> str:
    try:
        reference = os.path.relpath(path, start=destination_directory)
    except ValueError:
        return path.as_posix()
    return Path(reference).as_posix()


def _write_temporary_specification(destination: Path, source: str) -> Path:
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{destination.stem}.",
            suffix=".toetra",
            dir=destination.parent,
            text=True,
        )
        temporary = Path(temporary_name)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(source.rstrip("\r\n") + "\n")
                handle.flush()
                os.fsync(handle.fileno())
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise
        return temporary
    except OSError as error:
        raise VerificationRuntimeError(
            f"Failed to stage generated specification: {destination}",
            code="INIT_STAGING_WRITE_FAILED",
            stage="output",
            hint="Check the destination directory, permissions, and storage.",
            path=str(destination),
        ) from error


def _require_valid_generated_specification(result: ValidationResult) -> None:
    if result.valid and result.completed_level is ValidationLevel.EXECUTABLE:
        return
    diagnostic = result.diagnostic
    message = "Generated specification failed executable validation."
    if diagnostic is None:
        raise VerificationRuntimeError(
            message,
            code="INIT_GENERATED_SPECIFICATION_INVALID",
            stage="initialization",
            hint="Report this failure with the model and generated source details.",
        )
    error_type = (
        VerificationConfigurationError
        if diagnostic.category == "configuration"
        else VerificationRuntimeError
    )
    raise error_type(
        f"{message} {diagnostic.message}",
        code=diagnostic.code,
        stage=diagnostic.stage,
        hint=diagnostic.hint,
        path=diagnostic.path,
        line=diagnostic.line,
        column=diagnostic.column,
    )


def _commit_temporary_specification(
    temporary: Path,
    destination: Path,
    *,
    force: bool,
) -> None:
    try:
        _reject_existing_destination(destination, force=force)
        if force:
            os.replace(temporary, destination)
            return
        try:
            os.link(temporary, destination)
        except FileExistsError as error:
            raise VerificationConfigurationError(
                f"Init destination already exists: {destination}",
                code="INIT_DESTINATION_EXISTS",
                stage="output",
                hint="Choose another destination or pass --force explicitly.",
                path=str(destination),
            ) from error
    except VerificationRuntimeError:
        raise
    except OSError as error:
        raise VerificationRuntimeError(
            f"Failed to commit generated specification: {destination}",
            code="INIT_DESTINATION_WRITE_FAILED",
            stage="output",
            hint="Check the destination path, permissions, and filesystem support.",
            path=str(destination),
        ) from error
