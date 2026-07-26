from __future__ import annotations

import pytest

from toetra._backends.defaults import create_default_backend_registry
from toetra._backends.errors import NoCompatibleBackendError
from toetra._backends.router import BackendRouter
from toetra._backends.z3_backend.runner import VerificationStatus, Z3Runner
from toetra._backends.z3_backend.translator import Z3Translator
from toetra._compiler.ir.ir2.context import IR2BuildContext
from toetra._compiler.ir.ir2.enums import NormalFormKind
from toetra._compiler.ir.ir2.run_ir2 import run_ir2, run_ir2_with_model_schema
from toetra._compiler.semantic.types.enums import EnumDataType
from toetra._models.detector.model_framework import EnumModelFramework
from toetra._models.schema.feature_schema import FeatureSchema
from toetra._models.schema.model_schema import ModelSchema


def _compile(source: str):
    (task,) = run_ir2(
        source,
        context=IR2BuildContext(preferred_normal_form=NormalFormKind.NNF),
    )
    return task


def _route_and_run(source: str):
    task = _compile(source)
    route = BackendRouter(create_default_backend_registry()).route(task)
    result = Z3Runner().run(task)
    return task, route, result


def test_z3_proves_affine_property_with_addition_and_constant_product() -> None:
    task, route, result = _route_and_run("""
        model := "model.onnx"
        target := MyTarget

        [LOGIC]:
        forall x0
            with domain(
                x0.a: [0.0, 3.0],
                x0.b: [0.0, 2.0]
            )
            => x0.a + 2.0 * x0.b <= 7.0
            using Z3
        """)
    assert task.requirements.requires_affine_arithmetic is True
    assert route.capabilities.supports_affine_arithmetic is True
    assert result.status is VerificationStatus.PROVED


def test_z3_finds_counterexample_for_violated_affine_property() -> None:
    _, _, result = _route_and_run("""
        model := "model.onnx"
        target := MyTarget

        [LOGIC]:
        forall x0
            with domain(
                x0.a: [0.0, 3.0],
                x0.b: [0.0, 2.0]
            )
            => x0.a + 2.0 * x0.b <= 6.0
            using Z3
        """)
    assert result.status is VerificationStatus.COUNTEREXAMPLE
    assert result.model is not None
    assert {"x0.a", "x0.b"}.issubset(result.model)


def test_z3_proves_division_by_constant_property() -> None:
    task, _, result = _route_and_run("""
        model := "model.onnx"
        target := MyTarget

        [LOGIC]:
        forall x0
            with domain(x0.a: [0.0, 3.0])
            => x0.a / 2.0 <= 1.5
            using Z3
        """)
    assert task.requirements.requires_affine_arithmetic is True
    assert task.requirements.requires_symbolic_division is False
    assert result.status is VerificationStatus.PROVED


def test_z3_uses_specification_constant_as_literal_not_solver_variable() -> None:
    task = _compile("""
        model := "model.onnx"
        target := MyTarget

        weight := 2.0

        [LOGIC]:
        forall x0
            with domain(x0.a: [0.0, 3.0])
            => weight * x0.a <= 6.0
            using Z3
        """)
    BackendRouter(create_default_backend_registry()).route(task)
    translation = Z3Translator().translate(task)
    result = Z3Runner().run(task)
    assert set(translation.variables) == {"x0.a"}
    assert "weight" not in translation.variables
    assert result.status is VerificationStatus.PROVED


def test_z3_proves_property_from_arithmetic_domain_bound() -> None:
    _, _, result = _route_and_run("""
        model := "model.onnx"
        target := MyTarget

        margin := 1.0

        [LOGIC]:
        forall x0
            with domain(
                x0.b: [0.0, 3.0],
                x0.a: [x0.b - margin, x0.b + margin]
            )
            => x0.a - x0.b <= margin
            using Z3
        """)
    assert result.status is VerificationStatus.PROVED


def test_router_rejects_nonlinear_dsl_property_before_translation() -> None:
    task = _compile("""
        model := "model.onnx"
        target := MyTarget

        [LOGIC]:
        forall x0 => x0.a * x0.b <= 3.0 using Z3
        """)
    assert task.requirements.requires_nonlinear_arithmetic is True
    with pytest.raises(NoCompatibleBackendError, match="nonlinear arithmetic"):
        BackendRouter(create_default_backend_registry()).route(task)


def test_router_rejects_symbolic_division_before_translation() -> None:
    task = _compile("""
        model := "model.onnx"
        target := MyTarget

        [LOGIC]:
        forall x0 => x0.a / x0.b <= 3.0 using Z3
        """)
    assert task.requirements.requires_symbolic_division is True
    with pytest.raises(NoCompatibleBackendError, match="symbolic division"):
        BackendRouter(create_default_backend_registry()).route(task)


def test_router_rejects_symbolic_category_domain() -> None:
    task = _compile("""
        model := "model.onnx"
        target := MyTarget

        [LOGIC]:
        forall x0
            with domain(x0.region: {EU, US})
            => x0.region == "EU"
            using Z3
        """)
    assert task.requirements.requires_symbolic_categories is True
    with pytest.raises(NoCompatibleBackendError, match="symbolic categories"):
        BackendRouter(create_default_backend_registry()).route(task)


def test_z3_connects_user_target_arithmetic_to_affine_model_assumption() -> None:
    schema = ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="LinearRegression",
        features={
            "a": FeatureSchema(name="a", dtype=EnumDataType.FLOAT),
        },
        target="MyTarget",
        task="regression",
        target_dtype=EnumDataType.FLOAT,
        metadata={
            "linear": {
                "coef": [2.0],
                "intercept": 1.0,
                "feature_names": ["a"],
            }
        },
    )
    source = """
        model := "model.pkl"
        target := MyTarget

        [LOGIC]:
        forall x0
            with domain(x0.a: [0.0, 3.0])
            => target - 2.0 * x0.a == 1.0
            using Z3
    """
    (task,) = run_ir2_with_model_schema(
        source,
        schema=schema,
        ir2_context=IR2BuildContext(preferred_normal_form=NormalFormKind.NNF),
    )
    route = BackendRouter(create_default_backend_registry()).route(task)
    result = Z3Runner().run(task)
    assert task.requirements.requires_affine_arithmetic is True
    assert task.requirements.requires_model_assertions is True
    assert route.capabilities.supports_affine_arithmetic is True
    assert result.status is VerificationStatus.PROVED
