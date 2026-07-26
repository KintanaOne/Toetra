from __future__ import annotations

from toetra._backends.z3_backend.symbols import Z3ModelQuantityIdentity
from toetra._backends.z3_backend.translator import Z3Translator
from toetra._compiler.ir.ir2.run_ir2 import run_ir2_with_model_schema
from test.fixtures.binary_classification import (
    binary_label_property,
    make_sklearn_logistic_schema,
)


def _task():
    return run_ir2_with_model_schema(
        binary_label_property(),
        schema=make_sklearn_logistic_schema(coefficient=2.0, intercept=-1.0),
    )[0]


def test_model_quantity_uses_one_shared_symbol_for_property_and_equation() -> None:
    translation = Z3Translator().translate(_task())
    quantity_symbols = {
        name: identity
        for name, identity in translation.symbol_identities.items()
        if isinstance(identity, Z3ModelQuantityIdentity)
    }
    assert set(quantity_symbols) == {
        "_model.decision[applicant]::<oriented_decision_value>"
    }
    identity = next(iter(quantity_symbols.values()))
    assert identity.evaluation.output_name == "decision"
    assert identity.evaluation.point.name == "applicant"
    assert identity.quantity_kind.value == "oriented_decision_value"


def test_model_quantity_symbol_metadata_is_not_public_output_metadata() -> None:
    translation = Z3Translator().translate(_task())
    metadata = translation.serialized_symbol_mapping()
    quantity_metadata = next(
        value for value in metadata.values() if value["kind"] == "model_quantity"
    )
    assert quantity_metadata == {
        "kind": "model_quantity",
        "model_identity": "credit.joblib",
        "point": {
            "name": "applicant",
            "binding_kind": "universal",
            "lexical_depth": 1,
            "generated": False,
        },
        "output_name": "decision",
        "quantity_kind": "oriented_decision_value",
        "semantic_profile_id": "binary_logistic_affine_classification",
    }


def test_model_quantity_symbols_remain_distinct_across_points() -> None:
    source = """\
model := "credit.joblib"
target := decision

[LOGIC]:
forall x0, x1 =>
    target[x0].label == "approved" and
    target[x1].label == "approved" using Z3
"""
    task = run_ir2_with_model_schema(
        source,
        schema=make_sklearn_logistic_schema(coefficient=1.0, intercept=0.0),
    )[0]
    translation = Z3Translator().translate(task)
    quantity_symbols = {
        name
        for name, identity in translation.symbol_identities.items()
        if isinstance(identity, Z3ModelQuantityIdentity)
    }
    assert quantity_symbols == {
        "_model.decision[x0]::<oriented_decision_value>",
        "_model.decision[x1]::<oriented_decision_value>",
    }
