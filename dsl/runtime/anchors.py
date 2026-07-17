from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from numbers import Integral, Real
from pathlib import Path
from typing import TypeAlias

import numpy as np
import pandas as pd

from dsl.runtime.errors import AnchorResolutionError
from dsl.semantic.symbols.point import (
    AnchorResolutionProvenance,
    PointLiteral,
    ResolvedAnchorBinding,
    frozen_mapping,
)
from dsl.semantic.types.enums import EnumDataType
from model.schema.model_schema import ModelSchema

AnchorSource: TypeAlias = pd.DataFrame | str | Path


@dataclass(frozen=True)
class AnchorLookupRequest:
    """Validated lookup request extracted from one referenced anchor."""

    name: str
    key: str
    value: PointLiteral


class AnchorResolver(ABC):
    """Resolve referenced anchors into complete transformed-feature points."""

    @abstractmethod
    def resolve(
        self,
        requests: Sequence[AnchorLookupRequest],
        *,
        schema: ModelSchema,
    ) -> Mapping[str, ResolvedAnchorBinding]:
        """Resolve every request or raise :class:`AnchorResolutionError`."""


class DataFrameAnchorResolver(AnchorResolver):
    """Resolve anchors from one pandas data frame or CSV source."""

    def __init__(self, source: AnchorSource):
        self._frame, self._source_kind, self._source_reference = _load_source(source)

    def resolve(
        self,
        requests: Sequence[AnchorLookupRequest],
        *,
        schema: ModelSchema,
    ) -> Mapping[str, ResolvedAnchorBinding]:
        resolved: dict[str, ResolvedAnchorBinding] = {}
        for request in requests:
            resolved[request.name] = self._resolve_one(request, schema=schema)
        return frozen_mapping(resolved)

    def _resolve_one(
        self,
        request: AnchorLookupRequest,
        *,
        schema: ModelSchema,
    ) -> ResolvedAnchorBinding:
        if request.key not in self._frame.columns:
            raise AnchorResolutionError(
                f"Anchor '{request.name}' lookup key column '{request.key}' "
                "is missing from anchor_source",
                code="ANCHOR_KEY_MISSING",
                anchor_name=request.name,
            )

        matches = self._frame.loc[
            self._frame[request.key].eq(request.value.value).fillna(False)
        ]
        match_count = len(matches)
        if match_count == 0:
            raise AnchorResolutionError(
                f"Anchor '{request.name}' lookup found no row where "
                f"{request.key} == {request.value.value!r}",
                code="ANCHOR_MATCH_NOT_FOUND",
                anchor_name=request.name,
            )
        if match_count != 1:
            raise AnchorResolutionError(
                f"Anchor '{request.name}' lookup must match exactly one row; "
                f"found {match_count}",
                code="ANCHOR_MATCH_NOT_UNIQUE",
                anchor_name=request.name,
            )

        row = matches.iloc[0]
        row_index = matches.index[0]
        concrete_values: dict[str, PointLiteral] = {}
        for feature_name, feature in schema.features.items():
            if feature_name not in self._frame.columns:
                raise AnchorResolutionError(
                    f"Anchor '{request.name}' source is missing transformed model "
                    f"feature '{feature_name}'",
                    code="ANCHOR_FEATURE_MISSING",
                    anchor_name=request.name,
                )
            concrete_values[feature_name] = _coerce_feature_value(
                row[feature_name],
                expected=feature.dtype,
                anchor_name=request.name,
                feature_name=feature_name,
            )

        return ResolvedAnchorBinding(
            concrete_values=frozen_mapping(concrete_values),
            provenance=AnchorResolutionProvenance(
                key=request.key,
                lookup_value=request.value,
                source_kind=self._source_kind,
                source_reference=self._source_reference,
                row_index=repr(_python_scalar(row_index)),
            ),
        )


def _load_source(source: AnchorSource) -> tuple[pd.DataFrame, str, str | None]:
    if isinstance(source, pd.DataFrame):
        return source, "dataframe", None

    path = Path(source).expanduser()
    if not path.is_file():
        raise AnchorResolutionError(
            f"Anchor source not found: {path}",
            code="ANCHOR_SOURCE_NOT_FOUND",
        )
    if path.suffix.lower() != ".csv":
        raise AnchorResolutionError(
            "The default anchor resolver accepts only pandas.DataFrame or CSV paths",
            code="ANCHOR_SOURCE_UNSUPPORTED",
        )
    return pd.read_csv(path), "csv", str(path.resolve())


def _coerce_feature_value(
    value: object,
    *,
    expected: EnumDataType,
    anchor_name: str,
    feature_name: str,
) -> PointLiteral:
    if bool(pd.isna(value)):
        raise _dtype_error(anchor_name, feature_name, expected, value)

    normalized = _python_scalar(value)
    if expected is EnumDataType.FLOAT:
        if isinstance(normalized, Real) and not isinstance(
            normalized, (bool, np.bool_)
        ):
            return PointLiteral(value=float(normalized), dtype=EnumDataType.FLOAT)
    elif expected is EnumDataType.INT:
        if isinstance(normalized, Integral) and not isinstance(
            normalized, (bool, np.bool_)
        ):
            return PointLiteral(value=int(normalized), dtype=EnumDataType.INT)
    elif expected is EnumDataType.BOOL:
        if isinstance(normalized, (bool, np.bool_)):
            return PointLiteral(value=bool(normalized), dtype=EnumDataType.BOOL)
    elif expected is EnumDataType.STRING:
        if isinstance(normalized, str):
            return PointLiteral(value=normalized, dtype=EnumDataType.STRING)

    raise _dtype_error(anchor_name, feature_name, expected, normalized)


def _python_scalar(value: object) -> object:
    item = getattr(value, "item", None)
    if callable(item):
        try:
            return item()
        except (TypeError, ValueError):
            return value
    return value


def _dtype_error(
    anchor_name: str,
    feature_name: str,
    expected: EnumDataType,
    value: object,
) -> AnchorResolutionError:
    return AnchorResolutionError(
        f"Anchor '{anchor_name}' feature '{feature_name}' expects "
        f"{expected.value}, got {type(value).__name__}",
        code="ANCHOR_DTYPE_MISMATCH",
        anchor_name=anchor_name,
    )
