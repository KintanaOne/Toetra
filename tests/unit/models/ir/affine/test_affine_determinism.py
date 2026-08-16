from toetra._models.ir.affine import AffineModelIR


def test_term_order_is_preserved():
    terms = (
        ("age", 0.7),
        ("income", -0.2),
        ("score", 1.3),
    )

    model_ir = AffineModelIR(
        terms=terms,
        bias=0.5,
    )

    assert model_ir.terms == terms


def test_equivalent_affine_model_irs_are_equal():
    left = AffineModelIR(
        terms=(
            ("age", 0.7),
            ("income", -0.2),
        ),
        bias=0.5,
    )

    right = AffineModelIR(
        terms=(
            ("age", 0.7),
            ("income", -0.2),
        ),
        bias=0.5,
    )

    assert left == right


def test_different_term_order_is_structurally_distinct():
    left = AffineModelIR(
        terms=(
            ("age", 0.7),
            ("income", -0.2),
        ),
        bias=0.5,
    )

    right = AffineModelIR(
        terms=(
            ("income", -0.2),
            ("age", 0.7),
        ),
        bias=0.5,
    )

    assert left != right


def test_different_bias_is_structurally_distinct():
    left = AffineModelIR(
        terms=(("age", 0.7),),
        bias=0.5,
    )

    right = AffineModelIR(
        terms=(("age", 0.7),),
        bias=1.0,
    )

    assert left != right