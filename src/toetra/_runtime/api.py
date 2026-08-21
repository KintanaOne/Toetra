from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, replace
from pathlib import Path

from toetra._backends.errors import (
    BackendExecutionError,
    BackendExecutionPolicyError,
    BackendNotRegisteredError,
    BackendRoutingError,
    BackendSymbolCollisionError,
    BackendTranslationError,
    NoCompatibleBackendError,
    NumericCompatibilityRouteError,
    UnsupportedBackendRequirementsError,
    UnsupportedScalarExpressionError,
)
from toetra._backends.execution import BackendExecutionPolicy
from toetra._backends.registry import BackendRegistry
from toetra._backends.router import BackendRouter
from toetra._compatibility.policy import (
    apply_numeric_compatibility_policy,
    apply_semantic_lowering_policy,
)
from toetra._compatibility.registry import NumericCompatibilityRegistry
from toetra._compatibility.errors import (
    AmbiguousCompatibilityRuleError,
    NumericCompatibilityError,
)
from toetra._compiler.ast.nodes.program import ProgramNode
from toetra._compiler.builder.errors import BuilderError
from toetra._compiler.builder.program import parse_program
from toetra._compiler.ir.ir2.context import IR2BuildContext
from toetra._compiler.ir.ir2.run_ir2 import run_ir2_with_model_schema
from toetra._compiler.model_lowering.errors import (
    InvalidModelIRLoweringError,
    ModelIRLoweringError,
    UnsupportedModelIRLoweringError,
)
from toetra._compiler.parser.errors import ParserError
from toetra._compiler.parser.parser import parse_toetra_code
from toetra._compiler.semantic.errors.errors import SemanticError
from toetra._reporting.builder import build_verification_report
from toetra._runtime.anchors import (
    AnchorLookupRequest,
    AnchorResolver,
    AnchorSource,
    DataFrameAnchorResolver,
)
from toetra._runtime.backends import BackendRunnerRegistry
from toetra._runtime.execution_context import (
    ExecutionContext,
    resolve_execution_context,
)
from toetra._runtime.errors import (
    AnchorResolutionError,
    BackendRunnerNotRegisteredError,
    VerificationConfigurationError,
    VerificationRuntimeError,
)
from toetra._runtime.session import VerificationExecution, VerificationSession
from toetra._compiler.semantic.core.anchors import AnchorValidator
from toetra._compiler.semantic.symbols.point import (
    PointBindingKind,
    ResolvedAnchorBinding,
    frozen_mapping,
)
from toetra._models.errors.base import ModelError
from toetra._models.errors.detection import (
    ModelDetectionError,
    UnsupportedModelError,
)
from toetra._models.errors.introspection import (
    MissingFeatureMetadataError,
    ModelIntrospectionError,
    ReferenceDatasetError,
    UnsupportedIntrospectorError,
)
from toetra._models.errors.loading import (
    ModelDeserializationError,
    ModelFileNotFoundError,
    ModelLoadingError,
    UnsupportedModelFormatError,
)
from toetra._models.encoder.context import ModelEncodingContext
from toetra._models.encoder.errors import (
    InvalidModelAssumptionError,
    MissingModelParameterError,
    ModelEncoderError,
    UnsupportedModelEncoderError,
    UnsupportedModelParameterError,
)
from toetra._models.encoder.factory import ModelEncoderFactory
from toetra._models.ir_builder.errors import (
    InvalidModelIRParameterError,
    MissingModelIRParameterError,
    ModelIRBuilderError,
    UnsupportedModelIRBuilderError,
)
from toetra._models.runtime.manager import ModelManager
from toetra._models.schema.model_schema import ModelSchema
from toetra._models.semantics.errors import (
    InvalidModelSemanticProfileError,
    MissingModelSemanticsError,
    ModelSemanticLoweringError,
    UnsupportedModelSemanticProfileError,
    UnsupportedObservableLoweringError,
)

# These names remain module-level monkeypatch seams for existing runtime tests and
# advanced private integrations while preflight planning is shared across commands.
_RUNTIME_MONKEYPATCH_SEAMS = (BackendRouter, run_ir2_with_model_schema)


@dataclass(frozen=True)
class _ResolvedModel:
    schema: ModelSchema
    model: object | None
    model_path: Path | None
    dataset_path: Path | None
    execution_context: ExecutionContext
    program: ProgramNode


@dataclass(frozen=True)
class _LoadedSpecification:
    source: str
    program: ProgramNode
    path: Path | None
    base_directory: Path
    model_reference: str
    target: str
    dataset_reference: str | None


def verify(
    specification: str | Path,
    *,
    model: str | Path | None = None,
    dataset: str | Path | None = None,
    target: str | None = None,
    schema: ModelSchema | None = None,
    model_context: ModelEncodingContext | None = None,
    model_encoder_factory: ModelEncoderFactory | None = None,
    ir2_context: IR2BuildContext | None = None,
    backend_registry: BackendRegistry | None = None,
    numeric_compatibility_registry: NumericCompatibilityRegistry | None = None,
    runner_registry: BackendRunnerRegistry | None = None,
    execution_policy: BackendExecutionPolicy | None = None,
    anchor_source: AnchorSource | None = None,
    anchor_resolver: AnchorResolver | None = None,
) -> VerificationSession:
    """Verify every property from a Toetra source or ``.toetra`` file.

    A caller may provide an already normalized ``ModelSchema`` or let Toetra
    build one from a serialized model. When ``model`` is omitted for a file
    specification, the model reference from the Toetra header is resolved
    relative to the specification file. An omitted ``dataset`` argument uses
    the optional header dataset under the same path rule. Referenced anchors
    require either a dedicated ``anchor_source`` (pandas DataFrame or CSV
    path) or a custom ``anchor_resolver``. When neither is provided, the
    effective dataset artifact is reused as the default anchor lookup source.
    This fallback is ergonomic only: model-schema introspection and anchor
    lookup remain distinct runtime responsibilities. Custom framework/model
    integrations may
    supply a ``model_encoder_factory`` whose selected encoder declares its
    numeric semantic target. ``execution_policy`` applies one backend-neutral
    timeout/resource/cancellation contract to every property in the session.
    """

    try:
        return _verify(
            specification,
            model=model,
            dataset=dataset,
            target=target,
            schema=schema,
            model_context=model_context,
            model_encoder_factory=model_encoder_factory,
            ir2_context=ir2_context,
            backend_registry=backend_registry,
            numeric_compatibility_registry=numeric_compatibility_registry,
            runner_registry=runner_registry,
            execution_policy=execution_policy,
            anchor_source=anchor_source,
            anchor_resolver=anchor_resolver,
        )
    except ParserError as error:
        raise _public_compiler_error(
            error,
            stage="syntax",
            path=_diagnostic_specification_path(specification),
        ) from error
    except BuilderError as error:
        raise _public_compiler_error(
            error,
            stage="builder",
            path=_diagnostic_specification_path(specification),
        ) from error
    except SemanticError as error:
        raise _public_compiler_error(
            error,
            stage="semantic",
            path=_diagnostic_specification_path(specification),
        ) from error


def _verify(
    specification: str | Path,
    *,
    model: str | Path | None,
    dataset: str | Path | None,
    target: str | None,
    schema: ModelSchema | None,
    model_context: ModelEncodingContext | None,
    model_encoder_factory: ModelEncoderFactory | None,
    ir2_context: IR2BuildContext | None,
    backend_registry: BackendRegistry | None,
    numeric_compatibility_registry: NumericCompatibilityRegistry | None,
    runner_registry: BackendRunnerRegistry | None,
    execution_policy: BackendExecutionPolicy | None,
    anchor_source: AnchorSource | None,
    anchor_resolver: AnchorResolver | None,
) -> VerificationSession:
    from toetra._runtime.preflight import build_executable_plan

    plan = build_executable_plan(
        specification,
        model=model,
        dataset=dataset,
        target=target,
        schema=schema,
        model_context=model_context,
        model_encoder_factory=model_encoder_factory,
        ir2_context=ir2_context,
        backend_registry=backend_registry,
        numeric_compatibility_registry=numeric_compatibility_registry,
        runner_registry=runner_registry,
        execution_policy=execution_policy,
        anchor_source=anchor_source,
        anchor_resolver=anchor_resolver,
        require_translation=False,
    )

    executions: list[VerificationExecution] = []
    for item in plan.properties:
        try:
            result = item.runner.run(
                item.task,
                policy=plan.execution_policy,
            )
        except BackendExecutionPolicyError as error:
            raise _public_backend_policy_error(error) from error
        except BackendTranslationError as error:
            raise _public_backend_translation_error(error) from error
        except BackendExecutionError as error:
            raise _public_backend_execution_error(error) from error
        result = apply_numeric_compatibility_policy(
            result,
            item.route.numeric_compatibility,
        )
        result = apply_semantic_lowering_policy(
            result,
            item.task.lowering_evidence,
        )
        report = build_verification_report(
            item.task,
            item.route,
            result,
            property_index=item.index,
            provenance_context=plan.provenance,
            schema=plan.schema,
        )
        executions.append(
            VerificationExecution(
                task=item.task,
                route=item.route,
                result=result,
                report=report,
            )
        )

    return VerificationSession(
        source=plan.source,
        specification_path=plan.specification_path,
        schema=plan.schema,
        executions=tuple(executions),
        model=plan.model,
        model_path=plan.model_path,
        dataset_path=plan.dataset_path,
        execution_context=plan.execution_context,
        anchor_resolutions=plan.anchor_resolutions,
        provenance=plan.provenance,
    )


def _public_compiler_error(
    error: ParserError | BuilderError | SemanticError,
    *,
    stage: str,
    path: str | None,
) -> VerificationConfigurationError:
    return VerificationConfigurationError(
        error.message,
        code=error.code,
        stage=stage,
        hint=error.hint,
        path=path,
        line=error.line,
        column=error.column,
    )


def _diagnostic_specification_path(specification: str | Path) -> str | None:
    if isinstance(specification, Path):
        return str(specification)
    if "\n" in specification or "\r" in specification:
        return None
    candidate = Path(specification)
    if candidate.suffix.lower() == ".toetra":
        return str(candidate)
    return None


def _load_specification(specification: str | Path) -> _LoadedSpecification:
    path = _specification_path(specification)
    if path is not None:
        if not path.is_file():
            raise VerificationConfigurationError(
                f"Toetra specification not found: {path}",
                code="SPECIFICATION_NOT_FOUND",
                stage="configuration",
                hint="Check the specification path and ensure the file exists.",
                path=str(path),
            )
        resolved_path = path.resolve()
        try:
            source = resolved_path.read_text(encoding="utf-8")
        except UnicodeError as error:
            raise VerificationConfigurationError(
                f"Toetra specification is not valid UTF-8: {path}",
                code="SPECIFICATION_ENCODING_INVALID",
                stage="configuration",
                hint="Save the specification as UTF-8 and try again.",
                path=str(path),
            ) from error
        except OSError as error:
            raise VerificationConfigurationError(
                f"Failed to read Toetra specification: {path}",
                code="SPECIFICATION_READ_FAILED",
                stage="configuration",
                hint="Check the specification path and read permissions.",
                path=str(path),
            ) from error
        base_directory = resolved_path.parent
    else:
        source = str(specification)
        resolved_path = None
        base_directory = Path.cwd()

    program = parse_program(parse_toetra_code(source))
    return _LoadedSpecification(
        source=source,
        program=program,
        path=resolved_path,
        base_directory=base_directory,
        model_reference=program.header.model,
        target=program.header.target,
        dataset_reference=program.header.dataset,
    )


def _specification_path(specification: str | Path) -> Path | None:
    if isinstance(specification, Path):
        candidate = specification
    else:
        if "\n" in specification or "\r" in specification:
            return None
        candidate = Path(specification)

    if candidate.suffix.lower() == ".forml":
        raise VerificationConfigurationError(
            "Legacy '.forml' specifications are not supported; "
            "rename the file with the canonical '.toetra' extension."
        )

    if isinstance(specification, Path):
        return candidate
    if candidate.exists() or candidate.suffix.lower() == ".toetra":
        return candidate
    return None


def _resolve_model(
    loaded: _LoadedSpecification,
    *,
    model: str | Path | None,
    dataset: str | Path | None,
    target: str | None,
    schema: ModelSchema | None,
    execution_context: ExecutionContext | None = None,
) -> _ResolvedModel:
    if execution_context is None:
        execution_context = resolve_execution_context(
            declared_model_reference=loaded.model_reference,
            declared_target=loaded.target,
            declared_dataset_reference=loaded.dataset_reference,
            model=model,
            target=target,
            dataset=dataset,
        )
    else:
        _validate_execution_context_declarations(loaded, execution_context)
    effective_program = execution_context.apply_to(loaded.program)

    if schema is not None:
        if model is not None or dataset is not None:
            raise VerificationConfigurationError(
                "Provide either 'schema' or explicit model/dataset artifacts, not both"
            )
        effective_schema = _schema_with_output_name(
            schema,
            execution_context.effective_target,
        )
        dataset_path = _resolve_effective_dataset_path(loaded, dataset=None)
        _require_dataset_file(dataset_path)
        return _ResolvedModel(
            schema=effective_schema,
            model=None,
            model_path=None,
            dataset_path=(dataset_path.resolve() if dataset_path is not None else None),
            execution_context=execution_context,
            program=effective_program,
        )

    model_locator: str | Path | None = model
    if model_locator is None and execution_context.model_overridden:
        model_locator = execution_context.effective_model_reference
    model_path = (
        _resolve_explicit_path(model_locator)
        if model_locator is not None
        else _resolve_header_model_path(loaded)
    )
    if not model_path.is_file():
        raise VerificationConfigurationError(
            f"Serialized model not found: {model_path}",
            code="MODEL_ARTIFACT_NOT_FOUND",
            stage="model",
            hint=(
                "Check model=... or the model path in the Toetra header. "
                "Header paths are relative to the specification file."
            ),
            path=str(model_path),
        )

    dataset_locator: str | Path | None = dataset
    if dataset_locator is None and execution_context.dataset_overridden:
        dataset_locator = execution_context.effective_dataset_reference
    dataset_path = _resolve_effective_dataset_path(
        loaded,
        dataset=dataset_locator,
    )
    _require_dataset_file(dataset_path)

    manager = ModelManager(
        model_path=model_path,
        dataset_path=dataset_path,
        output_name=execution_context.effective_target,
    )
    try:
        resolved_schema = manager.build_schema()
    except ModelError as error:
        raise _public_model_error(
            error,
            model_path=model_path,
            dataset_path=dataset_path,
        ) from error
    _validate_target_contract(
        execution_context.effective_target,
        resolved_schema.output_name,
    )
    return _ResolvedModel(
        schema=resolved_schema,
        model=manager.model,
        model_path=model_path.resolve(),
        dataset_path=(dataset_path.resolve() if dataset_path is not None else None),
        execution_context=execution_context,
        program=effective_program,
    )


def _validate_execution_context_declarations(
    loaded: _LoadedSpecification,
    context: ExecutionContext,
) -> None:
    declared = (
        context.declared_model_reference,
        context.declared_target,
        context.declared_dataset_reference,
    )
    current = (
        loaded.model_reference,
        loaded.target,
        loaded.dataset_reference,
    )
    if declared == current:
        return
    raise VerificationConfigurationError(
        "Execution context declarations do not match the specification header.",
        code="EXECUTION_CONTEXT_DECLARATION_MISMATCH",
        stage="configuration",
        hint="Use the exact specification that declared this execution context.",
        path=str(loaded.path) if loaded.path is not None else None,
    )


def _schema_with_output_name(schema: ModelSchema, output_name: str) -> ModelSchema:
    """Return an isolated schema view bound to one effective output name."""

    if schema.output_name == output_name:
        return schema
    return replace(schema, output_name=output_name)


def _resolve_header_model_path(loaded: _LoadedSpecification) -> Path:
    candidate = Path(loaded.model_reference)
    if candidate.is_absolute():
        return candidate
    return loaded.base_directory / candidate


def _resolve_header_dataset_path(loaded: _LoadedSpecification) -> Path | None:
    reference = loaded.dataset_reference
    if reference is None:
        return None
    candidate = Path(reference)
    if candidate.is_absolute():
        return candidate
    return loaded.base_directory / candidate


def _resolve_effective_dataset_path(
    loaded: _LoadedSpecification,
    *,
    dataset: str | Path | None,
) -> Path | None:
    if dataset is not None:
        return _resolve_explicit_path(dataset)
    return _resolve_header_dataset_path(loaded)


def _require_dataset_file(dataset_path: Path | None) -> None:
    if dataset_path is None or dataset_path.is_file():
        return
    raise VerificationConfigurationError(
        f"Reference dataset not found: {dataset_path}",
        code="MODEL_DATASET_NOT_FOUND",
        stage="model",
        hint=(
            "Check dataset=... or the dataset path in the Toetra header. "
            "Header paths are relative to the specification file."
        ),
        path=str(dataset_path),
    )


def _resolve_explicit_path(value: str | Path) -> Path:
    return Path(value).expanduser()


def _public_model_error(
    error: ModelError,
    *,
    model_path: Path,
    dataset_path: Path | None,
) -> VerificationRuntimeError:
    model_artifact_path = str(model_path)
    dataset_artifact_path = str(dataset_path) if dataset_path is not None else None

    if isinstance(error, UnsupportedModelFormatError):
        return VerificationConfigurationError(
            str(error),
            code="MODEL_ARTIFACT_FORMAT_UNSUPPORTED",
            stage="model",
            hint=(
                "Use a supported serialized model artifact. The built-in V1 "
                "routes accept fitted sklearn models serialized as .joblib or .pkl."
            ),
            path=model_artifact_path,
        )
    if isinstance(error, ModelFileNotFoundError):
        return VerificationConfigurationError(
            f"Serialized model not found: {model_path}",
            code="MODEL_ARTIFACT_NOT_FOUND",
            stage="model",
            hint="Check the model artifact path and try again.",
            path=model_artifact_path,
        )
    if isinstance(error, ModelDeserializationError):
        return VerificationConfigurationError(
            str(error),
            code="MODEL_ARTIFACT_DESERIALIZATION_FAILED",
            stage="model",
            hint=(
                "Recreate the model artifact with compatible Python and "
                "framework versions, then try again."
            ),
            path=model_artifact_path,
        )
    if isinstance(error, ModelLoadingError):
        return VerificationConfigurationError(
            str(error),
            code="MODEL_ARTIFACT_INVALID",
            stage="model",
            hint="Check the serialized model artifact and its format.",
            path=model_artifact_path,
        )
    if isinstance(error, ReferenceDatasetError):
        return VerificationConfigurationError(
            str(error),
            code="MODEL_DATASET_READ_FAILED",
            stage="model",
            hint="Provide a readable UTF-8 CSV reference dataset.",
            path=dataset_artifact_path,
        )
    if isinstance(error, MissingFeatureMetadataError):
        return VerificationConfigurationError(
            str(error),
            code="MODEL_FEATURE_METADATA_REQUIRED",
            stage="model",
            hint=(
                "Pass dataset=... with the model input columns, or provide "
                "an explicit schema=... instead of artifact introspection."
            ),
            path=dataset_artifact_path or model_artifact_path,
        )
    if isinstance(error, UnsupportedModelError):
        return VerificationRuntimeError(
            str(error),
            code="MODEL_TYPE_UNSUPPORTED",
            stage="model",
            hint=(
                "Use a model family listed in the public V1 profile or add a "
                "complete framework, model-schema, and encoder integration."
            ),
            path=model_artifact_path,
        )
    if isinstance(error, UnsupportedIntrospectorError):
        return VerificationRuntimeError(
            str(error),
            code="MODEL_FRAMEWORK_UNSUPPORTED",
            stage="model",
            hint=(
                "Use a framework adapter listed in the public V1 profile or "
                "register a complete framework integration."
            ),
            path=model_artifact_path,
        )
    if isinstance(error, ModelDetectionError):
        return VerificationRuntimeError(
            str(error),
            code="MODEL_DETECTION_FAILED",
            stage="model",
            hint="Check that the artifact contains a supported fitted model.",
            path=model_artifact_path,
        )
    if isinstance(error, ModelIntrospectionError):
        return VerificationRuntimeError(
            str(error),
            code="MODEL_INTROSPECTION_FAILED",
            stage="model",
            hint="Check the model and reference dataset metadata.",
            path=dataset_artifact_path or model_artifact_path,
        )
    return VerificationRuntimeError(
        str(error),
        code="MODEL_PROCESSING_FAILED",
        stage="model",
        hint="Inspect the chained model-layer cause for diagnostic details.",
        path=model_artifact_path,
    )


def _public_model_encoder_error(
    error: ModelEncoderError,
    *,
    model_path: Path | None,
) -> VerificationRuntimeError:
    path = str(model_path) if model_path is not None else None
    if isinstance(error, UnsupportedModelEncoderError):
        return VerificationRuntimeError(
            str(error),
            code="MODEL_ENCODER_UNSUPPORTED",
            stage="model",
            hint=(
                "Use a model family with a complete V1 encoder route or register "
                "a compatible model encoder through the advanced integration API."
            ),
            path=path,
        )
    if isinstance(error, MissingModelParameterError):
        return VerificationConfigurationError(
            str(error),
            code="MODEL_ENCODER_PARAMETER_MISSING",
            stage="model",
            hint=(
                "Provide a complete normalized model schema, including the "
                "parameters required by its selected encoder."
            ),
            path=path,
        )
    if isinstance(error, UnsupportedModelParameterError):
        return VerificationRuntimeError(
            str(error),
            code="MODEL_ENCODER_PARAMETER_UNSUPPORTED",
            stage="model",
            hint=(
                "Use parameters within the selected encoder profile or add a "
                "complete encoder integration for this model variant."
            ),
            path=path,
        )
    if isinstance(error, InvalidModelAssumptionError):
        return VerificationRuntimeError(
            str(error),
            code="MODEL_ENCODER_OUTPUT_INVALID",
            stage="model",
            hint=(
                "The selected encoder emitted invalid model assumptions; inspect "
                "the chained integration error."
            ),
            path=path,
        )
    return VerificationRuntimeError(
        str(error),
        code="MODEL_ENCODING_FAILED",
        stage="model",
        hint="Inspect the chained model-encoder error for diagnostic details.",
        path=path,
    )


def _public_model_ir_builder_error(
    error: ModelIRBuilderError,
    *,
    model_path: Path | None,
) -> VerificationRuntimeError:
    """Preserve the V1 model-route error surface for Model IR construction."""

    path = str(model_path) if model_path is not None else None
    if isinstance(error, UnsupportedModelIRBuilderError):
        return VerificationRuntimeError(
            str(error),
            code="MODEL_ENCODER_UNSUPPORTED",
            stage="model",
            hint=(
                "Use a model family with a complete Model IR route or register "
                "an explicit legacy model_encoder_factory integration."
            ),
            path=path,
        )
    if isinstance(error, MissingModelIRParameterError):
        return VerificationConfigurationError(
            str(error),
            code="MODEL_ENCODER_PARAMETER_MISSING",
            stage="model",
            hint=(
                "Provide a model artifact, or a schema containing the legacy "
                "parameters required for schema-only Model IR construction."
            ),
            path=path,
        )
    if isinstance(error, InvalidModelIRParameterError):
        return VerificationRuntimeError(
            str(error),
            code="MODEL_ENCODER_PARAMETER_UNSUPPORTED",
            stage="model",
            hint="Use source parameters that define a valid supported Model IR.",
            path=path,
        )
    return VerificationRuntimeError(
        str(error),
        code="MODEL_ENCODING_FAILED",
        stage="model",
        hint="Inspect the chained Model IR construction error.",
        path=path,
    )


def _public_model_ir_lowering_error(
    error: ModelIRLoweringError,
    *,
    model_path: Path | None,
) -> VerificationRuntimeError:
    """Normalize compiler Model IR lowering failures at the model boundary."""

    path = str(model_path) if model_path is not None else None
    if isinstance(error, UnsupportedModelIRLoweringError):
        return VerificationRuntimeError(
            str(error),
            code="MODEL_ENCODER_UNSUPPORTED",
            stage="model",
            hint="Use a Model IR/schema pair with a supported compiler lowering.",
            path=path,
        )
    if isinstance(error, InvalidModelIRLoweringError):
        return VerificationRuntimeError(
            str(error),
            code="MODEL_ENCODER_OUTPUT_INVALID",
            stage="model",
            hint="The selected Model IR lowering emitted invalid model assumptions.",
            path=path,
        )
    return VerificationRuntimeError(
        str(error),
        code="MODEL_ENCODING_FAILED",
        stage="model",
        hint="Inspect the chained Model IR lowering error.",
        path=path,
    )


def _public_model_semantic_error(
    error: ModelSemanticLoweringError,
    *,
    model_path: Path | None,
) -> VerificationRuntimeError:
    path = str(model_path) if model_path is not None else None
    if isinstance(error, UnsupportedModelSemanticProfileError):
        return VerificationRuntimeError(
            str(error),
            code="MODEL_SEMANTIC_PROFILE_UNSUPPORTED",
            stage="model",
            hint=(
                "Use a model family with a registered semantic profile for the "
                "requested output observable."
            ),
            path=path,
        )
    if isinstance(error, UnsupportedObservableLoweringError):
        return VerificationRuntimeError(
            str(error),
            code="MODEL_OBSERVABLE_UNSUPPORTED",
            stage="model",
            hint=(
                "Use an observable and comparison supported by the selected "
                "model-family semantic profile."
            ),
            path=path,
        )
    if isinstance(error, InvalidModelSemanticProfileError):
        return VerificationRuntimeError(
            str(error),
            code="MODEL_SEMANTIC_PROFILE_INVALID",
            stage="model",
            hint=(
                "Check that the model schema satisfies the selected semantic "
                "profile contract."
            ),
            path=path,
        )
    if isinstance(error, MissingModelSemanticsError):
        return VerificationRuntimeError(
            str(error),
            code="MODEL_SEMANTIC_LOWERING_INCOMPLETE",
            stage="model",
            hint=(
                "The selected integration did not lower every public model "
                "observable; inspect the chained integration error."
            ),
            path=path,
        )
    return VerificationRuntimeError(
        str(error),
        code="MODEL_SEMANTIC_LOWERING_FAILED",
        stage="model",
        hint="Inspect the chained model-semantic error for diagnostic details.",
        path=path,
    )


def _public_numeric_compatibility_error(
    error: NumericCompatibilityError,
    *,
    model_path: Path | None,
) -> VerificationRuntimeError:
    code = (
        "NUMERIC_COMPATIBILITY_AMBIGUOUS"
        if isinstance(error, AmbiguousCompatibilityRuleError)
        else "NUMERIC_COMPATIBILITY_INVALID"
    )
    hint = (
        "Remove equally specific compatibility rules so one deterministic route "
        "wins."
        if isinstance(error, AmbiguousCompatibilityRuleError)
        else "Check the registered numeric compatibility descriptors and rules."
    )
    return VerificationRuntimeError(
        str(error),
        code=code,
        stage="compatibility",
        hint=hint,
        path=str(model_path) if model_path is not None else None,
    )


def _public_backend_routing_error(
    error: BackendRoutingError,
    *,
    model_path: Path | None,
) -> VerificationRuntimeError:
    path = str(model_path) if model_path is not None else None
    if isinstance(error, NumericCompatibilityRouteError):
        return VerificationRuntimeError(
            str(error),
            code="NUMERIC_COMPATIBILITY_ROUTE_UNSUPPORTED",
            stage="compatibility",
            hint=(
                "Use a framework, encoder, backend, and property combination "
                "covered by an executable numeric compatibility rule."
            ),
            path=path,
        )
    if isinstance(error, BackendNotRegisteredError):
        return VerificationRuntimeError(
            str(error),
            code="BACKEND_NOT_REGISTERED",
            stage="routing",
            hint=(
                "Use a registered backend from the public V1 profile or provide "
                "a complete backend integration."
            ),
            path=path,
        )
    if isinstance(error, NoCompatibleBackendError):
        return VerificationRuntimeError(
            str(error),
            code="BACKEND_ROUTE_UNSUPPORTED",
            stage="routing",
            hint=(
                "Choose a backend whose declared capabilities satisfy the "
                "property and execution-policy requirements."
            ),
            path=path,
        )
    return VerificationRuntimeError(
        str(error),
        code="BACKEND_ROUTING_FAILED",
        stage="routing",
        hint="Inspect the chained backend-routing error for diagnostic details.",
        path=path,
    )


def _public_backend_runner_error(
    error: BackendRunnerNotRegisteredError,
) -> VerificationRuntimeError:
    return VerificationRuntimeError(
        str(error),
        code="BACKEND_RUNNER_NOT_REGISTERED",
        stage="backend",
        hint=(
            "Register a runner for the selected backend or use the default "
            "runner registry."
        ),
    )


def _public_backend_policy_error(
    error: BackendExecutionPolicyError,
) -> VerificationConfigurationError:
    return VerificationConfigurationError(
        str(error),
        code="BACKEND_EXECUTION_POLICY_INVALID",
        stage="backend",
        hint=(
            "Use backend_options only for backend-native controls; configure "
            "timeout, resources, cancellation, and seed through their generic "
            "execution-policy fields."
        ),
    )


def _public_backend_translation_error(
    error: BackendTranslationError,
) -> VerificationRuntimeError:
    if isinstance(error, UnsupportedBackendRequirementsError):
        code = "BACKEND_TRANSLATION_REQUIREMENTS_UNSUPPORTED"
        hint = (
            "Route the task through a backend whose declared capabilities "
            "satisfy every IR2 requirement."
        )
    elif isinstance(error, BackendSymbolCollisionError):
        code = "BACKEND_SYMBOL_COLLISION"
        hint = (
            "Inspect the chained backend translation error and the structured "
            "symbol identities that collided."
        )
    elif isinstance(error, UnsupportedScalarExpressionError):
        code = "BACKEND_SCALAR_EXPRESSION_UNSUPPORTED"
        hint = "Use scalar expressions within the selected backend numeric profile."
    else:
        code = "BACKEND_TRANSLATION_FAILED"
        hint = "Inspect the chained backend-translation error for details."
    return VerificationRuntimeError(
        str(error),
        code=code,
        stage="backend",
        hint=hint,
    )


def _public_backend_execution_error(
    error: BackendExecutionError,
) -> VerificationRuntimeError:
    return VerificationRuntimeError(
        str(error),
        code="BACKEND_EXECUTION_FAILED",
        stage="backend",
        hint=(
            "Inspect the chained backend error and its execution evidence; "
            "retry only after resolving the technical backend failure."
        ),
    )


def _validate_target_contract(effective_target: str, schema_target: str) -> None:
    if effective_target != schema_target:
        raise VerificationConfigurationError(
            f"Effective target '{effective_target}' does not match model schema "
            f"target '{schema_target}'. The property and model assumptions would "
            "otherwise refer to different outputs.",
            code="TARGET_SCHEMA_MISMATCH",
            stage="model",
            hint=(
                "Use a target override supported by the effective model/schema, "
                "or remove the override."
            ),
        )


def _resolve_anchor_bindings(
    program: ProgramNode,
    *,
    schema: ModelSchema,
    anchor_source: AnchorSource | None,
    anchor_resolver: AnchorResolver | None,
    dataset_fallback: AnchorSource | None,
) -> Mapping[str, ResolvedAnchorBinding]:
    environment = AnchorValidator(model_schema=schema).validate(program.anchors)
    requests = tuple(
        AnchorLookupRequest(
            name=point.name,
            key=point.reference.key,
            value=point.reference.value,
        )
        for point in environment.global_anchors()
        if point.binding_kind is PointBindingKind.REFERENCED_ANCHOR
        and point.reference is not None
    )
    if anchor_source is not None and anchor_resolver is not None:
        raise VerificationConfigurationError(
            "Provide either 'anchor_source' or 'anchor_resolver', not both"
        )
    if not requests:
        return frozen_mapping({})

    if anchor_resolver is None:
        effective_source = (
            anchor_source if anchor_source is not None else dataset_fallback
        )
        if effective_source is None:
            raise AnchorResolutionError(
                "Referenced anchors require anchor_source=..., "
                "anchor_resolver=..., or a compatible dataset=... artifact",
                code="ANCHOR_SOURCE_REQUIRED",
            )
        anchor_resolver = DataFrameAnchorResolver(effective_source)

    resolved = anchor_resolver.resolve(requests, schema=schema)
    return _validate_resolver_output(requests, resolved)


def _validate_resolver_output(
    requests: tuple[AnchorLookupRequest, ...],
    resolved: Mapping[str, ResolvedAnchorBinding],
) -> Mapping[str, ResolvedAnchorBinding]:
    expected = tuple(request.name for request in requests)
    missing = [name for name in expected if name not in resolved]
    if missing:
        raise AnchorResolutionError(
            "Anchor resolver did not return binding(s): " + ", ".join(missing),
            code="ANCHOR_RESOLVER_INCOMPLETE",
        )
    unexpected = [name for name in resolved if name not in set(expected)]
    if unexpected:
        raise AnchorResolutionError(
            "Anchor resolver returned unexpected binding(s): " + ", ".join(unexpected),
            code="ANCHOR_RESOLVER_UNEXPECTED",
        )
    return frozen_mapping({name: resolved[name] for name in expected})
