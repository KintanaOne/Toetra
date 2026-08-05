from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path

import pandas as pd
import pytest

from toetra._backends.results import VerificationStatus
from toetra._runtime.anchors import (
    AnchorLookupRequest,
    AnchorResolver,
)
from toetra._runtime.errors import (
    AnchorResolutionError,
    VerificationConfigurationError,
)
from toetra._runtime.api import verify
from toetra._compiler.semantic.symbols.point import ResolvedAnchorBinding
from toetra._compiler.semantic.types.enums import EnumDataType
from toetra._models.detector.model_framework import EnumModelFramework
from toetra._models.schema.feature_schema import FeatureSchema
from toetra._models.schema.model_schema import ModelSchema

_SOURCE = """
model := "linear.joblib"
target := score

anchor row := ref(
    key = "id",
    value = "R-42"
)

[BOUND]:
check_at row
=> target <= 3.0 using Z3
"""


def _schema() -> ModelSchema:
    return ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="LinearRegression",
        features={"a": FeatureSchema(name="a", dtype=EnumDataType.FLOAT)},
        target="score",
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


class _IncompleteResolver(AnchorResolver):
    def resolve(
        self,
        requests: Sequence[AnchorLookupRequest],
        *,
        schema: ModelSchema,
    ) -> Mapping[str, ResolvedAnchorBinding]:
        return {}


def test_verify_requires_anchor_input_when_dataset_fallback_is_unavailable() -> None:
    with pytest.raises(AnchorResolutionError) as caught:
        verify(_SOURCE, schema=_schema())

    assert caught.value.code == "ANCHOR_SOURCE_REQUIRED"


def test_verify_rejects_anchor_source_and_custom_resolver_together() -> None:
    with pytest.raises(VerificationConfigurationError, match="either 'anchor_source'"):
        verify(
            _SOURCE,
            schema=_schema(),
            anchor_source=pd.DataFrame({"id": ["R-42"], "a": [1.0]}),
            anchor_resolver=_IncompleteResolver(),
        )


def test_verify_rejects_incomplete_custom_resolver_output() -> None:
    with pytest.raises(AnchorResolutionError) as caught:
        verify(_SOURCE, schema=_schema(), anchor_resolver=_IncompleteResolver())

    assert caught.value.code == "ANCHOR_RESOLVER_INCOMPLETE"


def test_verify_resolves_ref_before_ir2_and_backend_execution() -> None:
    session = verify(
        _SOURCE,
        schema=_schema(),
        anchor_source=pd.DataFrame({"id": ["R-42"], "a": [1.0]}),
    )

    assert session.reports[0].status is VerificationStatus.PROVED
    assert tuple(session.anchor_resolutions) == ("row",)
    assumptions = session.executions[0].task.assumptions
    anchor_facts = [
        item
        for item in assumptions
        if item.metadata.get("origin") == "referenced_anchor"
    ]
    assert len(anchor_facts) == 1
    assert anchor_facts[0].metadata["point"] == "row"
    assert anchor_facts[0].metadata["feature"] == "a"
    assert anchor_facts[0].metadata["lookup_provenance"] == {
        "key": "id",
        "lookup_value": "R-42",
        "lookup_dtype": "string",
        "source_kind": "dataframe",
        "source_reference": None,
        "row_index": "0",
    }


def test_inline_anchor_does_not_require_external_resolution() -> None:
    source = """
    model := "linear.joblib"
    target := score

    anchor row := { a: 1.0 }

    [BOUND]:
    target[row] <= 3.0 using Z3
    """

    session = verify(source, schema=_schema())

    assert session.reports[0].status is VerificationStatus.PROVED
    assert not session.anchor_resolutions


def test_header_dataset_is_reused_as_anchor_fallback(tmp_path: Path) -> None:
    dataset_path = tmp_path / "reference.csv"
    pd.DataFrame({"id": ["R-42"], "a": [1.0]}).to_csv(
        dataset_path,
        index=False,
    )
    specification_path = tmp_path / "policy.toetra"
    specification_path.write_text(
        _SOURCE.replace(
            "target := score\n",
            'target := score\ndataset := "reference.csv"\n',
            1,
        ),
        encoding="utf-8",
    )

    session = verify(specification_path, schema=_schema())

    assert session.reports[0].status is VerificationStatus.PROVED
    assert session.dataset_path == dataset_path.resolve()
    assert tuple(session.anchor_resolutions) == ("row",)
