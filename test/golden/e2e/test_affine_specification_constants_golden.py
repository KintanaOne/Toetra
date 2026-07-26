from __future__ import annotations

import json
from pathlib import Path

from toetra._backends.defaults import create_default_backend_registry
from toetra._backends.router import BackendRouter
from toetra._backends.z3_backend.runner import VerificationStatus, Z3Runner
from toetra._compiler.ir.ir1.nodes import (
    ComparisonIR,
    ConstantExpressionIR,
    TargetExpressionIR,
)
from toetra._compiler.ir.ir2.context import IR2BuildContext
from toetra._compiler.ir.ir2.enums import NormalFormKind
from toetra._compiler.ir.ir2.run_ir2 import run_ir2_with_model_schema
from toetra._compiler.semantic.types.enums import EnumDataType
from toetra._models.detector.model_framework import EnumModelFramework
from toetra._models.schema.feature_schema import FeatureSchema
from toetra._models.schema.model_schema import ModelSchema
from test.fixtures.ir_schema_aware.ir_helpers import serialize_logical

FIXTURE_ROOT = Path("test/fixtures/end_to_end")
CASE_PATH = FIXTURE_ROOT / "cases/affine_specification_constants.toetra"
EXPECTED_PATH = FIXTURE_ROOT / "expected/affine_specification_constants.json"


def _linear_schema() -> ModelSchema:
    return ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="LinearRegression",
        features={
            "a": FeatureSchema(name="a", dtype=EnumDataType.FLOAT),
        },
        target="score",
        target_dtype=EnumDataType.FLOAT,
        task="regression",
        metadata={
            "linear": {
                "coef": [2.0],
                "intercept": 1.0,
                "feature_names": ["a"],
            }
        },
    )


def _contract() -> dict[str, object]:
    source = CASE_PATH.read_text(encoding="utf-8")
    (task,) = run_ir2_with_model_schema(
        source,
        schema=_linear_schema(),
        ir2_context=IR2BuildContext(preferred_normal_form=NormalFormKind.NNF),
    )
    route = BackendRouter(create_default_backend_registry()).route(task)
    result = Z3Runner().run(task)

    assert isinstance(task.spec_formula.expression, ComparisonIR)
    comparison = task.spec_formula.expression
    assert isinstance(comparison.left, TargetExpressionIR)
    assert isinstance(comparison.right, ConstantExpressionIR)

    return {
        "property_type": task.property_type.value,
        "backend": route.backend.value,
        "route_reason": route.reason,
        "semantics": task.semantics.value,
        "normal_form": task.normal_form.value,
        "status": result.status.value,
        "solver_status": result.solver_status,
        "message": result.message,
        "diagnostics": [diagnostic.code for diagnostic in result.diagnostics],
        "domain_assumption_count": task.metadata["domain_assumption_count"],
        "assumptions": [
            {
                "source": assumption.source.value,
                "description": assumption.description,
                "metadata": assumption.metadata,
            }
            for assumption in task.assumptions
        ],
        "requirements": {
            "affine_arithmetic": task.requirements.requires_affine_arithmetic,
            "model_assertions": task.requirements.requires_model_assertions,
            "domain_assumptions": task.requirements.requires_domain_assumptions,
            "scalar_sorts": sorted(
                dtype.value for dtype in task.requirements.required_scalar_sorts
            ),
        },
        "spec_formula": serialize_logical(task.spec_formula.expression),
        "target_dtype": comparison.left.dtype.value,
        "threshold_provenance": {
            "source_kind": comparison.right.source_kind.value,
            "source_name": comparison.right.source_name,
        },
    }


def test_affine_specification_constants_end_to_end_matches_golden() -> None:
    expected = json.loads(EXPECTED_PATH.read_text(encoding="utf-8"))

    actual = _contract()

    assert actual == expected
    assert actual["status"] == VerificationStatus.PROVED.value
