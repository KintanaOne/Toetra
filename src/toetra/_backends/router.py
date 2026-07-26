from __future__ import annotations

from dataclasses import dataclass

from toetra._backends.capabilities import BackendCapabilities
from toetra._backends.errors import BackendNotRegisteredError, NoCompatibleBackendError
from toetra._backends.execution import BackendExecutionPolicy
from toetra._backends.registry import BackendRegistry
from toetra._compatibility.defaults import create_default_numeric_compatibility_registry
from toetra._compatibility.descriptors import PropertyNumericRequirements
from toetra._compatibility.inspection import contains_non_finite_numeric_values
from toetra._compatibility.model import (
    NumericCompatibilityAssessment,
    NumericCompatibilityContext,
    NumericCompatibilityQuery,
)
from toetra._compatibility.registry import NumericCompatibilityRegistry
from toetra._compiler.ir.ir2.dsl.nodes import VerificationTaskIR2
from toetra._language.vocabulary.backends import EnumBackend


@dataclass(frozen=True)
class BackendRoute:
    """Routing decision produced from an IR2-compatible task."""

    backend: EnumBackend
    capabilities: BackendCapabilities
    reason: str
    numeric_compatibility: NumericCompatibilityAssessment | None = None


class BackendRouter:
    """Select a backend from capabilities and task-local semantic contracts."""

    def __init__(
        self,
        registry: BackendRegistry | None = None,
        *,
        numeric_compatibility_registry: NumericCompatibilityRegistry | None = None,
    ):
        self.registry = registry or BackendRegistry()
        self.numeric_compatibility_registry = (
            numeric_compatibility_registry
            or create_default_numeric_compatibility_registry()
        )

    def route(
        self,
        task: VerificationTaskIR2,
        *,
        numeric_compatibility_context: NumericCompatibilityContext | None = None,
        execution_policy: BackendExecutionPolicy | None = None,
    ) -> BackendRoute:
        resolved_execution_policy = execution_policy or BackendExecutionPolicy()
        requested_backend = task.backend
        if requested_backend is not None:
            return self._route_requested_backend(
                task,
                requested_backend,
                numeric_compatibility_context=numeric_compatibility_context,
                execution_policy=resolved_execution_policy,
            )
        return self._route_any_compatible_backend(
            task,
            numeric_compatibility_context=numeric_compatibility_context,
            execution_policy=resolved_execution_policy,
        )

    def _route_requested_backend(
        self,
        task: VerificationTaskIR2,
        backend: EnumBackend,
        *,
        numeric_compatibility_context: NumericCompatibilityContext | None,
        execution_policy: BackendExecutionPolicy,
    ) -> BackendRoute:
        capabilities = self.registry.get(backend)
        if capabilities is None:
            raise BackendNotRegisteredError(
                f"Requested backend '{backend.value}' is not registered"
            )

        incompatibilities = capabilities.incompatibilities(task.requirements)
        execution_incompatibilities = (
            capabilities.execution_capabilities.incompatibilities(execution_policy)
        )
        incompatibilities = incompatibilities + tuple(
            f"execution policy: {item}" for item in execution_incompatibilities
        )
        if incompatibilities:
            details = "; ".join(incompatibilities)
            raise NoCompatibleBackendError(
                f"Requested backend '{backend.value}' does not satisfy IR2 "
                f"requirements: {details}"
            )

        assessment = self._assess_numeric_compatibility(
            task, capabilities, numeric_compatibility_context
        )
        if assessment is not None and not assessment.is_executable:
            details = "; ".join(assessment.diagnostics) or assessment.summary
            raise NoCompatibleBackendError(
                f"Requested backend '{backend.value}' has no executable numeric "
                f"compatibility route: {details}"
            )

        reason = "requested backend satisfies IR2 requirements"
        if assessment is not None:
            reason += "; " + assessment.summary
        return BackendRoute(
            backend=capabilities.backend,
            capabilities=capabilities,
            reason=reason,
            numeric_compatibility=assessment,
        )

    def _route_any_compatible_backend(
        self,
        task: VerificationTaskIR2,
        *,
        numeric_compatibility_context: NumericCompatibilityContext | None,
        execution_policy: BackendExecutionPolicy,
    ) -> BackendRoute:
        rejected: list[str] = []
        for capabilities in self.registry.all():
            incompatibilities = capabilities.incompatibilities(task.requirements)
            execution_incompatibilities = (
                capabilities.execution_capabilities.incompatibilities(execution_policy)
            )
            incompatibilities = incompatibilities + tuple(
                f"execution policy: {item}" for item in execution_incompatibilities
            )
            if incompatibilities:
                rejected.append(
                    f"{capabilities.backend.value}: " + "; ".join(incompatibilities)
                )
                continue

            assessment = self._assess_numeric_compatibility(
                task, capabilities, numeric_compatibility_context
            )
            if assessment is not None and not assessment.is_executable:
                rejected.append(
                    f"{capabilities.backend.value}: "
                    + ("; ".join(assessment.diagnostics) or assessment.summary)
                )
                continue

            reason = "first registered backend satisfying IR2 requirements"
            if assessment is not None:
                reason += "; " + assessment.summary
            return BackendRoute(
                backend=capabilities.backend,
                capabilities=capabilities,
                reason=reason,
                numeric_compatibility=assessment,
            )

        details = "; ".join(rejected) if rejected else "no backends registered"
        raise NoCompatibleBackendError(
            "No registered backend satisfies IR2 and numeric compatibility "
            "requirements: " + details
        )

    def _assess_numeric_compatibility(
        self,
        task: VerificationTaskIR2,
        capabilities: BackendCapabilities,
        context: NumericCompatibilityContext | None,
    ) -> NumericCompatibilityAssessment | None:
        if context is None:
            return None

        backend_profile = capabilities.numeric_profile
        if backend_profile is None:
            raise NoCompatibleBackendError(
                f"Backend '{capabilities.backend.value}' does not declare a "
                "numeric compatibility profile"
            )

        query = NumericCompatibilityQuery.build(
            context=context,
            backend=backend_profile,
            requirements=PropertyNumericRequirements.from_ir2(task.requirements),
            contains_non_finite_values=contains_non_finite_numeric_values(task),
        )
        return self.numeric_compatibility_registry.assess(
            query, backend_profile=backend_profile
        )
