
import random
from copy import deepcopy

from dsl.builder.assertion import (
    ImplicationNode,
)

from dsl.builder.program import ProgramNode

from test.hypothesis.mutation.functions.base import (
    MutationLayer,
    MutationLayer,
    mutation,
    MutationImpact,
    MutationNature,
    MutationSeverity,
    PipelineStage,
)

@mutation(
    layer=MutationLayer.LEXICAL,
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
def reverse_implication(ast: ProgramNode) -> ProgramNode:
    """
    Reverse implication direction.

    Example:
        A -> B becomes B -> A
    """

    mutated = deepcopy(ast)

    for p in mutated.body:

        root = p.rule.assertion.root

        if isinstance(root, ImplicationNode):
            root.left, root.right = root.right, root.left

    return mutated

IMPLICATION_MUTATIONS = [
    reverse_implication,
]