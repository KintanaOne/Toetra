from __future__ import annotations

from dsl.ast.nodes.assertion import (
    AndNode,
    ComparisonNode,
    ImplicationNode,
    LogicalNode,
    NotNode,
    OrNode,
    ProblemNode,
)
from dsl.ast.nodes.domain import (
    FiniteSetDomainNode,
    IntervalDomainNode,
    SymbolLiteralNode,
)
from dsl.ast.nodes.header import SpecificationConstantDeclarationNode
from dsl.ast.nodes.neighborhood import NeighborhoodMembershipNode
from dsl.ast.nodes.primitives import (
    AttributeNode,
    BinaryArithmeticNode,
    ConstantNode,
    NameRefNode,
    ScalarExpressionNode,
    TargetRefNode,
    UnaryArithmeticNode,
)
from dsl.semantic.context.context import SemanticContext
from dsl.semantic.core.restrictions import NeighborhoodLowerer
from dsl.semantic.core.specification_constants import SPECIFICATION_CONSTANT_KIND
from dsl.semantic.errors.errors import UnboundVariableError
from dsl.semantic.runtime.annotations import SemanticAnnotations
from dsl.semantic.runtime.tracer import ValidationTracer
from dsl.semantic.symbols.symbol import Symbol


class BindingValidator:
    """Resolve assertions, restrictions, domains, and indexed model outputs."""

    def __init__(self, tracer=None, model_schema=None):
        self.tracer = tracer or ValidationTracer()
        self.model_schema = model_schema

    def validate(
        self,
        context: SemanticContext,
        rhs: LogicalNode,
    ) -> LogicalNode:
        self.tracer.log(f"Binding validation context: {context}")

        if context.domain is not None:
            self._bind_domain(context.domain, context)

        if context.restriction is not None:
            expression = context.restriction.expression
            if isinstance(expression, LogicalNode):
                bound_restriction = self._check_node(expression, context)
                context.restriction.expression = bound_restriction
                context.canonical_restriction = bound_restriction
            elif isinstance(expression, NeighborhoodMembershipNode):
                expression.epsilon = self._resolve_scalar_expression(
                    expression.epsilon,
                    context,
                    allow_implicit_feature=False,
                )
                lowered = NeighborhoodLowerer(model_schema=self.model_schema).lower(
                    expression, context
                )
                bound_restriction = self._check_node(lowered, context)
                context.canonical_restriction = bound_restriction
            else:
                raise TypeError(
                    f"Unsupported restriction type: {type(expression).__name__}"
                )

        return self._check_node(rhs, context)

    def _check_node(
        self,
        node: LogicalNode,
        context: SemanticContext,
    ) -> LogicalNode:
        if isinstance(node, ComparisonNode):
            node.left = self._resolve_scalar_expression(
                node.left,
                context,
                allow_implicit_feature=True,
            )
            node.right = self._resolve_scalar_expression(
                node.right,
                context,
                allow_implicit_feature=True,
            )
            return node

        if isinstance(node, AndNode):
            node.operands = [
                self._check_node(child, context) for child in node.operands
            ]
            return node

        if isinstance(node, OrNode):
            node.operands = [
                self._check_node(child, context) for child in node.operands
            ]
            return node

        if isinstance(node, NotNode):
            node.operand = self._check_node(node.operand, context)
            return node

        if isinstance(node, ImplicationNode):
            node.left = self._check_node(node.left, context)
            node.right = self._check_node(node.right, context)
            return node

        if isinstance(node, ProblemNode):
            return node

        raise TypeError(f"Unsupported node type: {type(node)}")

    def _resolve_scalar_expression(
        self,
        node: ScalarExpressionNode,
        context: SemanticContext,
        *,
        allow_implicit_feature: bool,
    ) -> ScalarExpressionNode:
        if isinstance(node, ConstantNode):
            return node

        if isinstance(node, TargetRefNode):
            self._resolve_target_ref(node, context)
            return node

        if isinstance(node, AttributeNode):
            self._resolve_attribute(node, context)
            return node

        if isinstance(node, NameRefNode):
            return self._resolve_name_ref(
                node,
                context,
                allow_implicit_feature=allow_implicit_feature,
            )

        if isinstance(node, UnaryArithmeticNode):
            node.operand = self._resolve_scalar_expression(
                node.operand,
                context,
                allow_implicit_feature=allow_implicit_feature,
            )
            return node

        if isinstance(node, BinaryArithmeticNode):
            node.left = self._resolve_scalar_expression(
                node.left,
                context,
                allow_implicit_feature=allow_implicit_feature,
            )
            node.right = self._resolve_scalar_expression(
                node.right,
                context,
                allow_implicit_feature=allow_implicit_feature,
            )
            return node

        raise TypeError(f"Unsupported scalar node type: {type(node)}")

    def _resolve_name_ref(
        self,
        node: NameRefNode,
        context: SemanticContext,
        *,
        allow_implicit_feature: bool,
    ) -> ScalarExpressionNode:
        symbol = context.symbol_table.resolve(node.name)

        if isinstance(symbol, Symbol) and symbol.kind == SPECIFICATION_CONSTANT_KIND:
            return self._constant_from_symbol(symbol)

        if not allow_implicit_feature:
            raise UnboundVariableError(
                f"Unknown specification constant '{node.name}' in domain bound"
            )

        attribute = AttributeNode(
            entity=None,
            feature=node.name,
            path=[node.name],
        )
        self._resolve_attribute(attribute, context)
        return attribute

    def _constant_from_symbol(self, symbol: Symbol) -> ConstantNode:
        declaration = symbol.origin

        if not isinstance(declaration, SpecificationConstantDeclarationNode):
            raise UnboundVariableError(
                f"Specification constant '{symbol.name}' has no declaration value"
            )

        declared_value = declaration.value
        constant = ConstantNode(
            value=declared_value.value,
            dtype=declared_value.dtype,
        )
        constant.semantic = SemanticAnnotations(
            resolved_type=declared_value.dtype.value,
            resolved_symbol=symbol,
        )
        return constant

    def _bind_domain(self, domain, context: SemanticContext) -> None:
        for entry in domain.entries:
            self._resolve_attribute(entry.subject, context)

            constraint = entry.constraint

            if isinstance(constraint, IntervalDomainNode):
                constraint.lower = self._resolve_scalar_expression(
                    constraint.lower,
                    context,
                    allow_implicit_feature=False,
                )
                constraint.upper = self._resolve_scalar_expression(
                    constraint.upper,
                    context,
                    allow_implicit_feature=False,
                )
                continue

            if isinstance(constraint, FiniteSetDomainNode):
                constraint.values = [
                    self._resolve_finite_set_value(value, context)
                    for value in constraint.values
                ]
                continue

            raise TypeError(
                f"Unsupported domain constraint: {type(constraint).__name__}"
            )

    def _resolve_finite_set_value(self, node, context: SemanticContext):
        if isinstance(node, ConstantNode):
            return node

        if isinstance(node, SymbolLiteralNode):
            return node

        if isinstance(node, NameRefNode):
            symbol = context.symbol_table.resolve(node.name)

            if (
                isinstance(symbol, Symbol)
                and symbol.kind == SPECIFICATION_CONSTANT_KIND
            ):
                return self._constant_from_symbol(symbol)

            return SymbolLiteralNode(name=node.name)

        raise TypeError(f"Unsupported finite-set value: {type(node).__name__}")

    def _resolve_target_ref(
        self,
        target: TargetRefNode,
        context: SemanticContext,
    ) -> None:
        semantic = self._ensure_semantic(target)

        if context.model_target is None:
            raise UnboundVariableError(
                "Cannot resolve 'target': missing model target in semantic context"
            )

        if target.point is not None:
            point = context.point_environment.resolve(target.point)
            if point is None:
                raise UnboundVariableError(
                    f"Unknown target point '{target.point}'. Visible points: "
                    f"{list(context.point_environment.names())}"
                )
        else:
            point = context.resolve_default_point(reference_kind="target")

        if not context.model_identity:
            raise UnboundVariableError(
                "Cannot resolve 'target': missing declared model identity "
                "in semantic context"
            )

        evaluation = context.evaluation_registry.intern(
            model_identity=context.model_identity,
            point=point,
            target_name=context.model_target,
        )

        semantic.resolved_entity = "_model"
        semantic.resolved_symbol = None
        # Keep the historical path stable until point-aware IR1 lands in 15.6.
        semantic.resolved_path = ["_model", context.model_target]
        semantic.resolved_type = "model_output"
        semantic.resolved_point = point
        semantic.resolved_evaluation = evaluation

    def _ensure_semantic(self, node):
        if not hasattr(node, "semantic") or node.semantic is None:
            node.semantic = SemanticAnnotations()
        return node.semantic

    def _resolve_attribute(
        self,
        attr: AttributeNode,
        context: SemanticContext,
    ) -> None:
        """Resolve explicit entities exactly and short features without fallback."""
        semantic = self._ensure_semantic(attr)

        if attr.entity is not None:
            point = context.point_environment.resolve(attr.entity)
            if point is None:
                raise UnboundVariableError(
                    f"Unknown variable '{attr.entity}', expected "
                    f"{list(context.point_environment.names())}"
                )

            semantic.resolved_entity = point.name
            semantic.resolved_symbol = point
            semantic.resolved_point = point
            semantic.resolved_path = [point.name, *attr.path[1:]]
            return

        point = context.resolve_default_point(
            reference_kind=f"feature '{attr.feature}'"
        )
        semantic.resolved_entity = point.name
        semantic.resolved_symbol = point
        semantic.resolved_point = point
        semantic.resolved_path = [point.name, attr.feature]
