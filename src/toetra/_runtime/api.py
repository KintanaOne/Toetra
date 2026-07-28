from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from toetra._backends.defaults import create_default_backend_registry
from toetra._backends.execution import BackendExecutionPolicy
from toetra._backends.registry import BackendRegistry
from toetra._backends.router import BackendRouter
from toetra._compatibility.model import NumericCompatibilityContext
from toetra._compatibility.policy import (
    apply_numeric_compatibility_policy,
    apply_semantic_lowering_policy,
)
from toetra._compatibility.registry import NumericCompatibilityRegistry
from toetra._compiler.ast.nodes.program import ProgramNode
from toetra._compiler.builder.errors import BuilderError
from toetra._compiler.builder.program import parse_program
from toetra._compiler.ir.ir2.context import IR2BuildContext
from toetra._compiler.ir.ir2.enums import NormalFormKind
from toetra._compiler.ir.ir2.run_ir2 import run_ir2_with_model_schema
from toetra._compiler.parser.errors import ParserError
from toetra._compiler.parser.parser import parse_toetra_code
from toetra._compiler.semantic.errors.errors import SemanticError
from toetra._provenance.builder import build_provenance_context
from toetra._reporting.builder import build_verification_report
from toetra._runtime.anchors import (
    AnchorLookupRequest,
    AnchorResolver,
    AnchorSource,
    DataFrameAnchorResolver,
)
from toetra._runtime.backends import (
    BackendRunnerRegistry,
    create_default_backend_runner_registry,
)
from toetra._runtime.errors import AnchorResolutionError, VerificationConfigurationError
from toetra._runtime.session import VerificationExecution, VerificationSession
from toetra._compiler.semantic.core.anchors import AnchorValidator
from toetra._compiler.semantic.symbols.point import (
    PointBindingKind,
    ResolvedAnchorBinding,
    frozen_mapping,
)
from toetra._models.compatibility import framework_model_descriptor
from toetra._models.encoder.context import ModelEncodingContext
from toetra._models.encoder.factory import ModelEncoderFactory
from toetra._models.encoder.profile import model_encoder_descriptor
from toetra._models.runtime.manager import ModelManager
from toetra._models.schema.model_schema import ModelSchema


@dataclass(frozen=True)
class _ResolvedModel:
    schema: ModelSchema
    model: object | None
    model_path: Path | None
    dataset_path: Path | None


@dataclass(frozen=True)
class _LoadedSpecification:
    source: str
    program: ProgramNode
    path: Path | None
    base_directory: Path
    model_reference: str
    target: str


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
    relative to the specification file. Referenced anchors require either a
    dedicated ``anchor_source`` (pandas DataFrame or CSV path) or a custom
    ``anchor_resolver``. When neither is provided, a compatible ``dataset``
    artifact is reused as the default anchor lookup source. This fallback is
    ergonomic only: src/toetra/_models/schema introspection and anchor lookup remain
    distinct runtime responsibilities. Custom framework/model integrations may
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
    loaded = _load_specification(specification)
    resolved = _resolve_model(
        loaded,
        model=model,
        dataset=dataset,
        target=target,
        schema=schema,
    )
    _validate_target_contract(loaded.target, resolved.schema.output_name)
    resolved_anchors = _resolve_anchor_bindings(
        loaded.program,
        schema=resolved.schema,
        anchor_source=anchor_source,
        anchor_resolver=anchor_resolver,
        dataset_fallback=resolved.dataset_path,
    )

    context = ir2_context or IR2BuildContext(preferred_normal_form=NormalFormKind.NNF)
    encoder_factory = model_encoder_factory or ModelEncoderFactory()
    selected_encoder = encoder_factory.create(resolved.schema)
    numeric_compatibility_context = NumericCompatibilityContext(
        source_model=framework_model_descriptor(resolved.schema),
        model_encoder=model_encoder_descriptor(selected_encoder),
    )
    tasks = run_ir2_with_model_schema(
        loaded.source,
        schema=resolved.schema,
        model_context=model_context,
        ir2_context=context,
        encoder_factory=encoder_factory,
        resolved_anchors=resolved_anchors,
    )

    router = BackendRouter(
        backend_registry or create_default_backend_registry(),
        numeric_compatibility_registry=numeric_compatibility_registry,
    )
    runners = runner_registry or create_default_backend_runner_registry()
    resolved_execution_policy = execution_policy or BackendExecutionPolicy()
    provenance_context = build_provenance_context(
        specification_source=loaded.source,
        specification_path=loaded.path,
        model_path=resolved.model_path,
        dataset_path=resolved.dataset_path,
        anchor_source=anchor_source,
        anchor_resolver=anchor_resolver,
        anchors_used=bool(resolved_anchors),
        schema=resolved.schema,
        ir2_context=context,
    )

    executions: list[VerificationExecution] = []
    for property_index, task in enumerate(tasks):
        route = router.route(
            task,
            numeric_compatibility_context=numeric_compatibility_context,
            execution_policy=resolved_execution_policy,
        )
        result = runners.require(route.backend).run(
            task,
            policy=resolved_execution_policy,
        )
        result = apply_numeric_compatibility_policy(
            result,
            route.numeric_compatibility,
        )
        result = apply_semantic_lowering_policy(
            result,
            task.lowering_evidence,
        )
        report = build_verification_report(
            task,
            route,
            result,
            property_index=property_index,
            provenance_context=provenance_context,
            schema=resolved.schema,
        )
        executions.append(
            VerificationExecution(
                task=task,
                route=route,
                result=result,
                report=report,
            )
        )

    return VerificationSession(
        source=loaded.source,
        specification_path=loaded.path,
        schema=resolved.schema,
        executions=tuple(executions),
        model=resolved.model,
        model_path=resolved.model_path,
        dataset_path=resolved.dataset_path,
        anchor_resolutions=resolved_anchors,
        provenance=provenance_context,
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
            raise FileNotFoundError(f"Toetra specification not found: {path}")
        resolved_path = path.resolve()
        source = resolved_path.read_text(encoding="utf-8")
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
) -> _ResolvedModel:
    if schema is not None:
        if model is not None or dataset is not None:
            raise VerificationConfigurationError(
                "Provide either 'schema' or model/dataset artifacts, not both"
            )
        if target is not None and target != schema.output_name:
            raise VerificationConfigurationError(
                f"Explicit target '{target}' does not match schema target "
                f"'{schema.output_name}'"
            )
        return _ResolvedModel(
            schema=schema,
            model=None,
            model_path=None,
            dataset_path=None,
        )

    resolved_target = target or loaded.target
    if resolved_target != loaded.target:
        raise VerificationConfigurationError(
            f"Explicit target '{resolved_target}' does not match Toetra header "
            f"target '{loaded.target}'"
        )

    model_path = (
        _resolve_explicit_path(model)
        if model is not None
        else _resolve_header_model_path(loaded)
    )
    if not model_path.is_file():
        raise FileNotFoundError(f"Serialized model not found: {model_path}")

    dataset_path = _resolve_explicit_path(dataset) if dataset is not None else None
    if dataset_path is not None and not dataset_path.is_file():
        raise FileNotFoundError(f"Reference dataset not found: {dataset_path}")

    manager = ModelManager(
        model_path=model_path,
        dataset_path=dataset_path,
        output_name=resolved_target,
    )
    resolved_schema = manager.build_schema()
    return _ResolvedModel(
        schema=resolved_schema,
        model=manager.model,
        model_path=model_path.resolve(),
        dataset_path=(dataset_path.resolve() if dataset_path is not None else None),
    )


def _resolve_header_model_path(loaded: _LoadedSpecification) -> Path:
    candidate = Path(loaded.model_reference)
    if candidate.is_absolute():
        return candidate
    return loaded.base_directory / candidate


def _resolve_explicit_path(value: str | Path) -> Path:
    return Path(value).expanduser()


def _validate_target_contract(header_target: str, schema_target: str) -> None:
    if header_target != schema_target:
        raise VerificationConfigurationError(
            f"Toetra header target '{header_target}' does not match model schema "
            f"target '{schema_target}'. The property and model assumptions would "
            "otherwise refer to different outputs."
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
