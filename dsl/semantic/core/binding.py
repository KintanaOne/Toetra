from dsl.semantic.context.context import SemanticContext
from dsl.semantic.errors.errors import UnboundVariableError
from dsl.semantic.runtime.annotations import SemanticAnnotations
from dsl.semantic.runtime.tracer import ValidationTracer

from dsl.ast.nodes.assertion import (
    ComparisonNode,
    AndNode,
    OrNode,
    NotNode,
    ImplicationNode,
    ProblemNode,
)

from dsl.ast.nodes.primitives import AttributeNode, TargetRefNode


class BindingValidator:
    """
    BindingValidator

    Responsibility
    --------------
    Resolve variable bindings inside RHS expressions.

    This phase occurs AFTER:
        - parsing
        - LHS validation

    And BEFORE:
        - logic validation
        - type validation
        - IR lowering
    """

    def __init__(self, tracer=None):
        self.tracer = tracer or ValidationTracer()

    # ─────────────────────────────────────────────
    # ENTRY POINT
    # ─────────────────────────────────────────────

    def validate(
        self,
        context: SemanticContext,
        rhs,
    ):

        self.tracer.log(f"Binding validation context: {context}")

        self._check_node(rhs, context)

    # ─────────────────────────────────────────────
    # RECURSIVE NODE WALK
    # ─────────────────────────────────────────────

    def _check_node(
        self,
        node,
        context: SemanticContext,
    ):

        if isinstance(node, ComparisonNode):

            if isinstance(node.left, TargetRefNode):
                self._resolve_target_ref(node.left, context)

            if isinstance(node.left, AttributeNode):
                self._resolve_attribute(node.left, context)

            if isinstance(node.right, AttributeNode):
                self._resolve_attribute(node.right, context)

            return

        if isinstance(node, AndNode):

            for child in node.operands:
                self._check_node(child, context)

            return

        if isinstance(node, OrNode):

            for child in node.operands:
                self._check_node(child, context)

            return

        if isinstance(node, NotNode):

            self._check_node(node.operand, context)

            return

        if isinstance(node, ImplicationNode):

            self._check_node(node.left, context)
            self._check_node(node.right, context)

            return

        if isinstance(node, ProblemNode):
            return

        raise TypeError(f"Unsupported node type: {type(node)}")

    def _resolve_target_ref(
        self,
        target: TargetRefNode,
        context: SemanticContext,
    ):
        semantic = self._ensure_semantic(target)

        if context.model_target is None:
            raise UnboundVariableError(
                "Cannot resolve 'target': missing model target in semantic context"
            )

        semantic.resolved_entity = "_model"
        semantic.resolved_symbol = None
        semantic.resolved_path = ["_model", context.model_target]
        semantic.resolved_type = "model_output"

        return

    # ─────────────────────────────────────────────
    # SEMANTIC INITIALIZATION
    # ─────────────────────────────────────────────

    def _ensure_semantic(self, node):
        if not hasattr(node, "semantic") or node.semantic is None:
            node.semantic = SemanticAnnotations()
        return node.semantic

    def _resolve_symbol(self, symbol_table, name):
        """
        Centralized symbol resolution layer.
        """
        if symbol_table is None:
            return None

        symbol = symbol_table.resolve(name)

        # explicit normalization point (future-proof)
        if symbol is None:
            return None

        return symbol

    # ─────────────────────────────────────────────
    # ATTRIBUTE RESOLUTION
    # ─────────────────────────────────────────────

    def _resolve_attribute(
        self,
        attr: AttributeNode,
        context: SemanticContext,
    ):
        """
        Resolve semantic binding for an AttributeNode.

        Resolution priority:
        --------------------
        1. SymbolTable explicit resolution
        2. Explicit entity (x, x', _x)
        3. Implicit entity (default_entity)
        4. Single-variable fallback
        5. Error (ambiguity)
        """

        semantic = self._ensure_semantic(attr)

        variables = context.variables
        default_entity = context.default_entity
        symbol_table = context.symbol_table

        # ==================================================
        # Helper: safe symbol resolution
        # ==================================================
        def resolve(name: str):
            if symbol_table is None:
                return None
            return symbol_table.resolve(name)

        # ==================================================
        # 1. SYMBOL TABLE OVERRIDE (HIGHEST PRIORITY)
        # ==================================================
        if attr.entity is not None:

            symbol = resolve(attr.entity)

            if symbol is not None:
                self.tracer.log(
                    f"SymbolTable resolution: {attr.entity} → {symbol.name}"
                )

                semantic.resolved_entity = symbol.name
                semantic.resolved_symbol = symbol
                semantic.resolved_path = [symbol.name, attr.feature]
                return

        # ==================================================
        # 2. EXPLICIT ENTITY RESOLUTION
        # ==================================================
        if attr.entity is not None:

            # CASE: unknown variable
            if attr.entity not in variables:

                # ------------------------------------------
                # 2.a Single variable fallback (alias case)
                # ------------------------------------------
                if len(variables) == 1:

                    resolved = next(iter(variables.keys()))
                    symbol = resolve(resolved)

                    self.tracer.log(f"Alias resolution: {attr.entity} → {resolved}")

                    semantic.resolved_entity = resolved
                    semantic.resolved_symbol = symbol
                    semantic.resolved_path = [resolved, attr.feature]
                    return

                raise UnboundVariableError(
                    f"Unknown variable '{attr.entity}', "
                    f"expected {list(variables.keys())}"
                )

            # CASE: valid explicit variable
            symbol = resolve(attr.entity)

            semantic.resolved_entity = attr.entity
            semantic.resolved_symbol = symbol
            semantic.resolved_path = [attr.entity, attr.feature]
            return

        # ==================================================
        # 3. IMPLICIT ENTITY RESOLUTION
        # ==================================================
        if default_entity is not None:

            symbol = resolve(default_entity)

            semantic.resolved_entity = default_entity
            semantic.resolved_symbol = symbol
            semantic.resolved_path = [default_entity, attr.feature]
            return

        # ==================================================
        # 4. SINGLE VARIABLE FALLBACK (no entity provided)
        # ==================================================
        if len(variables) == 1:

            resolved = next(iter(variables.keys()))
            symbol = resolve(resolved)

            semantic.resolved_entity = resolved
            semantic.resolved_symbol = symbol
            semantic.resolved_path = [resolved, attr.feature]
            return

        # ==================================================
        # 5. AMBIGUITY ERROR
        # ==================================================
        raise UnboundVariableError(
            f"Ambiguous feature '{attr.feature}' "
            f"with variables {list(variables.keys())}"
        )
