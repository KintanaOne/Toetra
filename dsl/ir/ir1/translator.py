from __future__ import annotations

from dsl.ast.nodes.expressions import AtExprNode, CheckAtExprNode, PairwiseExprNode, QuantifierExprNode
from dsl.ast.nodes.program import ProgramNode
from dsl.ast.nodes.property import PropertyNode

from dsl.ast.nodes.assertion import (
    LogicalNode,
    ComparisonNode,
    AndNode,
    OrNode,
    NotNode,
    ImplicationNode,
    ProblemNode,
)

from dsl.ast.nodes.primitives import AttributeNode, ConstantNode

from dsl.ir.ir1.nodes import (
    VerificationTask,
    ScopeIR,
    QueryIR,
    LogicalIR,
    ComparisonIR,
    AndIR,
    OrIR,
    NotIR,
    ImplyIR,
    ProblemIR,
    NeighborhoodIR,
    DomainIR
)

from dsl.language.vocabulary.problems import EnumProblem
from dsl.language.vocabulary.functions import EnumFunction
from dsl.language.vocabulary.backends import EnumBackend
from dsl.language.vocabulary.operators import EnumLogicalOperator
from dsl.language.vocabulary.operators import EnumComparisonOperator


class IRTranslator:
    """
    AST (semantic validated) → IR executable layer
    """

    # --------------------------------------------------------------------------
    # ENTRY POINT
    # --------------------------------------------------------------------------

    def translate(self, program: ProgramNode) -> list[VerificationTask]:
        return [self._translate_property(p) for p in program.body]

    # --------------------------------------------------------------------------
    # PROPERTY
    # --------------------------------------------------------------------------

    def _translate_property(self, prop: PropertyNode) -> VerificationTask:

        scope_ir = self._translate_scope(prop.rule.scope)
        query_ir = self._translate_assertion(prop.rule.assertion.root)

        backend = prop.backend.name if prop.backend else None

        return VerificationTask(
            property_type=prop.type,
            scope=scope_ir,
            query=query_ir,
            backend=EnumBackend[backend] if backend else None
        )

    # --------------------------------------------------------------------------
    # SCOPE
    # --------------------------------------------------------------------------

    def _translate_scope(self, scope) -> ScopeIR:

        variables = {}
        neighborhood_ir = None
        domain_ir = None
        kind = "unknown"

        # ------------------------------------------------------------------
        # AT
        # ------------------------------------------------------------------

        if isinstance(scope, AtExprNode):

            kind = "local"

            variables = {
                scope.variable: "anchor",
                f"{scope.variable}'": "perturbation"
            }

            # --------------------------
            # neighborhood
            # --------------------------

            if scope.neighborhood is not None:

                args_dict = {
                    arg.key: arg.value
                    for arg in scope.neighborhood.args
                }

                eps = args_dict.get("eps")

                neighborhood_ir = NeighborhoodIR(
                    metric=scope.neighborhood.metric,
                    args=args_dict
                )

            # --------------------------
            # domain
            # --------------------------

            if scope.domain is not None:

                domain_ir = DomainIR(
                    name=scope.domain.name,
                    args={
                        "values": scope.domain.values
                    }
                )

        # ------------------------------------------------------------------
        # PAIRWISE
        # ------------------------------------------------------------------

        elif isinstance(scope, PairwiseExprNode):

            kind = "pairwise"

            left, right = [
                x.strip()
                for x in scope.pair.split(",")
            ]

            variables = {
                left: "left",
                right: "right"
            }

        # ------------------------------------------------------------------
        # CHECK AT
        # ------------------------------------------------------------------

        elif isinstance(scope, CheckAtExprNode):

            kind = "pointwise"

            variables = {
                scope.variable: "point"
            }

        # ------------------------------------------------------------------
        # QUANTIFIER
        # ------------------------------------------------------------------

        elif isinstance(scope, QuantifierExprNode):

            kind = "quantifier"

            if scope.domain is not None:

                domain_ir = DomainIR(
                    name=scope.domain.name,
                    args={}
                )

        # ------------------------------------------------------------------
        # FINAL
        # ------------------------------------------------------------------

        return ScopeIR(
            kind=kind,
            variables=variables,
            neighborhood=neighborhood_ir,
            domain=domain_ir,
        )

    # --------------------------------------------------------------------------
    # ASSERTION → QUERY
    # --------------------------------------------------------------------------

    def _flatten_and(self, node: AndNode) -> list[LogicalNode]:
        result = []

        for n in node.operands:
            if isinstance(n, AndNode):
                result.extend(self._flatten_and(n))
            else:
                result.append(n)

        return result
    
    def _flatten_or(self, node: OrNode) -> list[LogicalNode]:
        result = []

        for n in node.operands:
            if isinstance(n, OrNode):
                result.extend(self._flatten_or(n))
            else:
                result.append(n)

        return result
    


    def _translate_assertion(self, node: LogicalNode) -> QueryIR:

        if isinstance(node, AndNode):

            operands = [
                self._translate_logical(n)
                for n in self._flatten_and(node)
            ]

            return QueryIR(
                expression=AndIR(
                    operands=operands
                )
            )
        
        if isinstance(node, OrNode):

            operands = [
                self._translate_logical(n)
                for n in self._flatten_or(node)
            ]

            return QueryIR(
                expression=OrIR(
                    operands=operands
                )
            )
        return QueryIR(
            expression=self._translate_logical(node)
        )
    

    def _translate_logical(self, node: LogicalNode) -> LogicalIR:
        """
        Recursively converts AST LogicalNode → IR LogicalIR.

        This function produces a PURE logical tree:
            - ComparisonIR (leaf)
            - AndIR / OrIR / NotIR / ImplyIR (structure)
            - ProblemIR (semantic leaf)

        No QueryIR wrapping here.
        """

        # -----------------------------
        # COMPARISON
        # -----------------------------
        if isinstance(node, ComparisonNode):

            assert node.left.entity is not None, "Left entity cannot be None"
            assert node.left.feature is not None, "Left feature cannot be None"

            return ComparisonIR(
                entity=node.left.entity,
                feature=node.left.feature,
                op=node.op,  # 🔥 important
                value=node.right.value
            )

        # -----------------------------
        # AND
        # -----------------------------
        if isinstance(node, AndNode):

            return AndIR(
                operands=[
                    self._translate_logical(n)
                    for n in node.operands
                ]
            )

        # -----------------------------
        # OR
        # -----------------------------
        if isinstance(node, OrNode):

            return OrIR(
                operands=[
                    self._translate_logical(n)
                    for n in node.operands
                ]
            )

        # -----------------------------
        # NOT
        # -----------------------------
        if isinstance(node, NotNode):

            return NotIR(
                operand=self._translate_logical(node.operand)
            )

        # -----------------------------
        # IMPLICATION
        # -----------------------------
        if isinstance(node, ImplicationNode):

            return ImplyIR(
                left=self._translate_logical(node.left),
                right=self._translate_logical(node.right)
            )

        # -----------------------------
        # PROBLEM NODE
        # -----------------------------
        if isinstance(node, ProblemNode):

            return ProblemIR(
                problem=EnumProblem[node.problem],
                function=EnumFunction[node.function] if node.function else None,
                args={}
            )

        # -----------------------------
        # FAIL SAFE
        # -----------------------------
        raise ValueError(f"Unsupported LogicalNode type: {type(node)}")