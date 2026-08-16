from dataclasses import FrozenInstanceError

import pytest

from toetra._models.ir.affine import AffineModelIR


def test_bias_cannot_be_reassigned():
    model_ir = AffineModelIR(
        terms=(("age", 0.5),),
        bias=0.0,
    )

    with pytest.raises(FrozenInstanceError):
        model_ir.bias = 1.0  # type: ignore[misc]


def test_terms_cannot_be_reassigned():
    model_ir = AffineModelIR(
        terms=(("age", 0.5),),
        bias=0.0,
    )

    with pytest.raises(FrozenInstanceError):
        model_ir.terms = (("income", 1.0),)  # type: ignore[misc]


def test_term_sequence_cannot_be_mutated():
    model_ir = AffineModelIR(
        terms=(
            ("age", 0.5),
            ("income", -0.3),
        ),
        bias=0.0,
    )

    assert isinstance(model_ir.terms, tuple)


def test_affine_terms_are_immutable_tuples():
    model_ir = AffineModelIR(
        terms=(("age", 0.5),),
        bias=0.0,
    )

    assert isinstance(model_ir.terms[0], tuple)