from typing import Any, cast

import pytest

from toetra._models.ir.affine import AffineModelIR


def test_zero_coefficients():
    model_ir = AffineModelIR(
        terms=(
            ("age", 0.0),
            ("income", 0.0),
        ),
        bias=0.0,
    )

    assert model_ir.terms == (
        ("age", 0.0),
        ("income", 0.0),
    )


def test_zero_bias():
    model_ir = AffineModelIR(
        terms=(("age", 0.5),),
        bias=0.0,
    )

    assert model_ir.bias == 0.0


def test_negative_coefficients():
    model_ir = AffineModelIR(
        terms=(
            ("age", -0.5),
            ("income", -0.3),
        ),
        bias=0.0,
    )

    assert model_ir.terms == (
        ("age", -0.5),
        ("income", -0.3),
    )


def test_negative_bias():
    model_ir = AffineModelIR(
        terms=(("age", 0.5),),
        bias=-1.0,
    )

    assert model_ir.bias == -1.0


def test_non_float_coefficient():
    with pytest.raises(TypeError):
        AffineModelIR(
            terms=(
                ("age", cast(Any, 1)),
                ("income", -0.3),
            ),
            bias=1.0,
        )


def test_non_float_bias():
    with pytest.raises(TypeError):
        AffineModelIR(
            terms=(("age", 0.5),),
            bias=cast(Any, 2),
        )


@pytest.mark.parametrize(
    "coefficient",
    [
        float("nan"),
        float("inf"),
        float("-inf"),
    ],
)
def test_non_finite_coefficient(coefficient: float):
    with pytest.raises(ValueError):
        AffineModelIR(
            terms=(("age", coefficient),),
            bias=0.0,
        )


@pytest.mark.parametrize(
    "bias",
    [
        float("nan"),
        float("inf"),
        float("-inf"),
    ],
)
def test_non_finite_bias(bias: float):
    with pytest.raises(ValueError):
        AffineModelIR(
            terms=(("age", 0.5),),
            bias=bias,
        )