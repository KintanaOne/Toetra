# /dsl/ir/pretty.py

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
)

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

    # Neighborhood
    if scope.neighborhood:
        n = scope.neighborhood
        lines.append("\n  Neighborhood :")
        lines.append(f"    metric  : {n.metric}")

        for k, v in n.args.items():
            lines.append(f"    {k:<8}: {v}")

    # Domain
    if scope.domain:
        d = scope.domain
        lines.append("\n  Domain :")
        lines.append(f"    name   : {d.name}")

        if hasattr(d, "args") and d.args:
            for k, v in d.args.items():
                lines.append(f"    {k:<6}: {v}")

        if hasattr(d, "values"):
            lines.append(f"    values : {d.args.values}")

    return lines


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
        dtype = ""

        if node.feature_dtype is not None:
            dtype = f" : {node.feature_dtype.value}"

        lines.append(
            f"{space}- {node.entity}.{node.feature}{dtype} "
            f"{node.op.value} {node.value}"
        )
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
