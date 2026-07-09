from __future__ import annotations

from dsl.ast.nodes.assertion import (
    LogicalNode,
    ComparisonNode,
    AndNode,
    OrNode,
    NotNode,
    ImplicationNode,
    ProblemNode,
)

from dsl.ast.nodes.primitives import AttributeNode, TargetRefNode
from dsl.ir.ir1.nodes import (
    QueryIR,
    LogicalIR,
    ComparisonIR,
    AndIR,
    OrIR,
    NotIR,
    ImplyIR,
    ProblemIR,
)

from dsl.language.vocabulary.problems import EnumProblem
from dsl.language.vocabulary.functions import EnumFunction
from dsl.semantic.types.enums import EnumDataType


class QueryTranslator:
    """
    Translate AST logical assertions into IR query representation.

    Responsibility:
        AssertionNode.root / LogicalNode -> QueryIR / LogicalIR

    This class does not translate scopes or properties.
    """

    # ------------------------------------------------------------------
    # ENTRY POINT
    # ------------------------------------------------------------------

    def translate(self, node: LogicalNode) -> QueryIR:
        if isinstance(node, AndNode):
            operands = [self._translate_logical(n) for n in self._flatten_and(node)]

            return QueryIR(expression=AndIR(operands=operands))

        if isinstance(node, OrNode):
            operands = [self._translate_logical(n) for n in self._flatten_or(node)]

            return QueryIR(expression=OrIR(operands=operands))

        return QueryIR(expression=self._translate_logical(node))

    # ------------------------------------------------------------------
    # FLATTENING
    # ------------------------------------------------------------------

    def _flatten_and(self, node: AndNode) -> list[LogicalNode]:
        result: list[LogicalNode] = []

        for child in node.operands:
            if isinstance(child, AndNode):
                result.extend(self._flatten_and(child))
            else:
                result.append(child)

        return result

    def _flatten_or(self, node: OrNode) -> list[LogicalNode]:
        result: list[LogicalNode] = []

        for child in node.operands:
            if isinstance(child, OrNode):
                result.extend(self._flatten_or(child))
            else:
                result.append(child)

        return result

    # ------------------------------------------------------------------
    # LOGICAL TRANSLATION
    # ------------------------------------------------------------------

    def _translate_logical(self, node: LogicalNode) -> LogicalIR:
        if isinstance(node, ComparisonNode):
            return self._translate_comparison(node)

        if isinstance(node, AndNode):
            return AndIR(
                operands=[self._translate_logical(child) for child in node.operands]
            )

        if isinstance(node, OrNode):
            return OrIR(
                operands=[self._translate_logical(child) for child in node.operands]
            )

        if isinstance(node, NotNode):
            return NotIR(operand=self._translate_logical(node.operand))

        if isinstance(node, ImplicationNode):
            return ImplyIR(
                left=self._translate_logical(node.left),
                right=self._translate_logical(node.right),
            )

        if isinstance(node, ProblemNode):
            return self._translate_problem(node)

        raise ValueError(f"Unsupported LogicalNode type: {type(node)}")

    # ------------------------------------------------------------------
    # LEAVES
    # ------------------------------------------------------------------

    def _translate_comparison(self, node: ComparisonNode) -> ComparisonIR:
        """
        Translate a semantically resolved comparison into IR.

        IMPORTANT:
        This must use semantic annotations, not raw parsed attributes.
        """

        entity, feature, feature_dtype = self._resolve_ir_operand(node.left)

        return ComparisonIR(
            entity=entity,
            feature=feature,
            op=node.op,
            value=node.right.value,
            feature_dtype=feature_dtype,
            value_dtype=node.right.dtype,
        )

    def _resolve_ir_operand(
        self,
        node: AttributeNode | TargetRefNode,
    ) -> tuple[str, str, EnumDataType | None]:
        if isinstance(node, AttributeNode):
            return self._resolve_ir_attribute(node)

        if isinstance(node, TargetRefNode):
            return self._resolve_ir_target_ref(node)

        raise TypeError(f"Unsupported comparison left operand: {type(node)}")

    def _resolve_ir_target_ref(
        self,
        node: TargetRefNode,
    ) -> tuple[str, str, EnumDataType | None]:
        semantic = node.semantic

        if semantic is None:
            raise ValueError("Cannot lower unbound target reference to IR")

        if semantic.resolved_entity != "_model":
            raise ValueError(
                f"Invalid target reference binding: expected '_model', "
                f"got {semantic.resolved_entity!r}"
            )

        if not semantic.resolved_path or len(semantic.resolved_path) < 2:
            raise ValueError(
                f"Invalid target reference path: {semantic.resolved_path!r}"
            )

        return "_model", semantic.resolved_path[-1], None

    def _translate_problem(self, node: ProblemNode) -> ProblemIR:
        problem = (
            node.problem
            if isinstance(node.problem, EnumProblem)
            else EnumProblem(node.problem)
        )

        function = None

        if node.function is not None:
            function = (
                node.function
                if isinstance(node.function, EnumFunction)
                else EnumFunction(node.function)
            )

        return ProblemIR(
            problem=problem,
            function=function,
            args={},
        )

    def _resolve_ir_attribute(
        self,
        attr: AttributeNode,
    ) -> tuple[str, str, EnumDataType | None]:
        """
        Convert a semantically resolved AttributeNode into IR coordinates.

        The IR layer must rely on semantic annotations, not on raw parsed fields.

        Examples:
            age      -> x'.age   depending on semantic scope
            x.age    -> x.age
            x'.age   -> x'.age
            _x.age   -> _x.age

        If schema-aware validation was enabled, the feature dtype is also
        propagated into IR.
        """

        semantic = getattr(attr, "semantic", None)

        if semantic is None:
            raise ValueError(
                f"Attribute '{attr.feature}' has no semantic annotations. "
                "Run semantic validation before IR translation."
            )

        if not semantic.resolved_entity:
            raise ValueError(
                f"Attribute '{attr.feature}' has no resolved entity. "
                "Binding validation probably did not run."
            )

        entity = semantic.resolved_entity

        if semantic.resolved_path and len(semantic.resolved_path) >= 2:
            feature = ".".join(semantic.resolved_path[1:])
        else:
            feature = attr.feature

        feature_dtype = None

        if semantic.resolved_type is not None:
            try:
                feature_dtype = EnumDataType(semantic.resolved_type)
            except ValueError as e:
                raise ValueError(
                    f"Unsupported resolved dtype '{semantic.resolved_type}' "
                    f"for attribute '{feature}'"
                ) from e

        return entity, feature, feature_dtype
