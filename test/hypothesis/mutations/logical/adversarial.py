"""
Adversarial mutations (ROBUSTNESS & SAFETY LAYER)

GOAL:
    Create valid but misleading or pathological ASTs.

ROLE IN FORML:
    - test validator robustness
    - detect silent corruption
    - stress semantic safety checks
    - simulate malicious or edge-case inputs

CHARACTERISTICS:
    ✔ AST valid
    ✔ syntax valid
    ✔ often passes shallow checks
    ❌ semantically misleading or dangerous
"""

import random
from copy import deepcopy

from dsl.builder.program import ProgramNode
from dsl.ast.nodes.assertion import NotNode, AndNode, OrNode

from test.hypothesis.mutations.base import (
    MutationLayer,
    mutation,
    MutationNature,
    MutationSeverity,
    MutationImpact,
    PipelineStage,
)

# =========================================================
# MUTATION 1 : tautology injection
# =========================================================


@mutation(
    layer=MutationLayer.ADVERSARIAL,
    nature=MutationNature.CORRUPTION,
    severity=MutationSeverity.HIGH,
    severity_score=0.85,
    impact={MutationImpact.SEMANTIC_INVALID},
    expected_failures={PipelineStage.SEMANTIC_ANALYSIS},
    preserves_valid_ast=True,
    preserves_typing=True,
    preserves_semantic_equivalence=False,
    preserves_valid_cst=True
)
def inject_adversarial_tautology(ast: ProgramNode) -> ProgramNode:
    """
    Inject tautological expressions.
    A becomes A OR NOT(A)
    """

    mutated = deepcopy(ast)

    for p in mutated.body:

        root = deepcopy(p.rule.assertion.root)

        p.rule.assertion.root = OrNode(operands=[root, NotNode(operand=deepcopy(root))])

    return mutated


# =========================================================
# MUTATION 2 : nested NOT explosion
# =========================================================


@mutation(
    layer=MutationLayer.ADVERSARIAL,
    nature=MutationNature.CORRUPTION,
    severity=MutationSeverity.MEDIUM,
    severity_score=0.6,
    impact={MutationImpact.SEMANTIC_INVALID},
    expected_failures={PipelineStage.SEMANTIC_ANALYSIS},
    preserves_valid_ast=True,
    preserves_typing=True,
    preserves_semantic_equivalence=False,
    preserves_valid_cst=True
)
def nest_negations(ast: ProgramNode) -> ProgramNode:
    """
    Wrap assertion in multiple NOT layers.
    """

    mutated = deepcopy(ast)

    for p in mutated.body:

        root = p.rule.assertion.root

        depth = random.randint(2, 5)

        for _ in range(depth):
            root = NotNode(operand=root)

        p.rule.assertion.root = root

    return mutated


ADVERSARIAL_MUTATIONS = [
    inject_adversarial_tautology,
    nest_negations,
]


def apply_adversarial_mutations(ast: ProgramNode, n: int = 1) -> ProgramNode:
    """
    Apply N adversarial mutations.
    """

    mutated = ast

    for _ in range(n):
        mutation_fn = random.choice(ADVERSARIAL_MUTATIONS)
        mutated = mutation_fn(mutated)

    return mutated


ADVERSARIAL_MUTATIONS = [
    inject_adversarial_tautology,
    nest_negations,
]