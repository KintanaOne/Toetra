from __future__ import annotations

from typing import Iterable

from dsl.ir.ir1.nodes import (
    AndIR,
    AttributeExpressionIR,
    ComparisonIR,
    ConstantExpressionIR,
    ImplyIR,
    LogicalIR,
    NotIR,
    OrIR,
    ProblemIR,
    QueryIR,
    ScopeIR,
    VerificationTask,
)
from dsl.language.vocabulary.backends import EnumBackend
from dsl.language.vocabulary.functions import EnumFunction
from dsl.language.vocabulary.operators import EnumComparisonOperator
from dsl.language.vocabulary.problems import EnumProblem
from dsl.language.vocabulary.properties import EnumProperty
from dsl.semantic.types.enums import EnumDataType

# -----------------------------------------------------------------------------
# Public API imports under test
# -----------------------------------------------------------------------------


def import_nnf_normalizer_cls():
    """
    Single import point for the NNF normalizer contract.

    If this import fails, the production code does not expose the expected public
    architecture:
        dsl.ir.normalization.nnf.NNFNormalizer
    """

    from dsl.ir.normalization.nnf import NNFNormalizer

    return NNFNormalizer


def import_run_nnf():
    """
    Single import point for the run_nnf contract.

    If this import fails, the production code does not expose the expected public
    executable entrypoint:
        dsl.ir.normalization.run_nnf.run_nnf
    """

    from dsl.ir.normalization.run_nnf import run_nnf

    return run_nnf


# -----------------------------------------------------------------------------
# IR factories
# -----------------------------------------------------------------------------


def cmp(
    feature: str,
    value: object,
    *,
    entity: str = "x0",
    op: EnumComparisonOperator = EnumComparisonOperator.LTE,
) -> ComparisonIR:
    if isinstance(value, bool):
        dtype = EnumDataType.BOOL
    elif isinstance(value, int):
        dtype = EnumDataType.INT
    elif isinstance(value, float):
        dtype = EnumDataType.FLOAT
    elif isinstance(value, str):
        dtype = EnumDataType.STRING
    elif value is None:
        dtype = EnumDataType.NoneType
    else:
        raise TypeError(f"Unsupported comparison fixture value: {value!r}")

    return ComparisonIR(
        left=AttributeExpressionIR(entity=entity, feature=feature),
        op=op,
        right=ConstantExpressionIR(value=value, dtype=dtype),
    )


def problem(
    problem_type: EnumProblem = EnumProblem.CLASSIFICATION,
    function: EnumFunction = EnumFunction.EQUAL,
) -> ProblemIR:
    return ProblemIR(problem=problem_type, function=function, args={})


def task_with_expr(expr: LogicalIR) -> VerificationTask:
    return VerificationTask(
        property_type=EnumProperty.LOGIC,
        scope=ScopeIR(
            kind="pointwise",
            variables={"x0": "anchor"},
            neighborhood=None,
            domain=None,
        ),
        query=QueryIR(expression=expr),
        backend=EnumBackend.Z3,
    )


def normalizer():
    return import_nnf_normalizer_cls()()


# -----------------------------------------------------------------------------
# NNF invariants
# -----------------------------------------------------------------------------


def iter_nodes(node: LogicalIR) -> Iterable[LogicalIR]:
    yield node

    if isinstance(node, NotIR):
        yield from iter_nodes(node.operand)
        return

    if isinstance(node, (AndIR, OrIR)):
        for child in node.operands:
            yield from iter_nodes(child)
        return

    if isinstance(node, ImplyIR):
        yield from iter_nodes(node.left)
        yield from iter_nodes(node.right)
        return


def assert_is_nnf(node: LogicalIR) -> None:
    """
    Structural NNF invariant.

    Allowed:
        - ComparisonIR
        - ProblemIR
        - NotIR(ComparisonIR)
        - NotIR(ProblemIR)
        - AndIR(...)
        - OrIR(...)

    Forbidden:
        - ImplyIR anywhere
        - NotIR above AndIR / OrIR / NotIR / ImplyIR
    """

    for current in iter_nodes(node):
        assert not isinstance(current, ImplyIR), f"ImplyIR found in NNF: {current!r}"

        if isinstance(current, NotIR):
            assert isinstance(
                current.operand,
                (ComparisonIR, ProblemIR),
            ), f"NotIR must only wrap atomic predicates in NNF, got {type(current.operand)}"


def assert_no_implication(node: LogicalIR) -> None:
    assert not any(isinstance(n, ImplyIR) for n in iter_nodes(node))


def assert_quantifier_scope(task: VerificationTask) -> None:
    """
    Quantifier scope contract.

    Semantic validation introduces the explicit symbolic entity declared by forall/exists.
    IR1 must not lose that binding, otherwise the query can reference `x0.a` while
    the scope declares no variable.
    """

    assert task.scope.kind == "quantifier"
    assert task.scope.variables == {"x0": "symbolic"}


def assert_scope_domain_values(
    task: VerificationTask,
    name: str,
    values: list[object],
    *,
    entity: str = "x0",
) -> None:
    """Assert one finite-set domain entry preserved in the IR1 scope."""

    from dsl.ir.ir1.nodes import (
        ConstantExpressionIR,
        FiniteSetDomainIR,
        SymbolLiteralIR,
    )

    domain = task.scope.domain
    assert domain is not None
    assert len(domain.entries) == 1

    entry = domain.entries[0]
    assert entry.entity == entity
    assert entry.feature == name
    assert isinstance(entry.constraint, FiniteSetDomainIR)

    actual_values = [
        (
            value.name
            if isinstance(value, SymbolLiteralIR)
            else value.value if isinstance(value, ConstantExpressionIR) else value
        )
        for value in entry.constraint.values
    ]
    assert actual_values == values


def _enum_value(value: object) -> object:
    return getattr(value, "value", value)


def _cmp_to_str(node: ComparisonIR) -> str:
    from dsl.ir.ir1.scalar import format_scalar_expression

    left = format_scalar_expression(node.left)
    right = format_scalar_expression(node.right)
    return f"CMP({left} {node.op.value} {right})"


def _problem_to_str(node: ProblemIR) -> str:
    problem_value = _enum_value(node.problem)
    function_value = _enum_value(node.function) if node.function is not None else "None"
    return f"PROBLEM({problem_value}.{function_value})"


def _flatten_same_operator(node: LogicalIR, cls: type[LogicalIR]) -> list[LogicalIR]:
    if isinstance(node, cls):
        children: list[LogicalIR] = []
        for child in node.operands:  # type: ignore[attr-defined]
            children.extend(_flatten_same_operator(child, cls))
        return children

    return [node]


def sexpr(node: LogicalIR) -> str:
    """
    Stable logical serialization.

    It intentionally flattens nested AND(AND(...)) and OR(OR(...)) groups in the
    serialized form, so golden files do not fail because of harmless associativity
    choices in the implementation.
    """

    if isinstance(node, ComparisonIR):
        return _cmp_to_str(node)

    if isinstance(node, ProblemIR):
        return _problem_to_str(node)

    if isinstance(node, NotIR):
        return f"NOT({sexpr(node.operand)})"

    if isinstance(node, AndIR):
        operands = _flatten_same_operator(node, AndIR)
        return "AND(" + ", ".join(sexpr(op) for op in operands) + ")"

    if isinstance(node, OrIR):
        operands = _flatten_same_operator(node, OrIR)
        return "OR(" + ", ".join(sexpr(op) for op in operands) + ")"

    if isinstance(node, ImplyIR):
        return f"IMPLY({sexpr(node.left)}, {sexpr(node.right)})"

    raise AssertionError(f"Unsupported node type for serialization: {type(node)}")


def task_to_golden(task: VerificationTask, index: int = 0) -> str:
    backend = task.backend.value if task.backend is not None else "None"
    variables = ",".join(f"{k}:{v}" for k, v in task.scope.variables.items())

    return "\n".join(
        [
            f"TASK {index}",
            f"PROPERTY {task.property_type.value}",
            f"BACKEND {backend}",
            f"SCOPE {task.scope.kind} variables={variables}",
            f"QUERY {sexpr(task.query.expression)}",
        ]
    )


def tasks_to_golden(tasks: list[VerificationTask]) -> str:
    return (
        "\n\n".join(task_to_golden(task, index=i) for i, task in enumerate(tasks))
        + "\n"
    )
