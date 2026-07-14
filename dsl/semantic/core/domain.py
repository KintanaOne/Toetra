from __future__ import annotations

from typing import TYPE_CHECKING

from dsl.ast.nodes.domain import (
    DomainNode,
    FiniteSetDomainNode,
    IntervalDomainNode,
    SymbolLiteralNode,
)
from dsl.ast.nodes.primitives import (
    AttributeNode,
    BinaryArithmeticNode,
    ConstantNode,
    NameRefNode,
    ScalarExpressionNode,
    TargetRefNode,
    UnaryArithmeticNode,
)
from dsl.language.vocabulary.domains import EnumBoundaryKind
from dsl.semantic.context.context import SemanticContext
from dsl.semantic.core.scalar_typing import ScalarAnalysis, ScalarTypeAnalyzer
from dsl.semantic.errors.errors import InvalidDomainError
from dsl.semantic.types.enums import EnumDataType

if TYPE_CHECKING:
    from model.schema.model_schema import ModelSchema


_NUMERIC_DTYPES = frozenset({EnumDataType.INT, EnumDataType.FLOAT})


class DomainValidator:
    """Validate a bound typed domain before IR1 lowering."""

    def __init__(self, model_schema: ModelSchema | None = None):
        self.model_schema = model_schema
        self.scalar_analyzer = ScalarTypeAnalyzer(model_schema=model_schema)

    def validate(
        self,
        domain: DomainNode | None,
        context: SemanticContext,
    ) -> None:
        if domain is None:
            return

        if not domain.entries:
            raise InvalidDomainError("Domain block must contain at least one entry")

        subjects: set[tuple[str, str]] = set()

        for entry in domain.entries:
            subject_key, subject_dtype = self._validate_subject(
                entry.subject,
                context,
            )

            if subject_key in subjects:
                entity, feature = subject_key
                raise InvalidDomainError(
                    f"Duplicate domain subject '{entity}.{feature}'"
                )
            subjects.add(subject_key)

            constraint = entry.constraint
            if isinstance(constraint, IntervalDomainNode):
                self._validate_interval(constraint)
                continue

            if isinstance(constraint, FiniteSetDomainNode):
                self._validate_finite_set(constraint, subject_dtype)
                continue

            raise InvalidDomainError(
                f"Unsupported domain constraint: {type(constraint).__name__}"
            )

    def _validate_subject(
        self,
        subject: AttributeNode,
        context: SemanticContext,
    ) -> tuple[tuple[str, str], EnumDataType | None]:
        if subject.entity is None:
            raise InvalidDomainError(
                f"Domain subject '{subject.feature}' must be explicitly qualified"
            )

        if subject.entity == "_model" or subject.feature == "target":
            raise InvalidDomainError("Model target cannot be used as a domain subject")

        if subject.entity not in context.variables:
            raise InvalidDomainError(
                f"Domain subject uses unknown variable '{subject.entity}'"
            )

        if (
            subject.semantic is None
            or subject.semantic.resolved_entity != subject.entity
        ):
            raise InvalidDomainError(
                f"Domain subject '{subject.entity}.{subject.feature}' is not bound exactly"
            )

        subject_analysis = self.scalar_analyzer.analyze(subject)
        return (subject.entity, subject.feature), subject_analysis.dtype

    def _validate_interval(self, interval: IntervalDomainNode) -> None:
        self._reject_target_reference(interval.lower)
        self._reject_target_reference(interval.upper)

        lower = self.scalar_analyzer.analyze(interval.lower)
        upper = self.scalar_analyzer.analyze(interval.upper)

        self._require_numeric_bound(lower, "lower")
        self._require_numeric_bound(upper, "upper")

        if lower.is_numeric_constant and upper.is_numeric_constant:
            lower_value = lower.constant_value
            upper_value = upper.constant_value

            if lower_value > upper_value:
                raise InvalidDomainError(
                    f"Reversed interval: lower bound {lower_value!r} is greater "
                    f"than upper bound {upper_value!r}"
                )

            if lower_value == upper_value and (
                interval.lower_boundary is EnumBoundaryKind.OPEN
                or interval.upper_boundary is EnumBoundaryKind.OPEN
            ):
                raise InvalidDomainError(
                    "Empty interval: equal constant bounds require both "
                    "boundaries to be closed"
                )

    def _validate_finite_set(
        self,
        finite_set: FiniteSetDomainNode,
        subject_dtype: EnumDataType | None,
    ) -> None:
        if not finite_set.values:
            raise InvalidDomainError("Finite domain set cannot be empty")

        member_dtypes: list[EnumDataType] = []

        for value in finite_set.values:
            if isinstance(value, ConstantNode):
                analysis = self.scalar_analyzer.analyze(value)
                if analysis.dtype is not None:
                    member_dtypes.append(analysis.dtype)
                continue

            if isinstance(value, SymbolLiteralNode):
                member_dtypes.append(EnumDataType.STRING)
                continue

            if isinstance(value, NameRefNode):
                raise InvalidDomainError(
                    f"Unresolved finite-set name '{value.name}' reached domain validation"
                )

            raise InvalidDomainError(
                f"Unsupported finite-set value: {type(value).__name__}"
            )

        if subject_dtype is not None:
            for member_dtype in member_dtypes:
                if not _compatible_domain_type(subject_dtype, member_dtype):
                    raise InvalidDomainError(
                        "Finite-set member type is incompatible with subject: "
                        f"expected {subject_dtype.value}, got {member_dtype.value}"
                    )
            return

        first_dtype = member_dtypes[0]
        for member_dtype in member_dtypes[1:]:
            if not _compatible_domain_type(first_dtype, member_dtype):
                raise InvalidDomainError(
                    "Finite-set members have incompatible types: "
                    f"{first_dtype.value} and {member_dtype.value}"
                )

    def _require_numeric_bound(
        self,
        analysis: ScalarAnalysis,
        label: str,
    ) -> None:
        if analysis.dtype is not None and analysis.dtype not in _NUMERIC_DTYPES:
            raise InvalidDomainError(
                f"Interval {label} bound must be numeric, got "
                f"{analysis.dtype.value}"
            )

    def _reject_target_reference(self, node: ScalarExpressionNode) -> None:
        if isinstance(node, TargetRefNode):
            raise InvalidDomainError("Model target cannot be used in domain bounds")

        if isinstance(node, UnaryArithmeticNode):
            self._reject_target_reference(node.operand)
            return

        if isinstance(node, BinaryArithmeticNode):
            self._reject_target_reference(node.left)
            self._reject_target_reference(node.right)


def _compatible_domain_type(
    expected: EnumDataType,
    actual: EnumDataType,
) -> bool:
    if expected is actual:
        return True
    return expected in _NUMERIC_DTYPES and actual in _NUMERIC_DTYPES
