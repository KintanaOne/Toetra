# test/hypothesis/mutations/semantic/context.py

"""
Semantic context mismatch mutations.

GOAL:
    Corrupt semantic contexts while preserving AST validity.

ROLE IN FORML:
    - stress semantic analyzers
    - validate semantic consistency
    - test incompatible semantic combinations

CHARACTERISTICS:
    ✔ AST valid
    ✔ syntax valid
    ✔ typing preserved
    ❌ semantic meaning corrupted
"""

from __future__ import annotations

import random
from copy import deepcopy

from dsl.builder.program import ProgramNode

from dsl.ast.nodes.assertion import ComparisonNode, ProblemNode

from dsl.language.vocabulary.operators import EnumComparisonOperator
from dsl.language.vocabulary.problems import EnumProblem
from dsl.language.vocabulary.functions import EnumFunction

from test.hypothesis.mutation.functions.base import (
    mutation,
    MutationLayer,
    MutationNature,
    MutationSeverity,
    MutationImpact,
    PipelineStage,
)


# =========================================================
# MUTATION 1 : corrupt problem context
# =========================================================


@mutation(
    layer=MutationLayer.SEMANTIC,
    nature=MutationNature.SUBSTITUTION,
    severity=MutationSeverity.HIGH,
    severity_score=0.80,
    impact={MutationImpact.SEMANTIC_INVALID},
    expected_failures={
        PipelineStage.SEMANTIC_ANALYSIS,
    },
    preserves_valid_cst=True,
    preserves_valid_ast=True,
    preserves_typing=True,
    preserves_semantic_equivalence=False,
)
def corrupt_problem_context(
    ast: ProgramNode,
) -> ProgramNode:
    """
    Replace semantic problem with another valid one.
    """

    mutated = deepcopy(ast)

    problems = list(EnumProblem)

    for property_node in mutated.body:

        root = property_node.rule.assertion.root

        if isinstance(root, ProblemNode):

            candidates = [
                p
                for p in problems
                if p != root.problem
            ]

            if candidates:
                root.problem = random.choice(candidates)

    return mutated


# =========================================================
# MUTATION 2 : corrupt function context
# =========================================================


@mutation(
    layer=MutationLayer.SEMANTIC,
    nature=MutationNature.SUBSTITUTION,
    severity=MutationSeverity.HIGH,
    severity_score=0.75,
    impact={MutationImpact.SEMANTIC_INVALID},
    expected_failures={
        PipelineStage.SEMANTIC_ANALYSIS,
    },
    preserves_valid_cst=True,
    preserves_valid_ast=True,
    preserves_typing=True,
    preserves_semantic_equivalence=False,
)
def corrupt_function_context(
    ast: ProgramNode,
) -> ProgramNode:
    """
    Replace semantic function with another valid one.
    """

    mutated = deepcopy(ast)

    functions = list(EnumFunction)

    for property_node in mutated.body:

        root = property_node.rule.assertion.root

        if isinstance(root, ProblemNode):

            candidates = [
                f
                for f in functions
                if f != root.function
            ]

            if candidates:
                root.function = random.choice(candidates)

    return mutated


# =========================================================
# MUTATION 1 : flip comparison operator
# =========================================================


@mutation(
    layer=MutationLayer.LOGICAL,
    nature=MutationNature.CORRUPTION,
    severity=MutationSeverity.HIGH,
    severity_score=0.75,
    impact={MutationImpact.SEMANTIC_INVALID},
    expected_failures={PipelineStage.SEMANTIC_ANALYSIS},
    preserves_valid_ast=True,
    preserves_typing=True,
    preserves_semantic_equivalence=False,
    preserves_valid_cst=True
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


CONTEXT_MUTATIONS = [
    corrupt_problem_context,
    corrupt_function_context,
    flip_comparison_operator
]
