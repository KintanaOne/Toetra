from __future__ import annotations

from dataclasses import dataclass

from dsl.ir.ir2.enums import VerificationSemantics
from dsl.ir.ir2.nodes import AssumptionIR2, VerificationTaskIR2
from dsl.ir.ir2.pretty import pretty_formula


@dataclass(frozen=True)
class IR2ExplainOptions:
    """Formatting options for developer-oriented IR2 explanations."""

    include_assumption_formulas: bool = True
    include_requirements: bool = True
    include_mermaid: bool = False


def explain_ir2_task(
    task: VerificationTaskIR2,
    *,
    options: IR2ExplainOptions | None = None,
) -> str:
    """Return a developer-friendly explanation of an IR2 verification task.

    The regular pretty-printer focuses on the final IR2 object. This explainer
    focuses on the mental model used while debugging the FORML pipeline:

        DSL specification P
        + assumptions Gamma
        + verification semantics
        -> verification condition
        -> selected normal form

    The verification condition depends on the task semantics:

        REFUTATION   -> Gamma AND NOT P
        SATISFACTION -> Gamma AND P

    It is intentionally backend-independent. It explains what IR2 built, not how
    a concrete backend such as Z3 will encode it.
    """

    options = options or IR2ExplainOptions()

    lines: list[str] = []
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("🔎 IR2 Explanation")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    lines.extend(_summary(task))
    lines.append("")
    lines.extend(_semantics(task))
    lines.append("")
    lines.extend(_scope(task))
    lines.append("")
    lines.extend(_spec_formula(task))
    lines.append("")
    lines.extend(_assumptions(task.assumptions, options=options))
    lines.append("")
    lines.extend(_verification_condition(task))

    if options.include_requirements:
        lines.append("")
        lines.extend(_requirements(task))

    if options.include_mermaid:
        lines.append("")
        lines.extend(_mermaid(task))

    return "\n".join(lines)


def explain_ir2_tasks(
    tasks: list[VerificationTaskIR2],
    *,
    options: IR2ExplainOptions | None = None,
) -> str:
    """Return explanations for several IR2 tasks."""

    blocks = []
    for i, task in enumerate(tasks):
        blocks.append(f"=== IR2 EXPLANATION {i} ===")
        blocks.append(explain_ir2_task(task, options=options))
    return "\n\n".join(blocks)


def _summary(task: VerificationTaskIR2) -> list[str]:
    return [
        f"Property      : {_enum_value(task.property_type)}",
        f"Backend hint  : {_enum_value(task.backend)}",
        f"Normal form   : {_enum_value(task.normal_form)}",
        f"Semantics     : {_enum_value(task.semantics)}",
    ]


def _semantics(task: VerificationTaskIR2) -> list[str]:
    if task.semantics is VerificationSemantics.REFUTATION:
        return [
            "🧭 Semantics",
            "  FORML searches for a violation of the user property P:",
            "  VC = Γ ∧ ¬P",
            "  - UNSAT means no counterexample exists under Γ, so P is proved.",
            "  - SAT means the backend found a candidate counterexample.",
            "  - UNKNOWN means the backend could not conclude.",
        ]

    if task.semantics is VerificationSemantics.SATISFACTION:
        return [
            "🧭 Semantics",
            "  FORML searches for a value satisfying the user property P:",
            "  VC = Γ ∧ P",
            "  - SAT means the backend found a witness.",
            "  - UNSAT means no witness exists under Γ.",
            "  - UNKNOWN means the backend could not conclude.",
        ]

    raise ValueError(f"Unsupported verification semantics: {task.semantics}")


def _scope(task: VerificationTaskIR2) -> list[str]:
    scope = task.scope
    lines = ["📍 Scope", f"  kind      : {scope.kind}", "  variables :"]

    for name, role in scope.variables.items():
        lines.append(f"    - {name} -> {role}")

    if scope.neighborhood is not None:
        lines.append("  neighborhood:")
        lines.append(f"    metric : {scope.neighborhood.metric}")
        lines.append(f"    eps    : {scope.neighborhood.eps}")
        for key, value in scope.neighborhood.args.items():
            lines.append(f"    {key} : {value}")

    if scope.domain is not None:
        lines.append("  domain:")
        for entry in scope.domain.entries:
            subject = (
                f"{entry.entity}.{entry.feature}"
                if entry.entity is not None
                else entry.feature
            )
            lines.append(f"    - {subject} : {entry.constraint}")

    return lines


def _spec_formula(task: VerificationTaskIR2) -> list[str]:
    return [
        "📝 User specification P",
        _indent(pretty_formula(task.spec_formula), spaces=2),
    ]


def _assumptions(
    assumptions: tuple[AssumptionIR2, ...],
    *,
    options: IR2ExplainOptions,
) -> list[str]:
    lines = ["🧱 Assumptions Γ", f"  count : {len(assumptions)}"]

    if not assumptions:
        lines.append("  <none>")
        return lines

    for i, assumption in enumerate(assumptions):
        lines.append(f"  assumption[{i}]")
        lines.append(f"    source      : {_enum_value(assumption.source)}")
        lines.append(f"    description : {assumption.description or '<none>'}")

        if assumption.metadata:
            lines.append("    metadata    :")
            for key, value in assumption.metadata.items():
                lines.append(f"      {key}: {value}")

        if options.include_assumption_formulas:
            lines.append("    formula     :")
            lines.append(_indent(pretty_formula(assumption.formula), spaces=6))

    return lines


def _verification_condition(task: VerificationTaskIR2) -> list[str]:
    if task.semantics is VerificationSemantics.REFUTATION:
        equation = "VC = Γ ∧ ¬P"
    elif task.semantics is VerificationSemantics.SATISFACTION:
        equation = "VC = Γ ∧ P"
    else:
        raise ValueError(f"Unsupported verification semantics: {task.semantics}")

    return [
        "🎯 Verification condition",
        f"  {equation}",
        f"  selected normal form : {_enum_value(task.normal_form)}",
        _indent(pretty_formula(task.verification_condition), spaces=2),
    ]


def _requirements(task: VerificationTaskIR2) -> list[str]:
    requirements = task.requirements

    rows = [
        ("boolean_logic", requirements.requires_boolean_logic),
        ("numeric_comparisons", requirements.requires_numeric_comparisons),
        ("problem_predicates", requirements.requires_problem_predicates),
        ("model_assertions", requirements.requires_model_assertions),
        (
            "uses_quantified_scope",
            requirements.uses_quantified_scope,
        ),
        (
            "native_quantifiers",
            requirements.requires_native_quantifiers,
        ),
        ("domains", requirements.requires_domains),
        ("neighborhoods", requirements.requires_neighborhoods),
    ]

    lines = ["🧩 Backend-neutral requirements"]

    for name, enabled in rows:
        lines.append(f"  - {name}: {enabled}")

    lines.append(
        "  - verification_semantics: "
        f"{_enum_value(requirements.required_verification_semantics)}"
    )
    lines.append(f"  - normal_form: {_enum_value(requirements.normal_form)}")

    return lines


def _mermaid(task: VerificationTaskIR2) -> list[str]:
    assumption_label = f"Γ assumptions ({len(task.assumptions)})"
    normal_form = _enum_value(task.normal_form)

    return [
        "🖼️ Mermaid view",
        "```mermaid",
        "flowchart LR",
        "    DSL[DSL spec P] --> VC[VC = Γ ∧ ¬P]",
        f"    MODEL[{assumption_label}] --> VC",
        f"    VC --> NF[{normal_form} form]",
        "    NF --> ROUTER[Backend routing]",
        "```",
    ]


def _enum_value(value: object) -> object:
    if value is None:
        return None
    return getattr(value, "value", value)


def _indent(text: str, spaces: int) -> str:
    prefix = " " * spaces
    return "\n".join(prefix + line if line else line for line in text.splitlines())
