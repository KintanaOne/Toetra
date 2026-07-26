from __future__ import annotations

from toetra._backends.defaults import create_default_backend_registry
from toetra._backends.router import BackendRouter
from toetra._compatibility.defaults import (
    SKLEARN_BINARY_LOGISTIC_EXACT_PROBABILITY_RULE_ID,
    SKLEARN_BINARY_LOGISTIC_PROBABILITY_RULE_ID,
)
from toetra._compatibility.model import NumericCompatibilityContext
from toetra._compiler.ir.ir2.run_ir2 import run_ir2_with_model_schema
from toetra._models.compatibility import framework_model_descriptor
from toetra._models.encoder.profile import model_encoder_descriptor
from toetra._models.encoder.sklearn.logistic import SklearnLogisticRegressionEncoder
from test.fixtures.binary_classification import (
    binary_probability_property,
    make_sklearn_logistic_schema,
)


def _route(threshold: str):
    schema = make_sklearn_logistic_schema()
    task = run_ir2_with_model_schema(
        binary_probability_property(threshold=threshold),
        schema=schema,
    )[0]
    context = NumericCompatibilityContext(
        source_model=framework_model_descriptor(schema),
        model_encoder=model_encoder_descriptor(SklearnLogisticRegressionEncoder()),
    )
    return BackendRouter(create_default_backend_registry()).route(
        task,
        numeric_compatibility_context=context,
    )


def test_non_exact_probability_threshold_uses_directed_bound_rule() -> None:
    route = _route("0.8")

    assert route.numeric_compatibility is not None
    assert (
        route.numeric_compatibility.matched_rule_id
        == SKLEARN_BINARY_LOGISTIC_PROBABILITY_RULE_ID
    )


def test_half_probability_threshold_uses_exact_boundary_rule() -> None:
    route = _route("0.5")

    assert route.numeric_compatibility is not None
    assert (
        route.numeric_compatibility.matched_rule_id
        == SKLEARN_BINARY_LOGISTIC_EXACT_PROBABILITY_RULE_ID
    )
