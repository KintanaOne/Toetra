# /dsl/ir/pretty.py

from dsl.ir.ir1.nodes import (
    AndIR,
    AttributeExpressionIR,
    ComparisonIR,
    FiniteSetDomainIR,
    ImplyIR,
    IntervalDomainIR,
    LogicalIR,
    NotIR,
    OrIR,
    ProblemIR,
    QueryIR,
    ScopeIR,
    SymbolLiteralIR,
    TargetExpressionIR,
    VerificationTask,
)
from dsl.ir.ir1.scalar import format_scalar_expression

# =============================================================================
# ENTRY POINT
# =============================================================================


def pretty_print_tasks(tasks: list[VerificationTask]):
    for i, task in enumerate(tasks):
        print(f"\n=== TASK {i} ===")
        print(pretty_task(task))


# =============================================================================
# TASK
# =============================================================================


def pretty_task(task: VerificationTask) -> str:
    lines = []

    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("🧠 Verification Task")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    lines.append(f"Property : {task.property_type}")
    lines.append(f"Backend  : {task.backend}")

    # Scope
    lines.append("\n📍 Scope")
    lines.extend(_pretty_scope(task.scope))

    # Query
    lines.append("\n🔍 Query")
    lines.extend(_pretty_query(task.query))

    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    return "\n".join(lines)


# =============================================================================
# SCOPE
# =============================================================================


def _pretty_scope(scope: ScopeIR) -> list[str]:
    lines = []

    lines.append(f"  Type        : {scope.kind}")

    # Variables
    lines.append("  Variables   :")
    for var, role in scope.variables.items():
        lines.append(f"    - {var:<4} → {role}")

    if scope.points:
        lines.append("\n  Points      :")
        for point in scope.points:
            generated = " generated" if point.generated else ""
            lines.append(
                f"    - {point.name:<12} → {point.binding_kind}"
                f" (depth={point.lexical_depth}{generated})"
            )

    if scope.binders:
        lines.append("\n  Binders     :")
        for binder in scope.binders:
            lines.append(f"    - {binder.quantifier} {binder.point.name}")

    if scope.default_point is not None:
        lines.append(f"\n  Default     : {scope.default_point.name}")

    if scope.provenance is not None:
        lines.append(f"  Source form : {scope.provenance.source_kind}")

    if scope.restriction is not None:
        lines.append(f"\n  Restriction ({scope.restriction.provenance.origin}) :")
        lines.extend(_pretty_logical(scope.restriction.expression, indent=4))

    # Neighborhood
    if scope.neighborhood:
        n = scope.neighborhood
        lines.append("\n  Neighborhood :")
        lines.append(f"    metric  : {n.metric}")

        for k, v in n.args.items():
            lines.append(f"    {k:<8}: {v}")

    # Domain
    if scope.domain:
        lines.append("\n  Domain :")
        for entry in scope.domain.entries:
            subject = (
                f"{entry.entity}.{entry.feature}"
                if entry.entity is not None
                else entry.feature
            )
            lines.append(
                f"    - {subject}: {_pretty_domain_constraint(entry.constraint)}"
            )

    return lines


def _pretty_scalar_expression(node) -> str:
    if isinstance(node, SymbolLiteralIR):
        return node.name
    return format_scalar_expression(node)


def _pretty_domain_constraint(constraint) -> str:
    if isinstance(constraint, IntervalDomainIR):
        left = "[" if constraint.lower_boundary.value == "closed" else "]"
        right = "]" if constraint.upper_boundary.value == "closed" else "["
        return (
            f"{left}{_pretty_scalar_expression(constraint.lower)}, "
            f"{_pretty_scalar_expression(constraint.upper)}{right}"
        )
    if isinstance(constraint, FiniteSetDomainIR):
        values = ", ".join(
            _pretty_scalar_expression(value) for value in constraint.values
        )
        return "{" + values + "}"
    return repr(constraint)


# =============================================================================
# QUERY
# =============================================================================


def _pretty_query(query: QueryIR) -> list[str]:
    return _pretty_logical(query.expression, indent=2)


# =============================================================================
# LOGICAL TREE
# =============================================================================


def _pretty_logical(node: LogicalIR, indent=0) -> list[str]:
    space = " " * indent
    lines = []

    # -----------------------------
    # Comparison
    # -----------------------------
    if isinstance(node, ComparisonIR):
        left = format_scalar_expression(node.left, point_aware=True)
        right = format_scalar_expression(node.right, point_aware=True)

        dtype = ""
        if isinstance(node.left, (AttributeExpressionIR, TargetExpressionIR)):
            if node.left.dtype is not None:
                dtype = f" : {node.left.dtype.value}"

        lines.append(f"{space}- {left}{dtype} {node.op.value} {right}")
        return lines

    # -----------------------------
    # Problem
    # -----------------------------
    if isinstance(node, ProblemIR):
        lines.append(f"{space}Problem :")
        lines.append(f"{space}  type      : {node.problem}")
        lines.append(f"{space}  function  : {node.function}")
        return lines

    # -----------------------------
    # AND
    # -----------------------------
    if isinstance(node, AndIR):
        lines.append(f"{space}AND")
        for op in node.operands:
            lines.extend(_pretty_logical(op, indent + 2))
        return lines

    # -----------------------------
    # OR
    # -----------------------------
    if isinstance(node, OrIR):
        lines.append(f"{space}OR")
        for op in node.operands:
            lines.extend(_pretty_logical(op, indent + 2))
        return lines

    # -----------------------------
    # NOT
    # -----------------------------
    if isinstance(node, NotIR):
        lines.append(f"{space}NOT")
        lines.extend(_pretty_logical(node.operand, indent + 2))
        return lines

    # -----------------------------
    # IMPLY
    # -----------------------------
    if isinstance(node, ImplyIR):
        lines.append(f"{space}IMPLY")
        lines.append(f"{space}  IF:")
        lines.extend(_pretty_logical(node.left, indent + 4))
        lines.append(f"{space}  THEN:")
        lines.extend(_pretty_logical(node.right, indent + 4))
        return lines

    # -----------------------------
    # FALLBACK
    # -----------------------------
    lines.append(f"{space}UNKNOWN NODE: {node}")
    return lines
