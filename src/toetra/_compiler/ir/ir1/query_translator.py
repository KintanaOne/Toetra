from __future__ import annotations

from toetra._compiler.ast.nodes.assertion import (
    LogicalNode,
    ComparisonNode,
    AndNode,
    OrNode,
    NotNode,
    ImplicationNode,
    ProblemNode,
)

from toetra._compiler.ir.ir1.nodes import (
    QueryIR,
    LogicalIR,
    ComparisonIR,
    AndIR,
    OrIR,
    NotIR,
    ImplyIR,
    ProblemIR,
)

from toetra._compiler.ir.ir1.scalar_translator import ScalarExpressionTranslator
from toetra._language.vocabulary.functions import EnumFunction
from toetra._language.vocabulary.problems import EnumProblem


class QueryTranslator:
    """
    Translate AST logical assertions into IR query representation.

    Responsibility:
        AssertionNode.root / LogicalNode -> QueryIR / LogicalIR

    This class does not translate scopes or properties.
    """

    def __init__(
        self,
        scalar_translator: ScalarExpressionTranslator | None = None,
    ) -> None:
        self.scalar_translator = scalar_translator or ScalarExpressionTranslator()

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

    def translate_expression(self, node: LogicalNode) -> LogicalIR:
        """Translate one logical AST root without adding a ``QueryIR`` wrapper."""
        return self._translate_logical(node)

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

    def _translate_comparison(
        self,
        node: ComparisonNode,
    ) -> ComparisonIR:
        """Preserve both scalar operands as backend-independent IR1 trees."""

        return ComparisonIR(
            left=self.scalar_translator.translate(node.left),
            op=node.op,
            right=self.scalar_translator.translate(node.right),
        )

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

        args = {}
        semantic = node.semantic
        if semantic is not None and semantic.resolved_evaluations:
            args["evaluations"] = tuple(
                self.scalar_translator.point_registry.evaluation(evaluation)
                for evaluation in semantic.resolved_evaluations
            )
        return ProblemIR(problem=problem, function=function, args=args)
