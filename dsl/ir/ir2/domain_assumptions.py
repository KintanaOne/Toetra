from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from dsl.ir.ir1.nodes import (
    AttributeExpressionIR,
    ComparisonIR,
    ConstantExpressionIR,
    DomainEntryIR,
    DomainFiniteValueIR,
    DomainIR,
    FiniteSetDomainIR,
    IntervalDomainIR,
    LogicalIR,
    OrIR,
    ScalarExpressionIR,
    SymbolLiteralIR,
)
from dsl.ir.ir1.scalar import format_scalar_expression
from dsl.ir.ir2.enums import AssumptionSource
from dsl.ir.ir2.nodes import AssumptionIR2, NNFFormulaIR2
from dsl.language.vocabulary.domains import EnumBoundaryKind
from dsl.language.vocabulary.operators import EnumComparisonOperator
from dsl.semantic.types.enums import EnumDataType

NumericBoundValue = int | float


@dataclass(frozen=True)
class NumericFeatureBounds:
    """Compatibility input for the pre-typed-domain numeric API.

    New compiler code should pass ``DomainIR`` through ``encode_domain``.
    This type remains supported so existing callers do not need to migrate in
    the same patch.
    """

    entity: str
    feature: str
    lower: NumericBoundValue | None = None
    upper: NumericBoundValue | None = None


class DomainAssumptionEncoder:
    """Lower typed IR1 domains into provenanced IR2 assumptions.

    Interval entries are expanded into one assumption per endpoint so each
    generated comparison can retain its own open/closed-boundary provenance.

    Finite sets become one NNF disjunction of equality comparisons. Numeric,
    boolean and string constants stay typed, while unquoted categories remain
    ``SymbolLiteralIR`` values for later capability matching.

    No backend object is created here.
    """

    def encode_domain(self, domain: DomainIR | None) -> tuple[AssumptionIR2, ...]:
        if domain is None:
            return ()

        assumptions: list[AssumptionIR2] = []

        for entry_index, entry in enumerate(domain.entries):
            assumptions.extend(
                self._encode_domain_entry(
                    entry,
                    entry_index=entry_index,
                )
            )

        return tuple(assumptions)

    def encode(
        self,
        bounds: Iterable[NumericFeatureBounds],
    ) -> tuple[AssumptionIR2, ...]:
        """Encode the historical numeric-bound adapter."""

        assumptions: list[AssumptionIR2] = []

        for item in bounds:
            assumptions.extend(self._encode_legacy_bound(item))

        return tuple(assumptions)

    def _encode_domain_entry(
        self,
        entry: DomainEntryIR,
        *,
        entry_index: int,
    ) -> tuple[AssumptionIR2, ...]:
        entity = entry.entity
        if entity is None:
            raise ValueError(
                f"DomainIR entry {entry_index} must have an explicit entity."
            )

        if isinstance(entry.constraint, IntervalDomainIR):
            return self._encode_interval(
                entry,
                entry.constraint,
                entry_index=entry_index,
            )

        if isinstance(entry.constraint, FiniteSetDomainIR):
            return (
                self._encode_finite_set(
                    entry,
                    entry.constraint,
                    entry_index=entry_index,
                ),
            )

        raise TypeError(
            f"Unsupported DomainIR constraint: " f"{type(entry.constraint).__name__}"
        )

    def _encode_interval(
        self,
        entry: DomainEntryIR,
        interval: IntervalDomainIR,
        *,
        entry_index: int,
    ) -> tuple[AssumptionIR2, ...]:
        subject = self._subject(entry)

        lower_op = (
            EnumComparisonOperator.GTE
            if interval.lower_boundary is EnumBoundaryKind.CLOSED
            else EnumComparisonOperator.GT
        )
        upper_op = (
            EnumComparisonOperator.LTE
            if interval.upper_boundary is EnumBoundaryKind.CLOSED
            else EnumComparisonOperator.LT
        )

        lower = self._domain_comparison_assumption(
            subject=subject,
            op=lower_op,
            bound=interval.lower,
            description=(
                f"domain lower bound: {entry.entity}.{entry.feature} "
                f"{lower_op.value} {format_scalar_expression(interval.lower)}"
            ),
            metadata=self._provenance(
                entry,
                entry_index=entry_index,
                constraint_kind="interval",
                expansion_kind="lower_bound",
                boundary=interval.lower_boundary.value,
                operator=lower_op.value,
                expression=interval.lower,
            ),
        )
        upper = self._domain_comparison_assumption(
            subject=subject,
            op=upper_op,
            bound=interval.upper,
            description=(
                f"domain upper bound: {entry.entity}.{entry.feature} "
                f"{upper_op.value} {format_scalar_expression(interval.upper)}"
            ),
            metadata=self._provenance(
                entry,
                entry_index=entry_index,
                constraint_kind="interval",
                expansion_kind="upper_bound",
                boundary=interval.upper_boundary.value,
                operator=upper_op.value,
                expression=interval.upper,
            ),
        )

        return (lower, upper)

    def _encode_finite_set(
        self,
        entry: DomainEntryIR,
        finite_set: FiniteSetDomainIR,
        *,
        entry_index: int,
    ) -> AssumptionIR2:
        if not finite_set.values:
            raise ValueError(
                f"DomainIR finite set for {entry.entity}.{entry.feature} "
                "cannot be empty."
            )

        subject = self._subject(entry)
        comparisons: list[LogicalIR] = [
            ComparisonIR(
                left=subject,
                op=EnumComparisonOperator.EQ,
                right=self._finite_value_as_scalar(value),
            )
            for value in finite_set.values
        ]

        expression: LogicalIR
        if len(comparisons) == 1:
            expression = comparisons[0]
        else:
            expression = OrIR(operands=comparisons)

        members = [
            self._finite_member_metadata(value, member_index=index)
            for index, value in enumerate(finite_set.values)
        ]

        return AssumptionIR2(
            source=AssumptionSource.DOMAIN,
            formula=NNFFormulaIR2(expression=expression),
            description=(
                f"domain finite set: {entry.entity}.{entry.feature} in "
                f"{{{', '.join(self._format_finite_value(v) for v in finite_set.values)}}}"
            ),
            metadata={
                **self._provenance(
                    entry,
                    entry_index=entry_index,
                    constraint_kind="finite_set",
                    expansion_kind="membership_disjunction",
                ),
                "members": members,
                "member_count": len(members),
            },
        )

    @staticmethod
    def _subject(entry: DomainEntryIR) -> AttributeExpressionIR:
        if entry.entity is None:
            raise ValueError("DomainIR subjects must be explicitly qualified.")

        return AttributeExpressionIR(
            entity=entry.entity,
            feature=entry.feature,
            dtype=entry.dtype,
        )

    @staticmethod
    def _finite_value_as_scalar(value: DomainFiniteValueIR) -> ScalarExpressionIR:
        if isinstance(value, (ConstantExpressionIR, SymbolLiteralIR)):
            return value

        raise TypeError(f"Unsupported finite-set IR value: {type(value).__name__}")

    @staticmethod
    def _domain_comparison_assumption(
        *,
        subject: AttributeExpressionIR,
        op: EnumComparisonOperator,
        bound: ScalarExpressionIR,
        description: str,
        metadata: dict[str, Any],
    ) -> AssumptionIR2:
        return AssumptionIR2(
            source=AssumptionSource.DOMAIN,
            formula=NNFFormulaIR2(
                expression=ComparisonIR(
                    left=subject,
                    op=op,
                    right=bound,
                )
            ),
            description=description,
            metadata=metadata,
        )

    @staticmethod
    def _provenance(
        entry: DomainEntryIR,
        *,
        entry_index: int,
        constraint_kind: str,
        expansion_kind: str,
        boundary: str | None = None,
        operator: str | None = None,
        expression: ScalarExpressionIR | None = None,
    ) -> dict[str, Any]:
        metadata: dict[str, Any] = {
            "origin": "dsl_domain",
            "entry_index": entry_index,
            "entity": entry.entity,
            "feature": entry.feature,
            "constraint_kind": constraint_kind,
            "expansion_kind": expansion_kind,
        }

        if boundary is not None:
            metadata["boundary"] = boundary
        if operator is not None:
            metadata["operator"] = operator
        if expression is not None:
            metadata["expression"] = format_scalar_expression(expression)

        return metadata

    @staticmethod
    def _finite_member_metadata(
        value: DomainFiniteValueIR,
        *,
        member_index: int,
    ) -> dict[str, Any]:
        if isinstance(value, SymbolLiteralIR):
            return {
                "member_index": member_index,
                "kind": "symbolic_category",
                "value": value.name,
            }

        if isinstance(value, ConstantExpressionIR):
            return {
                "member_index": member_index,
                "kind": "constant",
                "value": value.value,
                "dtype": value.dtype.value,
                "source_kind": value.source_kind.value,
                "source_name": value.source_name,
            }

        raise TypeError(f"Unsupported finite-set value: {type(value).__name__}")

    @staticmethod
    def _format_finite_value(value: DomainFiniteValueIR) -> str:
        if isinstance(value, SymbolLiteralIR):
            return value.name
        if isinstance(value, ConstantExpressionIR):
            return repr(value.value)
        raise TypeError(f"Unsupported finite-set value: {type(value).__name__}")

    def _encode_legacy_bound(
        self,
        bound: NumericFeatureBounds,
    ) -> tuple[AssumptionIR2, ...]:
        self._validate_legacy_bound(bound)

        assumptions: list[AssumptionIR2] = []

        if bound.lower is not None:
            assumptions.append(
                self._legacy_comparison_assumption(
                    bound=bound,
                    op=EnumComparisonOperator.GTE,
                    value=bound.lower,
                    label=f"{bound.entity}.{bound.feature} >= {bound.lower}",
                    expansion_kind="lower_bound",
                )
            )

        if bound.upper is not None:
            assumptions.append(
                self._legacy_comparison_assumption(
                    bound=bound,
                    op=EnumComparisonOperator.LTE,
                    value=bound.upper,
                    label=f"{bound.entity}.{bound.feature} <= {bound.upper}",
                    expansion_kind="upper_bound",
                )
            )

        return tuple(assumptions)

    def _legacy_comparison_assumption(
        self,
        *,
        bound: NumericFeatureBounds,
        op: EnumComparisonOperator,
        value: NumericBoundValue,
        label: str,
        expansion_kind: str,
    ) -> AssumptionIR2:
        atom = ComparisonIR(
            left=AttributeExpressionIR(
                entity=bound.entity,
                feature=bound.feature,
            ),
            op=op,
            right=ConstantExpressionIR(
                value=value,
                dtype=(
                    EnumDataType.INT
                    if isinstance(value, int) and not isinstance(value, bool)
                    else EnumDataType.FLOAT
                ),
            ),
        )

        return AssumptionIR2(
            source=AssumptionSource.DOMAIN,
            formula=NNFFormulaIR2(expression=atom),
            description=f"numeric domain bound: {label}",
            metadata={
                "origin": "legacy_numeric_bounds",
                "entity": bound.entity,
                "feature": bound.feature,
                "constraint_kind": "interval",
                "expansion_kind": expansion_kind,
                "operator": op.value,
                "value": value,
            },
        )

    @staticmethod
    def _validate_legacy_bound(bound: NumericFeatureBounds) -> None:
        if not bound.entity:
            raise ValueError("NumericFeatureBounds.entity cannot be empty.")

        if not bound.feature:
            raise ValueError("NumericFeatureBounds.feature cannot be empty.")

        if bound.lower is None and bound.upper is None:
            raise ValueError(
                "NumericFeatureBounds must define at least one of lower or upper."
            )

        for label, value in (("lower", bound.lower), ("upper", bound.upper)):
            if value is not None and (
                isinstance(value, bool) or not isinstance(value, (int, float))
            ):
                raise TypeError(
                    f"NumericFeatureBounds.{label} must be int or float, "
                    f"got {type(value).__name__}."
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
