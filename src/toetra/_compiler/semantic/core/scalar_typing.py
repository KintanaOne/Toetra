from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from toetra._compiler.ast.nodes.outputs import (
    ClassProbabilityObservableNode,
    PredictedLabelObservableNode,
)
from toetra._compiler.ast.nodes.primitives import (
    AttributeNode,
    BinaryArithmeticNode,
    ConstantNode,
    ScalarExpressionNode,
    TargetRefNode,
    UnaryArithmeticNode,
)
from toetra._language.vocabulary.operators import (
    EnumArithmeticOperator,
    EnumUnaryOperator,
)
from toetra._compiler.semantic.errors.errors import (
    InvalidArithmeticError,
    InvalidPropertyError,
)
from toetra._compiler.semantic.runtime.annotations import SemanticAnnotations
from toetra._compiler.semantic.types.enums import EnumArithmeticClass, EnumDataType

if TYPE_CHECKING:
    from toetra._models.schema.model_schema import ModelSchema


_NUMERIC_DTYPES = frozenset({EnumDataType.INT, EnumDataType.FLOAT})
_CLASS_RANK = {
    EnumArithmeticClass.AFFINE: 0,
    EnumArithmeticClass.NONLINEAR: 1,
    EnumArithmeticClass.SYMBOLIC_DIVISION: 2,
}
_NO_CONSTANT = object()


@dataclass(frozen=True)
class ScalarAnalysis:
    """Semantic result for one scalar expression tree."""

    dtype: EnumDataType | None
    arithmetic_class: EnumArithmeticClass | None
    constant_value: Any = _NO_CONSTANT
    arithmetic_allowed: bool = True
    ordering_allowed: bool = True

    @property
    def is_constant(self) -> bool:
        return self.constant_value is not _NO_CONSTANT

    @property
    def is_numeric_constant(self) -> bool:
        return self.is_constant and _is_numeric_value(self.constant_value)


class ScalarTypeAnalyzer:
    """Infer scalar types and classify arithmetic without choosing a backend."""

    def __init__(self, model_schema: ModelSchema | None = None):
        self.model_schema = model_schema

    def analyze(self, node: ScalarExpressionNode) -> ScalarAnalysis:
        if isinstance(node, ConstantNode):
            arithmetic_class = (
                EnumArithmeticClass.AFFINE if _is_numeric_dtype(node.dtype) else None
            )
            result = ScalarAnalysis(
                dtype=node.dtype,
                arithmetic_class=arithmetic_class,
                constant_value=node.value,
            )
            self._annotate(node, result)
            return result

        if isinstance(node, AttributeNode):
            dtype = self._attribute_dtype(node)
            result = ScalarAnalysis(
                dtype=dtype,
                arithmetic_class=(
                    EnumArithmeticClass.AFFINE
                    if dtype is None or _is_numeric_dtype(dtype)
                    else None
                ),
            )
            self._annotate(node, result)
            return result

        if isinstance(node, PredictedLabelObservableNode):
            dtype = _dtype_from_annotation(node)
            result = ScalarAnalysis(
                dtype=dtype,
                arithmetic_class=None,
                arithmetic_allowed=False,
                ordering_allowed=False,
            )
            self._annotate(node, result)
            return result

        if isinstance(node, ClassProbabilityObservableNode):
            dtype = _dtype_from_annotation(node) or EnumDataType.FLOAT
            result = ScalarAnalysis(
                dtype=dtype,
                arithmetic_class=None,
            )
            self._annotate(node, result)
            return result

        if isinstance(node, TargetRefNode):
            dtype = self._target_dtype()
            result = ScalarAnalysis(
                dtype=dtype,
                arithmetic_class=(
                    EnumArithmeticClass.AFFINE
                    if dtype is None or _is_numeric_dtype(dtype)
                    else None
                ),
            )
            self._annotate(node, result)
            return result

        if isinstance(node, UnaryArithmeticNode):
            operand = self.analyze(node.operand)
            self._require_arithmetic_operand(operand, "unary arithmetic")

            constant_value: Any = _NO_CONSTANT
            if operand.is_numeric_constant:
                if node.operator is EnumUnaryOperator.PLUS:
                    constant_value = +operand.constant_value
                elif node.operator is EnumUnaryOperator.MINUS:
                    constant_value = -operand.constant_value
                else:
                    raise InvalidArithmeticError(
                        f"Unsupported unary operator '{node.operator}'"
                    )

            result = ScalarAnalysis(
                dtype=operand.dtype,
                arithmetic_class=operand.arithmetic_class or EnumArithmeticClass.AFFINE,
                constant_value=constant_value,
            )
            self._annotate(node, result)
            return result

        if isinstance(node, BinaryArithmeticNode):
            left = self.analyze(node.left)
            right = self.analyze(node.right)

            self._require_arithmetic_operand(left, "left arithmetic operand")
            self._require_arithmetic_operand(right, "right arithmetic operand")

            result = self._analyze_binary(node.operator, left, right)
            self._annotate(node, result)
            return result

        raise InvalidArithmeticError(
            f"Unsupported scalar expression type: {type(node).__name__}"
        )

    def validate_comparison_types(
        self,
        left: ScalarAnalysis,
        right: ScalarAnalysis,
        operator: Any,
    ) -> None:
        """Validate comparison compatibility when both operand types are known."""
        operator_value = getattr(operator, "value", str(operator))
        if operator_value in {"<", "<=", ">", ">="}:
            if not left.ordering_allowed or not right.ordering_allowed:
                raise InvalidPropertyError(
                    "Ordering comparisons are not defined for predicted labels"
                )
            if left.dtype is None or right.dtype is None:
                return
            if not (_is_numeric_dtype(left.dtype) and _is_numeric_dtype(right.dtype)):
                raise InvalidPropertyError(
                    "Ordering comparisons require numeric operands, got "
                    f"{left.dtype.value} and {right.dtype.value}"
                )
            return

        if left.dtype is None or right.dtype is None:
            return

        if operator_value in {"==", "!="} and not _compatible_types(
            left.dtype,
            right.dtype,
        ):
            raise InvalidPropertyError(
                "Equality comparison requires compatible operands, got "
                f"{left.dtype.value} and {right.dtype.value}"
            )

    def _analyze_binary(
        self,
        operator: EnumArithmeticOperator,
        left: ScalarAnalysis,
        right: ScalarAnalysis,
    ) -> ScalarAnalysis:
        constant_value = self._fold_binary(operator, left, right)
        dtype = _binary_result_dtype(operator, left.dtype, right.dtype)

        if operator in {EnumArithmeticOperator.ADD, EnumArithmeticOperator.SUB}:
            arithmetic_class = combine_arithmetic_classes(
                left.arithmetic_class,
                right.arithmetic_class,
            )

        elif operator is EnumArithmeticOperator.MUL:
            inherited = combine_arithmetic_classes(
                left.arithmetic_class,
                right.arithmetic_class,
            )
            if (
                left.is_numeric_constant
                or right.is_numeric_constant
                or (left.is_constant and right.is_constant)
            ):
                arithmetic_class = inherited or EnumArithmeticClass.AFFINE
            elif inherited is EnumArithmeticClass.SYMBOLIC_DIVISION:
                arithmetic_class = EnumArithmeticClass.SYMBOLIC_DIVISION
            else:
                arithmetic_class = EnumArithmeticClass.NONLINEAR

        elif operator is EnumArithmeticOperator.DIV:
            if right.is_numeric_constant:
                if right.constant_value == 0:
                    raise InvalidArithmeticError("Literal division by zero")
                arithmetic_class = (
                    combine_arithmetic_classes(
                        left.arithmetic_class,
                        right.arithmetic_class,
                    )
                    or EnumArithmeticClass.AFFINE
                )
            else:
                arithmetic_class = EnumArithmeticClass.SYMBOLIC_DIVISION

        else:
            raise InvalidArithmeticError(
                f"Unsupported arithmetic operator '{operator}'"
            )

        return ScalarAnalysis(
            dtype=dtype,
            arithmetic_class=arithmetic_class,
            constant_value=constant_value,
        )

    def _fold_binary(
        self,
        operator: EnumArithmeticOperator,
        left: ScalarAnalysis,
        right: ScalarAnalysis,
    ) -> Any:
        if not left.is_numeric_constant or not right.is_numeric_constant:
            if operator is EnumArithmeticOperator.DIV and right.is_constant:
                if right.constant_value == 0:
                    raise InvalidArithmeticError("Literal division by zero")
            return _NO_CONSTANT

        left_value = left.constant_value
        right_value = right.constant_value

        if operator is EnumArithmeticOperator.ADD:
            return left_value + right_value
        if operator is EnumArithmeticOperator.SUB:
            return left_value - right_value
        if operator is EnumArithmeticOperator.MUL:
            return left_value * right_value
        if operator is EnumArithmeticOperator.DIV:
            if right_value == 0:
                raise InvalidArithmeticError("Literal division by zero")
            return left_value / right_value

        raise InvalidArithmeticError(f"Unsupported arithmetic operator '{operator}'")

    def _attribute_dtype(self, node: AttributeNode) -> EnumDataType | None:
        if self.model_schema is None:
            return _dtype_from_annotation(node)

        feature_schema = self.model_schema.features.get(node.feature)
        if feature_schema is None:
            available = ", ".join(sorted(self.model_schema.features.keys()))
            raise InvalidPropertyError(
                f"Unknown feature '{node.feature}'. Available features: {available}"
            )

        return feature_schema.dtype

    def _target_dtype(self) -> EnumDataType | None:
        if self.model_schema is None:
            return None
        return self.model_schema.target_dtype

    def _require_arithmetic_operand(
        self,
        analysis: ScalarAnalysis,
        position: str,
    ) -> None:
        if not analysis.arithmetic_allowed:
            raise InvalidArithmeticError(
                "Predicted labels cannot participate in arithmetic expressions"
            )
        if analysis.dtype is not None and not _is_numeric_dtype(analysis.dtype):
            raise InvalidArithmeticError(
                f"{position} must be numeric, got {analysis.dtype.value}"
            )

    def _annotate(
        self,
        node: ScalarExpressionNode,
        result: ScalarAnalysis,
    ) -> None:
        if node.semantic is None:
            node.semantic = SemanticAnnotations()

        node.semantic.inferred_dtype = result.dtype
        node.semantic.arithmetic_class = result.arithmetic_class
        node.semantic.arithmetic_allowed = result.arithmetic_allowed
        node.semantic.ordering_allowed = result.ordering_allowed
        if result.dtype is not None:
            node.semantic.resolved_type = result.dtype.value


def _dtype_from_annotation(node: ScalarExpressionNode) -> EnumDataType | None:
    if node.semantic is None:
        return None
    if node.semantic.inferred_dtype is not None:
        return node.semantic.inferred_dtype
    if node.semantic.resolved_type is None:
        return None

    try:
        return EnumDataType(node.semantic.resolved_type)
    except ValueError:
        return None


def _binary_result_dtype(
    operator: EnumArithmeticOperator,
    left: EnumDataType | None,
    right: EnumDataType | None,
) -> EnumDataType | None:
    if operator is EnumArithmeticOperator.DIV:
        if left is None or right is None:
            return None
        return EnumDataType.FLOAT

    if left is None or right is None:
        return None

    if EnumDataType.FLOAT in {left, right}:
        return EnumDataType.FLOAT

    return EnumDataType.INT


def combine_arithmetic_classes(
    left: EnumArithmeticClass | None,
    right: EnumArithmeticClass | None,
) -> EnumArithmeticClass | None:
    present = [item for item in (left, right) if item is not None]
    if not present:
        return None
    return max(present, key=lambda item: _CLASS_RANK[item])


def _compatible_types(left: EnumDataType, right: EnumDataType) -> bool:
    if left is right:
        return True
    return _is_numeric_dtype(left) and _is_numeric_dtype(right)


def _is_numeric_dtype(dtype: EnumDataType) -> bool:
    return dtype in _NUMERIC_DTYPES


def _is_numeric_value(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)
