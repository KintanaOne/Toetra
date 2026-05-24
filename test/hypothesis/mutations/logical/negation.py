import random
from copy import deepcopy
from tkinter import NE

from dsl.builder.assertion import (
    AndNode,
    ImplicationNode,
    NotNode,
    OrNode,
)

from dsl.builder.program import ProgramNode

from test.hypothesis.mutations.base import (
    MutationLayer,
    MutationLayer,
    mutation,
    MutationImpact,
    MutationNature,
    MutationSeverity,
    PipelineStage,
)

@mutation(
    layer=MutationLayer.LOGICAL,
    nature=MutationNature.PERTURBATION,
    severity=MutationSeverity.HIGH,
    severity_score=0.8,
    impact={MutationImpact.SEMANTIC_INVALID},
    expected_failures={PipelineStage.SEMANTIC_ANALYSIS},
    preserves_valid_ast=True,
    preserves_typing=True,
    preserves_semantic_equivalence=False,
    preserves_valid_cst=True
)
def negate_assertion(ast: ProgramNode) -> ProgramNode:
    """
    Negate assertion roots.

    Example:
        A becomes NOT(A)
    """

    mutated = deepcopy(ast)

    for p in mutated.body:

        root = p.rule.assertion.root
        p.rule.assertion.root = NotNode(operand=root)

    return mutated


@mutation(
    layer=MutationLayer.LOGICAL,
    nature=MutationNature.PERTURBATION,
    severity=MutationSeverity.MEDIUM,
    severity_score=0.55,
    impact={MutationImpact.SEMANTIC_INVALID},
    expected_failures={PipelineStage.SEMANTIC_ANALYSIS},
    preserves_valid_ast=True,
    preserves_typing=True,
    preserves_semantic_equivalence=False,
    preserves_valid_cst=True
)
def remove_negation(ast: ProgramNode) -> ProgramNode:
    """
    Remove NOT operators.

    Example:
        NOT(A) becomes A
    """

    mutated = deepcopy(ast)

    for p in mutated.body:

        root = p.rule.assertion.root

        if isinstance(root, NotNode):
            p.rule.assertion.root = root.operand

    return mutated


@mutation(
    layer=MutationLayer.LOGICAL,
    nature=MutationNature.PERTURBATION,
    severity=MutationSeverity.INFO,
    severity_score=0.1,
    impact={MutationImpact.NONE},
    expected_failures=set(),
    preserves_valid_ast=True,
    preserves_typing=True,
    preserves_semantic_equivalence=True,
    preserves_valid_cst=True
)
def inject_double_negation(ast: ProgramNode) -> ProgramNode:
    """
    Inject double negation.

    Example:
        A becomes NOT(NOT(A))

    NOTE:
        Logically equivalent.
    """

    mutated = deepcopy(ast)

    for p in mutated.body:

        root = deepcopy(p.rule.assertion.root)

        p.rule.assertion.root = NotNode(operand=NotNode(operand=root))

    return mutated


NEGATION_MUTATIONS = [
    negate_assertion,
    remove_negation,
    inject_double_negation,
]