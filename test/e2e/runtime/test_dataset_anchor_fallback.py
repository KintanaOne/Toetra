from __future__ import annotations

from collections.abc import Mapping, Sequence

import joblib
import pandas as pd
import pytest
from sklearn.linear_model import LinearRegression

from toetra._backends.results import VerificationStatus
from toetra._runtime import (
    AnchorLookupRequest,
    AnchorResolutionError,
    AnchorResolver,
    verify,
)
from toetra._compiler.semantic.symbols.point import ResolvedAnchorBinding
from toetra._compiler.semantic.types.enums import EnumDataType
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
=> target <= 3.1 using Z3
"""


class _IncompleteResolver(AnchorResolver):
    def resolve(
        self,
        requests: Sequence[AnchorLookupRequest],
        *,
        schema: ModelSchema,
    ) -> Mapping[str, ResolvedAnchorBinding]:
        return {}


def _artifacts(tmp_path, *, anchor_value: float = 1.0):
    training = pd.DataFrame(
        {
            "id": ["R-00", "R-42", "R-99"],
            "a": [0.0, anchor_value, 3.0],
            "score": [1.0, 2.0 * anchor_value + 1.0, 7.0],
        }
    )
    model = LinearRegression().fit(training[["a"]], training["score"])
    model_path = tmp_path / "linear.joblib"
    dataset_path = tmp_path / "reference.csv"
    joblib.dump(model, model_path)
    training.to_csv(dataset_path, index=False)
    return model_path, dataset_path


def test_run_ref_008_dataset_is_default_anchor_source(tmp_path) -> None:
    model_path, dataset_path = _artifacts(tmp_path)

    session = verify(_SOURCE, model=model_path, dataset=dataset_path)

    assert session.reports[0].status is VerificationStatus.PROVED
    assert tuple(session.schema.features) == ("a",)
    assert (
        EnumDataType.STRING
        not in session.executions[0].task.requirements.required_scalar_sorts
    )
    provenance = session.anchor_resolutions["row"].provenance
    assert provenance is not None
    assert provenance.source_kind == "csv"
    assert provenance.source_reference == str(dataset_path.resolve())


def test_run_ref_009_explicit_anchor_source_overrides_dataset(tmp_path) -> None:
    model_path, dataset_path = _artifacts(tmp_path, anchor_value=2.0)
    explicit_source = pd.DataFrame({"id": ["R-42"], "a": [1.0]})

    session = verify(
        _SOURCE,
        model=model_path,
        dataset=dataset_path,
        anchor_source=explicit_source,
    )

    assert session.reports[0].status is VerificationStatus.PROVED
    provenance = session.anchor_resolutions["row"].provenance
    assert provenance is not None
    assert provenance.source_kind == "dataframe"
    assert provenance.source_reference is None


def test_custom_anchor_resolver_has_priority_over_dataset(tmp_path) -> None:
    model_path, dataset_path = _artifacts(tmp_path)

    with pytest.raises(AnchorResolutionError) as caught:
        verify(
            _SOURCE,
            model=model_path,
            dataset=dataset_path,
            anchor_resolver=_IncompleteResolver(),
        )

    assert caught.value.code == "ANCHOR_RESOLVER_INCOMPLETE"
