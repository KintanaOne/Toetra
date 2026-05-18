from typing import Type, TypeVar, cast

from lark import Tree

from dsl.ast.nodes.expressions import (
    AtExprNode,
    CheckAtExprNode,
    PairwiseExprNode,
    QuantifierExprNode,
)
from dsl.builder.program import parse_program
from dsl.parser.parser import parse_forml_code

T = TypeVar("T")

# ======================================================================================================================
# HEADER
# ======================================================================================================================


def assert_header(
    program,
    *,
    model: str,
    target: str,
) -> None:
    """
    Assert program header structure.
    """

    assert program.header is not None

    header = program.header

    assert header.model == model
    assert header.target == target


# ----------------------------------------------------------------------------------------------------------------------
# Parse / Build helpers
# ----------------------------------------------------------------------------------------------------------------------


def parse(code: str) -> Tree:
    """
    Parse raw FORML code into a Lark parse tree.
    """

    return parse_forml_code(code)


def build_program(code: str):
    """
    Parse and build a full FORML program.
    """

    return parse_program(parse(code))


def build_property(code: str):
    """
    Parse and build the first property of a FORML program.
    """

    return build_program(code).body[0]


# ----------------------------------------------------------------------------------------------------------------------
# Scope helpers
# ----------------------------------------------------------------------------------------------------------------------


def assert_scope_type(scope, expected_type: Type[T]) -> T:
    """
    Assert the scope node type and return the properly typed scope.
    """

    assert isinstance(scope, expected_type), (
        f"Expected scope type {expected_type.__name__}, " f"got {type(scope).__name__}"
    )

    return cast(T, scope)


# ----------------------------------------------------------------------------------------------------------------------
# Property helpers
# ----------------------------------------------------------------------------------------------------------------------


def assert_property_basics(prop, expected_type: str = "ROBUSTNESS") -> None:
    """
    Assert common property invariants.
    """

    assert prop is not None
    assert prop.type == expected_type

    assert prop.rule is not None
    assert prop.rule.assertion is not None


# ----------------------------------------------------------------------------------------------------------------------
# Neighborhood helpers
# ----------------------------------------------------------------------------------------------------------------------


def assert_neighborhood(neighborhood, metric: str, **expected_args) -> None:
    """
    Assert neighborhood structure and arguments.
    """

    assert neighborhood is not None

    assert neighborhood.metric == metric

    args = {arg.key: arg.value for arg in neighborhood.args}

    for key, expected_value in expected_args.items():
        assert key in args
        assert args[key] == expected_value


# ----------------------------------------------------------------------------------------------------------------------
# Domain helpers
# ----------------------------------------------------------------------------------------------------------------------


def assert_domain(domain, name: str, values: list[str]) -> None:
    """
    Assert domain structure and values.
    """

    assert domain is not None

    assert domain.name == name
    assert domain.values == values


# ----------------------------------------------------------------------------------------------------------------------
# Backend helpers
# ----------------------------------------------------------------------------------------------------------------------


def assert_backend(
    prop,
    expected_name: str,
    **expected_args,
) -> None:
    """
    Assert backend structure and arguments.
    """

    assert prop.backend is not None

    backend = prop.backend

    assert backend.name == expected_name

    args = {arg.key: arg.value for arg in backend.args}

    for key, expected_value in expected_args.items():

        assert key in args, f"Missing backend arg '{key}'"

        assert args[key] == expected_value, (
            f"Expected backend arg '{key}'=" f"{expected_value}, got {args[key]}"
        )


def assert_no_backend(prop) -> None:
    """
    Assert no backend is attached to the property.
    """

    assert prop.backend is None


# ----------------------------------------------------------------------------------------------------------------------
# Pairwise helpers
# ----------------------------------------------------------------------------------------------------------------------


def assert_pair(
    pair: str,
    left_expected: str,
    right_expected: str,
) -> None:
    """
    Assert pairwise pair structure.
    """

    parts = pair.split("~")

    if len(parts) != 2:
        raise ValueError(f"Invalid pair format: {pair}")

    left, right = [x.strip() for x in parts]

    assert left == left_expected
    assert right == right_expected


# ----------------------------------------------------------------------------------------------------------------------
# Scope shortcuts
# ----------------------------------------------------------------------------------------------------------------------


def assert_at_scope(prop) -> AtExprNode:
    return assert_scope_type(prop.rule.scope, AtExprNode)


def assert_check_at_scope(prop) -> CheckAtExprNode:
    return assert_scope_type(prop.rule.scope, CheckAtExprNode)


def assert_pairwise_scope(prop) -> PairwiseExprNode:
    return assert_scope_type(prop.rule.scope, PairwiseExprNode)


def assert_quantifier_scope(prop) -> QuantifierExprNode:
    return assert_scope_type(prop.rule.scope, QuantifierExprNode)
