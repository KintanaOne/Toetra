from typing import Any, cast

import pytest

from toetra._models.ir.affine import AffineModelIR
from toetra._models.ir.base import ModelIR


def test_valid_affine_model_ir():
    model_ir = AffineModelIR(
        terms=(
            ("age", 0.7),
            ("income", -0.2),
        ),
        bias=0.0,
    )

    assert isinstance(model_ir, AffineModelIR)
    assert isinstance(model_ir, ModelIR)


def test_empty_terms():
    model_ir = AffineModelIR(
        terms=(),
        bias=0.0,
    )

    assert isinstance(model_ir, AffineModelIR)


def test_duplicate_feature_names():
    with pytest.raises(ValueError):
        AffineModelIR(
            terms=(
                ("age", 0.5),
                ("age", -0.3),
            ),
            bias=0.0,
        )


def test_non_string_feature_name():
    with pytest.raises(TypeError):
        AffineModelIR(
            terms=(
                (cast(Any, True), 0.5),
                ("income", -0.3),
            ),
            bias=0.0,
        )


def test_empty_feature_name():
    with pytest.raises(ValueError):
        AffineModelIR(
            terms=(
                ("", 0.5),
                ("income", -0.3),
            ),
            bias=0.0,
        )


@pytest.mark.parametrize(
    "feature",
    [
        "   ",
        " age",
        "age ",
        "\tage",
        "age\t",
        "\nage",
        "age\n",
    ],
)
def test_feature_name_with_surrounding_whitespace(feature: str):
    with pytest.raises(ValueError):
        AffineModelIR(
            terms=((feature, 0.5),),
            bias=0.0,
        )


def test_terms_must_be_tuple():
    with pytest.raises(TypeError):
        AffineModelIR(
            terms=cast(
                Any,
                [
                    ("age", 0.5),
                    ("income", -0.3),
                ],
            ),
            bias=0.0,
        )


def test_each_term_must_be_tuple():
    with pytest.raises(TypeError):
        AffineModelIR(
            terms=cast(
                Any,
                (
                    ["age", 0.5],
                    ("income", -0.3),
                ),
            ),
            bias=0.0,
        )


def test_term_must_have_exactly_two_elements():
    with pytest.raises(ValueError):
        AffineModelIR(
            terms=cast(
                Any,
                (
                    ("age", 0.5, "extra"),
                    ("income", -0.3),
                ),
            ),
            bias=0.0,
        )