from __future__ import annotations

from dataclasses import replace

from dsl.ir.ir1.nodes import (
    AndIR,
    ComparisonIR,
    ImplyIR,
    LogicalIR,
    NotIR,
    OrIR,
    ProblemIR,
    QueryIR,
    VerificationTask,
)


class NNFNormalizer:
    """
    Convert IR logical expressions into Negation Normal Form.

    Guarantees:
    - no ImplyIR remains
    - NotIR only appears directly above atomic predicates
    - AND/OR structure is preserved
    """

    def normalize_task(self, task: VerificationTask) -> VerificationTask:
        return replace(task, query=self.normalize_query(task.query))

    def normalize_tasks(self, tasks: list[VerificationTask]) -> list[VerificationTask]:
        return [self.normalize_task(task) for task in tasks]

    def normalize_query(self, query: QueryIR) -> QueryIR:
        return QueryIR(expression=self.normalize_expr(query.expression))

    def normalize_expr(self, node: LogicalIR) -> LogicalIR:
        return self._nnf(node, negated=False)

    def _nnf(self, node: LogicalIR, negated: bool) -> LogicalIR:
        if isinstance(node, (ComparisonIR, ProblemIR)):
            return NotIR(node) if negated else node

        if isinstance(node, NotIR):
            return self._nnf(node.operand, not negated)

        if isinstance(node, AndIR):
            normalized = [self._nnf(child, negated) for child in node.operands]
            return OrIR(normalized) if negated else AndIR(normalized)

        if isinstance(node, OrIR):
            normalized = [self._nnf(child, negated) for child in node.operands]
            return AndIR(normalized) if negated else OrIR(normalized)

        if isinstance(node, ImplyIR):
            if negated:
                # NOT(A -> B) === A AND NOT B
                return AndIR(
                    operands=[
                        self._nnf(node.left, False),
                        self._nnf(node.right, True),
                    ]
                )

            # A -> B === NOT A OR B
            return OrIR(
                operands=[
                    self._nnf(node.left, True),
                    self._nnf(node.right, False),
                ]
            )

        raise TypeError(f"Unsupported IR node for NNF: {type(node)}")
