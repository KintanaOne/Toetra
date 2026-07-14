from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from dsl.backends.defaults import create_default_backend_registry
from dsl.backends.registry import BackendRegistry
from dsl.backends.router import BackendRouter
from dsl.builder.program import parse_program
from dsl.ir.ir2.context import IR2BuildContext
from dsl.ir.ir2.enums import NormalFormKind
from dsl.ir.ir2.run_ir2 import run_ir2_with_model_schema
from dsl.parser.parser import parse_forml_code
from dsl.reporting import build_verification_report
from dsl.runtime.backends import (
    BackendRunnerRegistry,
    create_default_backend_runner_registry,
)
from dsl.runtime.errors import VerificationConfigurationError
from dsl.runtime.session import VerificationExecution, VerificationSession
from model.encoder.context import ModelEncodingContext
from model.runtime.manager import ModelManager
from model.schema.model_schema import ModelSchema


@dataclass(frozen=True)
class _ResolvedModel:
    schema: ModelSchema
    model: object | None
    model_path: Path | None
    dataset_path: Path | None


@dataclass(frozen=True)
class _LoadedSpecification:
    source: str
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
    ir2_context: IR2BuildContext | None = None,
    backend_registry: BackendRegistry | None = None,
    runner_registry: BackendRunnerRegistry | None = None,
) -> VerificationSession:
    """Verify every property from a FORML source or ``.forml`` file.

    A caller may provide an already normalized ``ModelSchema`` or let FORML
    build one from a serialized model. When ``model`` is omitted for a file
    specification, the model reference from the FORML header is resolved
    relative to the specification file.
    """

    loaded = _load_specification(specification)
    resolved = _resolve_model(
        loaded,
        model=model,
        dataset=dataset,
        target=target,
        schema=schema,
    )
    _validate_target_contract(loaded.target, resolved.schema.target)

    context = ir2_context or IR2BuildContext(preferred_normal_form=NormalFormKind.NNF)
    tasks = run_ir2_with_model_schema(
        loaded.source,
        schema=resolved.schema,
        model_context=model_context,
        ir2_context=context,
    )

    router = BackendRouter(backend_registry or create_default_backend_registry())
    runners = runner_registry or create_default_backend_runner_registry()

    executions: list[VerificationExecution] = []
    for property_index, task in enumerate(tasks):
        route = router.route(task)
        result = runners.require(route.backend).run(task)
        report = build_verification_report(
            task,
            route,
            result,
            property_index=property_index,
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
    )


def _load_specification(specification: str | Path) -> _LoadedSpecification:
    path = _specification_path(specification)
    if path is not None:
        if not path.is_file():
            raise FileNotFoundError(f"FORML specification not found: {path}")
        resolved_path = path.resolve()
        source = resolved_path.read_text(encoding="utf-8")
        base_directory = resolved_path.parent
    else:
        source = str(specification)
        resolved_path = None
        base_directory = Path.cwd()

    program = parse_program(parse_forml_code(source))
    return _LoadedSpecification(
        source=source,
        path=resolved_path,
        base_directory=base_directory,
        model_reference=program.header.model,
        target=program.header.target,
    )


def _specification_path(specification: str | Path) -> Path | None:
    if isinstance(specification, Path):
        return specification

    if "\n" in specification or "\r" in specification:
        return None

    candidate = Path(specification)
    if candidate.exists() or candidate.suffix.lower() == ".forml":
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
        if target is not None and target != schema.target:
            raise VerificationConfigurationError(
                f"Explicit target '{target}' does not match schema target "
                f"'{schema.target}'"
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
            f"Explicit target '{resolved_target}' does not match FORML header "
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
        target_name=resolved_target,
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
            f"FORML header target '{header_target}' does not match model schema "
            f"target '{schema_target}'. The property and model assumptions would "
            "otherwise refer to different outputs."
        )
