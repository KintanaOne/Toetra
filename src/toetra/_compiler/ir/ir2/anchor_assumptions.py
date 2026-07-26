from __future__ import annotations

from toetra._compiler.ir.ir1.nodes import (
    AttributeExpressionIR,
    ComparisonIR,
    ConstantExpressionIR,
    PointBindingIR,
    ScopeIR,
)
from toetra._compiler.ir.ir2.enums import AssumptionSource
from toetra._compiler.ir.ir2.errors import InvalidIR2InputError
from toetra._compiler.ir.ir2.dsl.nodes import (
    AssumptionIR2,
    NNFFormulaIR2,
)
from toetra._language.vocabulary.operators import EnumComparisonOperator


class AnchorAssumptionEncoder:
    """Lower resolved concrete-anchor values to point-owned IR2 assumptions."""

    def encode_scope(self, scope: ScopeIR) -> tuple[AssumptionIR2, ...]:
        assumptions: list[AssumptionIR2] = []
        for point in scope.points:
            assumptions.extend(self._encode_point(point))
        return tuple(assumptions)

    def _encode_point(self, point: PointBindingIR) -> tuple[AssumptionIR2, ...]:
        if point.binding_kind not in {"inline_anchor", "referenced_anchor"}:
            return ()
        if point.binding_kind == "referenced_anchor" and not point.concrete_values:
            raise InvalidIR2InputError(
                f"Referenced anchor '{point.name}' reached IR2 without runtime "
                "resolution"
            )

        origin = point.binding_kind
        assumptions: list[AssumptionIR2] = []
        for index, concrete in enumerate(point.concrete_values):
            subject = AttributeExpressionIR(
                entity=point.name,
                feature=concrete.feature,
                dtype=concrete.literal.dtype,
                point=point,
            )
            value = ConstantExpressionIR(
                value=concrete.literal.value,
                dtype=concrete.literal.dtype,
            )
            metadata: dict[str, object] = {
                "origin": origin,
                "point": point.name,
                "binding_kind": point.binding_kind,
                "feature": concrete.feature,
                "value_index": index,
                "source_span": _source_span_metadata(point),
            }
            resolution = _resolution_metadata(point)
            if resolution is not None:
                metadata["lookup_provenance"] = resolution

            assumptions.append(
                AssumptionIR2(
                    source=AssumptionSource.SCOPE,
                    formula=NNFFormulaIR2(
                        expression=ComparisonIR(
                            left=subject,
                            op=EnumComparisonOperator.EQ,
                            right=value,
                        )
                    ),
                    description=(
                        f"{origin.replace('_', ' ')} fact: "
                        f"{point.name}.{concrete.feature} "
                        f"== {concrete.literal.value!r}"
                    ),
                    metadata=metadata,
                )
            )
        return tuple(assumptions)


def _source_span_metadata(point: PointBindingIR) -> dict[str, int] | None:
    span = point.source_span
    if span is None:
        return None
    return {
        "line": span.line,
        "column": span.column,
        "end_line": span.end_line,
        "end_column": span.end_column,
    }


def _resolution_metadata(point: PointBindingIR) -> dict[str, object] | None:
    resolution = point.resolution
    if resolution is None:
        return None
    return {
        "key": resolution.key,
        "lookup_value": resolution.lookup_value.value,
        "lookup_dtype": resolution.lookup_value.dtype.value,
        "source_kind": resolution.source_kind,
        "source_reference": resolution.source_reference,
        "row_index": resolution.row_index,
    }
