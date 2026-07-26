from __future__ import annotations

from toetra._compiler.ir.ir1.nodes import (
    AndIR,
    AtomicIR,
    ComparisonIR,
    LogicalIR,
    NotIR,
    OrIR,
    ProblemIR,
)
from toetra._compiler.ir.ir1.scalar import format_scalar_expression
from toetra._compiler.ir.ir2.dsl.nodes import (
    CNFFormulaIR2,
    DNFFormulaIR2,
    FormulaIR2,
    LiteralIR2,
    NNFFormulaIR2,
    VerificationTaskIR2,
)
from toetra._compiler.ir.ir2.enums import Polarity
from toetra._compiler.ir.ir2.model.affine import (
    AffineExpressionIR2,
    AffineModelQuantityConstraintIR2,
    AffineOutputConstraintIR2,
)
from toetra._compiler.ir.ir2.model.base import ModelConstraintIR2


def pretty_print_ir2_tasks(tasks: list[VerificationTaskIR2]) -> None:
    for i, task in enumerate(tasks):
        print(f"\n=== IR2 TASK {i} ===")
        print(pretty_ir2_task(task))


def pretty_ir2_task(task: VerificationTaskIR2) -> str:
    lines = []
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("🧠 Verification Task IR2")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append(
        f"Property      : {getattr(task.property_type, 'value', task.property_type)}"
    )
    lines.append(f"Backend       : {getattr(task.backend, 'value', task.backend)}")
    lines.append(f"Scope         : {task.scope.kind}")
    lines.append(f"Semantics     : {task.semantics.value}")
    lines.append(f"Normal form   : {task.normal_form.value}")
    lines.append("Requirements  : " + _pretty_requirements(task))
    lines.append(f"Assumptions   : {len(task.assumptions)}")
    if task.lowering_evidence:
        lines.append(f"Lowerings     : {len(task.lowering_evidence)}")

    if task.assumptions:
        lines.append("Assumption formulas:")
        for index, assumption in enumerate(task.assumptions):
            source = getattr(assumption.source, "value", assumption.source)
            lines.append(f"  Γ[{index}] source={source}")
            if assumption.description:
                lines.append(f"    description : {assumption.description}")
            lines.append(_indent(pretty_formula(assumption.formula), spaces=4))

    lines.append("Spec formula  :")
    lines.append(_indent(pretty_formula(task.spec_formula), spaces=2))
    lines.append("Verification condition:")
    lines.append(_indent(pretty_formula(task.verification_condition), spaces=2))
    return "\n".join(lines)


def _pretty_requirements(task: VerificationTaskIR2) -> str:
    req = task.requirements
    active = []

    if req.requires_boolean_logic:
        active.append("boolean_logic")
    if req.requires_numeric_comparisons:
        active.append("numeric_comparisons")
    if req.requires_problem_predicates:
        active.append("problem_predicates")
    if req.requires_model_assertions:
        active.append("model_assertions")
    if req.requires_model_semantic_quantities:
        active.append("model_semantic_quantities")
    if req.requires_native_quantifiers:
        active.append("native_quantifiers")
    if req.requires_domains:
        active.append("domains")
    if req.requires_neighborhoods:
        active.append("neighborhoods")

    return ", ".join(active) if active else "none"


def pretty_formula(formula: FormulaIR2) -> str:
    """Pretty-print an IR2 formula with explicit literal polarity.

    The pretty representation intentionally avoids inline syntax such as
    ``NOT _x.b <= 2`` because it can be misread. In CNF/DNF, every leaf is
    shown as ``LITERAL[positive](...)`` or ``LITERAL[negative](...)``.
    """

    if isinstance(formula, NNFFormulaIR2):
        return "NNF\n" + _indent(_pretty_logical_tree(formula.expression), spaces=2)

    if isinstance(formula, CNFFormulaIR2):
        return _pretty_cnf(formula)

    if isinstance(formula, DNFFormulaIR2):
        return _pretty_dnf(formula)

    return repr(formula)


def _pretty_cnf(formula: CNFFormulaIR2) -> str:
    lines = ["CNF"]

    if len(formula.clauses) == 0:
        lines.append("  <empty>")
        return "\n".join(lines)

    if len(formula.clauses) == 1:
        lines.append("  OR")
        for literal in formula.clauses[0].literals:
            lines.append("    " + _pretty_literal(literal))
        return "\n".join(lines)

    for i, clause in enumerate(formula.clauses):
        lines.append(f"  clause[{i}] OR")
        for literal in clause.literals:
            lines.append("    " + _pretty_literal(literal))

    return "\n".join(lines)


def _pretty_dnf(formula: DNFFormulaIR2) -> str:
    lines = ["DNF"]

    if len(formula.terms) == 0:
        lines.append("  <empty>")
        return "\n".join(lines)

    if len(formula.terms) == 1:
        lines.append("  AND")
        for literal in formula.terms[0].literals:
            lines.append("    " + _pretty_literal(literal))
        return "\n".join(lines)

    for i, term in enumerate(formula.terms):
        lines.append(f"  branch[{i}] AND")
        for literal in term.literals:
            lines.append("    " + _pretty_literal(literal))

    return "\n".join(lines)


def _pretty_literal(literal: LiteralIR2) -> str:
    return f"LITERAL[{literal.polarity.value}]({_pretty_atom(literal.atom)})"


def _pretty_logical_tree(node: LogicalIR) -> str:
    if isinstance(node, AtomicIR):
        return _pretty_literal(LiteralIR2(atom=node, polarity=Polarity.POSITIVE))

    if isinstance(node, NotIR):
        if isinstance(node.operand, AtomicIR):
            return _pretty_literal(
                LiteralIR2(atom=node.operand, polarity=Polarity.NEGATIVE)
            )

        return "NOT\n" + _indent(_pretty_logical_tree(node.operand), spaces=2)

    if isinstance(node, AndIR):
        return _pretty_variadic("AND", node.operands)

    if isinstance(node, OrIR):
        return _pretty_variadic("OR", node.operands)

    return repr(node)


def _pretty_variadic(name: str, operands: list[LogicalIR]) -> str:
    lines = [name]

    for operand in operands:
        lines.append(_indent(_pretty_logical_tree(operand), spaces=2))

    return "\n".join(lines)


def _pretty_atom(atom: AtomicIR) -> str:
    if isinstance(atom, ComparisonIR):
        return _pretty_comparison(atom)

    if isinstance(atom, ProblemIR):
        return _pretty_problem(atom)

    if isinstance(atom, ModelConstraintIR2):
        return _pretty_model_constraint(atom)

    raise TypeError(f"Unsupported IR2 atom: {type(atom).__name__}")


def _pretty_comparison(atom: ComparisonIR) -> str:
    op = getattr(atom.op, "value", atom.op)
    left = format_scalar_expression(atom.left)
    right = format_scalar_expression(atom.right)
    return f"{left} {op} {right}"


def _pretty_problem(atom: ProblemIR) -> str:
    problem = getattr(atom.problem, "value", atom.problem)
    function = getattr(atom.function, "value", atom.function)
    return f"{problem}.{function}({atom.args or {}})"


def _pretty_model_constraint(atom: ModelConstraintIR2) -> str:
    if isinstance(atom, AffineOutputConstraintIR2):
        return _pretty_affine_output_constraint(atom)
    if isinstance(atom, AffineModelQuantityConstraintIR2):
        return _pretty_affine_model_quantity_constraint(atom)

    return f"<model-constraint:{type(atom).__name__}>"


def _pretty_affine_output_constraint(atom: AffineOutputConstraintIR2) -> str:
    op = getattr(atom.op, "value", atom.op)
    output = (
        f"target[{atom.evaluation.point.name}]"
        if atom.evaluation is not None
        else f"{atom.output_entity}.{atom.output_feature}"
    )
    return f"{output} {op} {_pretty_affine_expression(atom.expression)}"


def _pretty_affine_model_quantity_constraint(
    atom: AffineModelQuantityConstraintIR2,
) -> str:
    op = getattr(atom.op, "value", atom.op)
    quantity = atom.quantity
    label = (
        f"_model.{quantity.output_name}[{quantity.point.name}]"
        f"::<{quantity.quantity_kind.value}>"
    )
    return f"{label} {op} {_pretty_affine_expression(atom.expression)}"


def _pretty_affine_expression(expression: AffineExpressionIR2) -> str:
    parts: list[str] = []

    for term in expression.terms:
        entity = term.point.name if term.point is not None else term.entity
        parts.append(f"{term.coefficient}*{entity}.{term.feature}")

    if expression.bias or not parts:
        parts.append(str(expression.bias))

    return " + ".join(parts)


def _indent(text: str, spaces: int) -> str:
    prefix = " " * spaces
    return "\n".join(prefix + line if line else line for line in text.splitlines())
