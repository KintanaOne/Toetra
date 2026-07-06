from __future__ import annotations

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
from dsl.ir.ir2.errors import InvalidIR2InputError


class NNFGuard:
    """Guards the IR2 input contract: IR2 receives IR1 already in NNF."""

    @classmethod
    def assert_task_is_nnf(cls, task: VerificationTask) -> None:
        cls.assert_query_is_nnf(task.query)

    @classmethod
    def assert_query_is_nnf(cls, query: QueryIR) -> None:
        cls.assert_expr_is_nnf(query.expression)

    @classmethod
    def assert_expr_is_nnf(cls, node: LogicalIR) -> None:
        if isinstance(node, ImplyIR):
            raise InvalidIR2InputError("IR2 input must not contain ImplyIR; run NNF first.")

        if isinstance(node, (ComparisonIR, ProblemIR)):
            return

        if isinstance(node, NotIR):
            if not isinstance(node.operand, (ComparisonIR, ProblemIR)):
                raise InvalidIR2InputError(
                    "IR2 input must be NNF: NotIR may only wrap atomic predicates."
                )
            return

        if isinstance(node, (AndIR, OrIR)):
            for operand in node.operands:
                cls.assert_expr_is_nnf(operand)
            return

        raise InvalidIR2InputError(f"Unsupported IR1 logical node for IR2: {type(node).__name__}")
