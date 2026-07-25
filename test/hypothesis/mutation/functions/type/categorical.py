"""
Categorical mutations (DISCRETE SEMANTICS)

GOAL:
    Corrupt discrete decision spaces such as enums,
    operators, and symbolic categories.

ROLE IN Toetra:
    - test enum robustness
    - break symbolic reasoning
    - stress DSL categorical integrity

CHARACTERISTICS:
    ✔ AST valid
    ✔ syntax valid
    ❌ semantic category integrity corrupted
"""

import random
from copy import deepcopy

from dsl.ast.nodes.assertion import ComparisonNode
from dsl.builder.program import ProgramNode
from dsl.language.vocabulary.operators import EnumComparisonOperator
from dsl.language.vocabulary.functions import EnumFunction
from dsl.language.vocabulary.problems import EnumProblem

from test.hypothesis.mutation.functions.base import (
    mutation,
    MutationNature,
    MutationSeverity,
    MutationImpact,
    PipelineStage,
)

# =========================================================
# MUTATION 1 : flip comparison operator
# =========================================================


@mutation(
    nature=MutationNature.CATEGORICAL,
    severity=MutationSeverity.HIGH,
    severity_score=0.75,
    impact={MutationImpact.SEMANTIC_INVALID},
    expected_failures={PipelineStage.SEMANTIC_ANALYSIS},
    preserves_valid_ast=True,
    preserves_typing=True,
)
def flip_comparison_operator(ast: ProgramNode) -> ProgramNode:
    """
    Replace comparison operators with random alternatives.
    """

    mutated = deepcopy(ast)

    operators = list(EnumComparisonOperator)

    for p in mutated.body:

        root = p.rule.assertion.root

        assert isinstance(root, ComparisonNode)

        if hasattr(root, "op"):
            root.op = random.choice(operators)

    return mutated


# =========================================================
# MUTATION 2 : corrupt problem context
# =========================================================


@mutation(
    nature=MutationNature.CATEGORICAL,
    severity=MutationSeverity.MEDIUM,
    severity_score=0.6,
    impact={MutationImpact.SEMANTIC_INVALID},
    expected_failures={PipelineStage.SEMANTIC_ANALYSIS},
    preserves_valid_ast=True,
    preserves_typing=True,
)
def corrupt_problem_context(ast: ProgramNode) -> ProgramNode:
    """
    Replace problem enum with another valid one.
    """

    mutated = deepcopy(ast)

    problems = list(EnumProblem)

    for p in mutated.body:

        if hasattr(p.rule.assertion, "context") and p.rule.assertion.context:
            p.rule.assertion.context.problem = random.choice(problems)

    return mutated


# =========================================================
# MUTATION 3 : corrupt function mapping
# =========================================================


@mutation(
    nature=MutationNature.CATEGORICAL,
    severity=MutationSeverity.MEDIUM,
    severity_score=0.65,
    impact={MutationImpact.SEMANTIC_INVALID},
    expected_failures={PipelineStage.SEMANTIC_ANALYSIS},
    preserves_valid_ast=True,
    preserves_typing=True,
)
def corrupt_function_mapping(ast: ProgramNode) -> ProgramNode:
    """
    Replace function enum with another valid one.
    """

    mutated = deepcopy(ast)

    functions = list(EnumFunction)

    for p in mutated.body:

        if hasattr(p.rule.assertion, "context") and p.rule.assertion.context:
            p.rule.assertion.context.function = random.choice(functions)

    return mutated


CATEGORICAL_MUTATIONS = [
    flip_comparison_operator,
    corrupt_problem_context,
    corrupt_function_mapping,
]


def apply_categorical_mutations(ast: ProgramNode, n: int = 1) -> ProgramNode:
    """
    Apply N categorical mutations.
    """

    mutated = ast

    for _ in range(n):
        mutation_fn = random.choice(CATEGORICAL_MUTATIONS)
        mutated = mutation_fn(mutated)

    return mutated
