from __future__ import annotations

from dsl.ast.nodes.outputs import (
    ClassProbabilityObservableNode,
    OutputObservableNode,
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
from dsl.ir.ir1.nodes import (
    AttributeExpressionIR,
    BinaryArithmeticExpressionIR,
    ConstantExpressionIR,
    ScalarExpressionIR,
    ScalarValueSource,
    TargetExpressionIR,
    UnaryArithmeticExpressionIR,
)
from dsl.ir.ir1.outputs import ClassLabelIR, OutputObservableExpressionIR
from dsl.ir.ir1.points import PointIRRegistry
from dsl.semantic.core.specification_constants import SPECIFICATION_CONSTANT_KIND
from dsl.semantic.types.enums import EnumArithmeticClass, EnumDataType


class ScalarExpressionTranslator:
    """Lower a semantically validated scalar AST tree into IR1."""

    def __init__(self, point_registry: PointIRRegistry | None = None) -> None:
        self.point_registry = point_registry or PointIRRegistry()

    def translate(self, node: ScalarExpressionNode) -> ScalarExpressionIR:
        if isinstance(node, ConstantNode):
            return self._translate_constant(node)

        if isinstance(node, AttributeNode):
            return self._translate_attribute(node)

        if isinstance(node, OutputObservableNode):
            return self._translate_output_observable(node)

        if isinstance(node, TargetRefNode):
            return self._translate_target(node)

        if isinstance(node, UnaryArithmeticNode):
            return UnaryArithmeticExpressionIR(
                operator=node.operator,
                operand=self.translate(node.operand),
                dtype=self._dtype(node),
                arithmetic_class=self._arithmetic_class(node),
            )

        if isinstance(node, BinaryArithmeticNode):
            return BinaryArithmeticExpressionIR(
                left=self.translate(node.left),
                operator=node.operator,
                right=self.translate(node.right),
                dtype=self._dtype(node),
                arithmetic_class=self._arithmetic_class(node),
            )

        if isinstance(node, NameRefNode):
            raise ValueError(
                f"Unresolved scalar name reached IR1 translation: {node.name!r}"
            )

        raise TypeError(f"Unsupported scalar AST node: {type(node).__name__}")

    def _translate_constant(self, node: ConstantNode) -> ConstantExpressionIR:
        source_kind = ScalarValueSource.LITERAL
        source_name: str | None = None

        semantic = node.semantic
        symbol = semantic.resolved_symbol if semantic is not None else None

        if symbol is not None and symbol.kind == SPECIFICATION_CONSTANT_KIND:
            source_kind = ScalarValueSource.SPECIFICATION_CONSTANT
            source_name = symbol.name

        return ConstantExpressionIR(
            value=node.value,
            dtype=node.dtype,
            source_kind=source_kind,
            source_name=source_name,
            source_lexeme=node.source_lexeme,
        )

    def _translate_attribute(self, node: AttributeNode) -> AttributeExpressionIR:
        semantic = node.semantic

        if semantic is None or semantic.resolved_entity is None:
            raise ValueError(
                f"Attribute '{node.feature}' is not semantically bound before IR1"
            )

        feature = node.feature
        if semantic.resolved_path and len(semantic.resolved_path) >= 2:
            feature = ".".join(semantic.resolved_path[1:])

        return AttributeExpressionIR(
            entity=semantic.resolved_entity,
            feature=feature,
            dtype=self._dtype(node),
            point=(
                self.point_registry.point(semantic.resolved_point)
                if semantic.resolved_point is not None
                else None
            ),
        )

    def _translate_output_observable(
        self,
        node: OutputObservableNode,
    ) -> OutputObservableExpressionIR:
        semantic = node.semantic
        if semantic is None or semantic.resolved_evaluation is None:
            raise ValueError(
                "Model output observable reached IR1 without a model "
                "evaluation identity"
            )
        if semantic.resolved_output_observable is None:
            raise ValueError(
                "Model output observable reached IR1 without an observable kind"
            )

        label = None
        if isinstance(node, ClassProbabilityObservableNode):
            if semantic.resolved_label is None:
                raise ValueError(
                    "Class probability reached IR1 without a canonical label"
                )
            label = ClassLabelIR(
                value=semantic.resolved_label,
                dtype=node.label.dtype,
                source_lexeme=node.label.source_lexeme,
            )

        return OutputObservableExpressionIR(
            evaluation=self.point_registry.evaluation(semantic.resolved_evaluation),
            observable=semantic.resolved_output_observable,
            dtype=self._dtype(node),
            label=label,
        )

    def _translate_target(self, node: TargetRefNode) -> TargetExpressionIR:
        semantic = node.semantic

        if semantic is None or semantic.resolved_entity != "_model":
            raise ValueError("Target reference is not bound to the model output")

        if not semantic.resolved_path or len(semantic.resolved_path) < 2:
            raise ValueError(
                f"Invalid target reference path: {semantic.resolved_path!r}"
            )

        if semantic.resolved_evaluation is None:
            raise ValueError(
                "Point-aware target reference reached IR1 without a model "
                "evaluation identity"
            )
        evaluation = self.point_registry.evaluation(semantic.resolved_evaluation)

        return TargetExpressionIR(
            entity="_model",
            feature=semantic.resolved_path[-1],
            dtype=self._dtype(node),
            evaluation=evaluation,
        )

    @staticmethod
    def _dtype(node: ScalarExpressionNode) -> EnumDataType | None:
        semantic = node.semantic
        if semantic is None:
            return node.dtype if isinstance(node, ConstantNode) else None

        if semantic.inferred_dtype is not None:
            return semantic.inferred_dtype

        if semantic.resolved_type is None or semantic.resolved_type == "model_output":
            return node.dtype if isinstance(node, ConstantNode) else None

        try:
            return EnumDataType(semantic.resolved_type)
        except ValueError:
            return node.dtype if isinstance(node, ConstantNode) else None

    @staticmethod
    def _arithmetic_class(
        node: ScalarExpressionNode,
    ) -> EnumArithmeticClass | None:
        if node.semantic is None:
            return None
        return node.semantic.arithmetic_class
