from __future__ import annotations

from toetra._compiler.ir.ir2.context import IR2BuildContext
from toetra._compiler.ir.ir2.enums import NormalFormKind
from toetra._compiler.ir.ir2.run_ir2 import run_ir2
from toetra._compiler.semantic.types.enums import EnumDataType


def _requirements(source: str):
    return run_ir2(
        source,
        context=IR2BuildContext(preferred_normal_form=NormalFormKind.NNF),
    )[0].requirements


def test_requirements_detect_affine_domain_arithmetic() -> None:
    requirements = _requirements("""
        model := "model.onnx"
        target := MyTarget
        margin := 1.5

        [LOGIC]:
        forall x0
            with domain(x0.a: [x0.b - margin, x0.b + margin])
            => x0.a <= 10
        """)

    assert requirements.requires_affine_arithmetic is True
    assert requirements.requires_nonlinear_arithmetic is False
    assert requirements.requires_symbolic_division is False
    assert EnumDataType.FLOAT in requirements.required_scalar_sorts


def test_requirements_detect_nonlinear_property_arithmetic() -> None:
    requirements = _requirements("""
        model := "model.onnx"
        target := MyTarget

        [LOGIC]:
        forall x0 => x0.a * x0.b <= target
        """)

    assert requirements.requires_nonlinear_arithmetic is True
    assert requirements.requires_affine_arithmetic is False
    assert requirements.requires_symbolic_division is False


def test_requirements_detect_symbolic_division() -> None:
    requirements = _requirements("""
        model := "model.onnx"
        target := MyTarget

        [LOGIC]:
        forall x0 => x0.a / x0.b <= target
        """)

    assert requirements.requires_symbolic_division is True
    assert requirements.requires_nonlinear_arithmetic is False


def test_requirements_detect_symbolic_finite_set_categories() -> None:
    requirements = _requirements("""
        model := "model.onnx"
        target := MyTarget

        [LOGIC]:
        forall x0 with domain(x0.region: {EU, US}) => target <= 10
        """)

    assert requirements.requires_domain_assumptions is True
    assert requirements.requires_finite_set_membership is True
    assert requirements.requires_symbolic_categories is True
