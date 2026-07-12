
# dsl/utils/pretty_ast.py

from typing import Any
from dsl.ast.nodes.assertion import (
    OrNode,
    AndNode,
    NotNode,
    ComparisonNode,
    ProblemNode,
)

from dsl.ast.nodes.primitives import (
    ConstantNode,
    AttributeNode,
    ArgNode,
)

from dsl.ast.nodes.expressions import (
    AtExprNode,
    CheckAtExprNode,
    PairwiseExprNode,
    QuantifierExprNode,
)

from dsl.ast.nodes.neighborhood import NeighborhoodNode
from dsl.ast.nodes.domain import (
    DomainEntryNode,
    DomainNode,
    FiniteSetDomainNode,
    IntervalDomainNode,
    SymbolLiteralNode,
)

from dsl.ast.nodes.property import PropertyNode, PropertyRuleNode
from dsl.ast.nodes.header import HeaderNode
from dsl.ast.nodes.program import ProgramNode

# =========================================================
# ENTRY POINT
# =========================================================


def pretty(node: Any, indent: int = 0) -> str:
    if node is None:
        return _pad(indent) + "None"

    if isinstance(node, list):
        return _pretty_list(node, indent)

    method = _DISPATCH.get(type(node))
    if method:
        return method(node, indent)

    return _pretty_object(node, indent)


# =========================================================
# DISPATCH
# =========================================================

_DISPATCH = {}


def register(cls):
    def wrapper(func):
        _DISPATCH[cls] = func
        return func

    return wrapper


# =========================================================
# HELPERS
# =========================================================


def _pad(indent: int) -> str:
    return "  " * indent


def _pretty_list(lst, indent):
    if not lst:
        return _pad(indent) + "[]"
    return "\n".join(pretty(item, indent) for item in lst)


def _pretty_object(obj, indent):
    pad = _pad(indent)
    lines = [f"{pad}{obj.__class__.__name__}"]

    if hasattr(obj, "__dict__"):
        for k, v in obj.__dict__.items():
            lines.append(f"{pad}  {k}:")
            lines.append(pretty(v, indent + 2))

    return "\n".join(lines)


def _expr(node):
    from dsl.ast.nodes.primitives import AttributeNode, ConstantNode

    if isinstance(node, AttributeNode):
        return ".".join(node.path)

    if isinstance(node, ConstantNode):
        return repr(node.value)

    if isinstance(node, SymbolLiteralNode):
        return node.name

    return str(node)


# =========================================================
# LOGIC
# =========================================================


@register(OrNode)
def _pretty_or(node: OrNode, indent: int):
    pad = _pad(indent)
    lines = [f"{pad}OR"]
    lines += [pretty(op, indent + 1) for op in node.operands]
    return "\n".join(lines)


@register(AndNode)
def _pretty_and(node: AndNode, indent: int):
    pad = _pad(indent)
    lines = [f"{pad}AND"]
    lines += [pretty(op, indent + 1) for op in node.operands]
    return "\n".join(lines)


@register(NotNode)
def _pretty_not(node: NotNode, indent: int):
    pad = _pad(indent)
    return f"{pad}NOT\n{pretty(node.operand, indent + 1)}"


@register(ComparisonNode)
def _pretty_cmp(node: ComparisonNode, indent: int):
    pad = _pad(indent)
    return f"{pad}{_expr(node.left)} {node.op} {_expr(node.right)}"


# =========================================================
# PRIMITIVES
# =========================================================


@register(AttributeNode)
def _pretty_attr(node: AttributeNode, indent: int):
    return _pad(indent) + ".".join(node.path)


@register(ConstantNode)
def _pretty_const(node: ConstantNode, indent: int):
    return _pad(indent) + str(node.value)


@register(ArgNode)
def _pretty_arg(node: ArgNode, indent: int):
    pad = _pad(indent)

    # suppose format: key=value
    key = getattr(node, "name", None) or getattr(node, "key", None)
    value = getattr(node, "value", None)

    if key is not None:
        return f"{pad}{key}={value}"

    return f"{pad}{value}"


# =========================================================
# DOMAIN / NEIGHBORHOOD
# =========================================================


@register(DomainNode)
def _pretty_domain(node: DomainNode, indent: int):
    pad = _pad(indent)
    lines = [f"{pad}domain"]
    lines.extend(pretty(entry, indent + 1) for entry in node.entries)
    return "\n".join(lines)


@register(DomainEntryNode)
def _pretty_domain_entry(node: DomainEntryNode, indent: int):
    pad = _pad(indent)
    return f"{pad}{_expr(node.subject)}: {pretty(node.constraint, 0).strip()}"


@register(IntervalDomainNode)
def _pretty_interval_domain(node: IntervalDomainNode, indent: int):
    pad = _pad(indent)
    left = "[" if node.lower_boundary.value == "closed" else "]"
    right = "]" if node.upper_boundary.value == "closed" else "["
    return f"{pad}{left}{_expr(node.lower)}, {_expr(node.upper)}{right}"


@register(FiniteSetDomainNode)
def _pretty_finite_set_domain(node: FiniteSetDomainNode, indent: int):
    pad = _pad(indent)
    values = ", ".join(_expr(value) for value in node.values)
    return f"{pad}{{{values}}}"


@register(SymbolLiteralNode)
def _pretty_symbol_literal(node: SymbolLiteralNode, indent: int):
    return _pad(indent) + node.name


@register(NeighborhoodNode)
def _pretty_neighborhood(node: NeighborhoodNode, indent: int):
    pad = _pad(indent)

    if not node.args:
        return f"{pad}neighborhood({node.metric})"

    args = ", ".join(
        f"{getattr(arg, 'name', getattr(arg, 'key', '?'))}={getattr(arg, 'value', '?')}"
        for arg in node.args
    )

    return f"{pad}neighborhood({node.metric}, {args})"


# =========================================================
# EXPRESSIONS
# =========================================================


@register(AtExprNode)
def _pretty_at(node: AtExprNode, indent: int):
    pad = _pad(indent)

    lines = [f"{pad}at {node.variable}"]

    if node.domain:
        lines.append(f"{pad}  in {pretty(node.domain, 0).strip()}")

    if node.neighborhood:
        lines.append(f"{pad}  in {pretty(node.neighborhood, 0).strip()}")

    return "\n".join(lines)


@register(CheckAtExprNode)
def _pretty_check(node: CheckAtExprNode, indent: int):
    return f"{_pad(indent)}check_at {node.variable}"


@register(PairwiseExprNode)
def _pretty_pairwise(node: PairwiseExprNode, indent: int):
    pad = _pad(indent)

    lines = [f"{pad}pairwise {node.left} ~ {node.right}"]

    if node.domain:
        lines.append(f"{pad}  in {pretty(node.domain, 0).strip()}")

    if node.neighborhood:
        lines.append(f"{pad}  in {pretty(node.neighborhood, 0).strip()}")

    return "\n".join(lines)


@register(QuantifierExprNode)
def _pretty_quantifier(node: QuantifierExprNode, indent: int):
    pad = _pad(indent)

    lines = [f"{pad}{node.quantifier} {node.variable}"]

    if node.domain:
        lines.append(f"{pad}  in {pretty(node.domain, 0).strip()}")

    return "\n".join(lines)


# =========================================================
# PROBLEM
# =========================================================


@register(ProblemNode)
def _pretty_problem(node: ProblemNode, indent: int):
    pad = _pad(indent)

    if node.function:
        return f"{pad}{node.problem}.{node.function}()"

    return f"{pad}{node.problem}"


# =========================================================
# PROPERTY
# =========================================================


@register(PropertyRuleNode)
def _pretty_rule(node: PropertyRuleNode, indent: int):
    pad = _pad(indent)

    lines = [
        f"{pad}scope:",
        pretty(node.scope, indent + 1),
    ]

    lines.extend(
        [
            f"{pad}assertion:",
            pretty(node.assertion, indent + 1),
        ]
    )

    return "\n".join(lines)


@register(PropertyNode)
def _pretty_property(node: PropertyNode, indent: int):
    pad = _pad(indent)

    lines = [f"{pad}[{node.type}]"]
    lines.append(pretty(node.rule, indent + 1))

    if node.backend:
        lines.append(f"{pad}using {node.backend}")

    return "\n".join(lines)


# =========================================================
# HEADER / PROGRAM
# =========================================================


@register(HeaderNode)
def _pretty_header(node: HeaderNode, indent: int):
    pad = _pad(indent)

    return "\n".join(
        [
            f"{pad}model := {node.model}",
            f"{pad}target := {node.target}",
        ]
    )


@register(ProgramNode)
def _pretty_program(node: ProgramNode, indent: int):
    lines = [pretty(node.header, indent), ""]

    for prop in node.body:
        lines.append(pretty(prop, indent))
        lines.append("")

    return "\n".join(lines).strip()


