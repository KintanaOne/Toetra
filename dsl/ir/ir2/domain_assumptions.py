from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from dsl.ir.ir1.nodes import ComparisonIR
from dsl.ir.ir2.enums import AssumptionSource
from dsl.ir.ir2.nodes import AssumptionIR2, NNFFormulaIR2
from dsl.language.vocabulary.operators import EnumComparisonOperator

NumericBoundValue = int | float


@dataclass(frozen=True)
class NumericFeatureBounds:
    """Numeric bounds for one symbolic feature.

    Example:
        0 <= x0.a <= 3

    is represented as:

        entity="x0"
        feature="a"
        lower=0
        upper=3
    """

    entity: str
    feature: str
    lower: NumericBoundValue | None = None
    upper: NumericBoundValue | None = None


class DomainAssumptionEncoder:
    """Encode simple numeric feature bounds into backend-independent IR2 assumptions.

    This encoder deliberately emits ComparisonIR atoms wrapped in NNFFormulaIR2.
    It does not create Z3 expressions and does not select a backend.
    """

    def encode(
        self,
        bounds: Iterable[NumericFeatureBounds],
    ) -> tuple[AssumptionIR2, ...]:
        assumptions: list[AssumptionIR2] = []

        for item in bounds:
            assumptions.extend(self._encode_bound(item))

        return tuple(assumptions)

    def _encode_bound(self, bound: NumericFeatureBounds) -> tuple[AssumptionIR2, ...]:
        self._validate_bound(bound)

        assumptions: list[AssumptionIR2] = []

        if bound.lower is not None:
            assumptions.append(
                self._comparison_assumption(
                    bound=bound,
                    op=EnumComparisonOperator.GTE,
                    value=bound.lower,
                    label=f"{bound.entity}.{bound.feature} >= {bound.lower}",
                )
            )

        if bound.upper is not None:
            assumptions.append(
                self._comparison_assumption(
                    bound=bound,
                    op=EnumComparisonOperator.LTE,
                    value=bound.upper,
                    label=f"{bound.entity}.{bound.feature} <= {bound.upper}",
                )
            )

        return tuple(assumptions)

    def _comparison_assumption(
        self,
        *,
        bound: NumericFeatureBounds,
        op: EnumComparisonOperator,
        value: NumericBoundValue,
        label: str,
    ) -> AssumptionIR2:
        atom = ComparisonIR(
            entity=bound.entity,
            feature=bound.feature,
            op=op,
            value=value,
        )

        return AssumptionIR2(
            source=AssumptionSource.DOMAIN,
            formula=NNFFormulaIR2(expression=atom),
            description=f"numeric domain bound: {label}",
            metadata={
                "entity": bound.entity,
                "feature": bound.feature,
                "operator": op.value,
                "value": value,
            },
        )

    def _validate_bound(self, bound: NumericFeatureBounds) -> None:
        if not bound.entity:
            raise ValueError("NumericFeatureBounds.entity cannot be empty.")

        if not bound.feature:
            raise ValueError("NumericFeatureBounds.feature cannot be empty.")

        if bound.lower is None and bound.upper is None:
            raise ValueError(
                "NumericFeatureBounds must define at least one of lower or upper."
            )

        if (
            bound.lower is not None
            and bound.upper is not None
            and bound.lower > bound.upper
        ):
            raise ValueError(
                f"Invalid numeric bounds for {bound.entity}.{bound.feature}: "
                f"lower={bound.lower} > upper={bound.upper}."
            )
