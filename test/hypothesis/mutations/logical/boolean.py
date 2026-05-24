

from ctypes.wintypes import BOOLEAN
import random
from copy import deepcopy

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
    severity=MutationSeverity.MEDIUM,
    severity_score=0.6,
    impact={MutationImpact.SEMANTIC_INVALID},
    expected_failures={PipelineStage.SEMANTIC_ANALYSIS},
    preserves_valid_ast=True,
    preserves_typing=True,
    preserves_semantic_equivalence=False,
    preserves_valid_cst=True
)
def swap_boolean_operators(ast: ProgramNode) -> ProgramNode:
    """
    Swap AND/OR operators.

    Example:
        A AND B becomes A OR B
    """

    mutated = deepcopy(ast)

    for p in mutated.body:

        root = p.rule.assertion.root

        if isinstance(root, AndNode):

            p.rule.assertion.root = OrNode(operands=root.operands)

        elif isinstance(root, OrNode):

            p.rule.assertion.root = AndNode(operands=root.operands)

    return mutated


@mutation(
    layer=MutationLayer.LOGICAL,
    nature=MutationNature.PERTURBATION,
    severity=MutationSeverity.LOW,
    severity_score=0.3,
    impact={MutationImpact.NONE},
    expected_failures=set(),
    preserves_valid_ast=True,
    preserves_typing=True,
    preserves_semantic_equivalence=True,
    preserves_valid_cst=True
)
def duplicate_operand(ast: ProgramNode) -> ProgramNode:
    """
    Duplicate logical operands.

    Example:
        A AND B becomes A AND A

    NOTE:
        Often logically equivalent.
    """

    mutated = deepcopy(ast)

    for p in mutated.body:

        root = p.rule.assertion.root

        if isinstance(root, (AndNode, OrNode)):

            if not root.operands:
                continue

            first = deepcopy(root.operands[0])

            root.operands = [
                first,
                deepcopy(first),
            ]

    return mutated


@mutation(
    layer=MutationLayer.LOGICAL,
    nature=MutationNature.DELETION,
    severity=MutationSeverity.HIGH,
    severity_score=0.7,
    impact={MutationImpact.SEMANTIC_INVALID},
    expected_failures={PipelineStage.SEMANTIC_ANALYSIS},
    preserves_valid_ast=True,
    preserves_typing=True,
    preserves_semantic_equivalence=False,
    preserves_valid_cst=True
)
def remove_operand(ast: ProgramNode) -> ProgramNode:
    """
    Remove one operand from boolean expressions.

    Example:
        A AND B becomes A
    """

    mutated = deepcopy(ast)

    for p in mutated.body:

        root = p.rule.assertion.root

        if isinstance(root, (AndNode, OrNode)):

            if len(root.operands) <= 1:
                continue

            root.operands.pop()

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
def permute_operands(ast: ProgramNode) -> ProgramNode:
    """
    Randomly permute boolean operands.

    Example:
        A AND B AND C becomes C AND A AND B

    NOTE:
        Logically equivalent for commutative operators.
    """

    mutated = deepcopy(ast)

    for p in mutated.body:

        root = p.rule.assertion.root

        if isinstance(root, (AndNode, OrNode)):
            random.shuffle(root.operands)

    return mutated


@mutation(
    layer=MutationLayer.LOGICAL,
    nature=MutationNature.PERTURBATION,
    severity=MutationSeverity.INFO,
    severity_score=0.15,
    impact={MutationImpact.NONE},
    expected_failures=set(),
    preserves_valid_ast=True,
    preserves_typing=True,
    preserves_semantic_equivalence=True,
    preserves_valid_cst=True
)
def flatten_boolean_tree(ast: ProgramNode) -> ProgramNode:
    """
    Flatten nested boolean operators.

    Example:
        A AND (B AND C)
        becomes
        A AND B AND C
    """

    mutated = deepcopy(ast)

    for p in mutated.body:

        root = p.rule.assertion.root

        if isinstance(root, AndNode):

            flattened = []

            for operand in root.operands:

                if isinstance(operand, AndNode):
                    flattened.extend(operand.operands)

                else:
                    flattened.append(operand)

            root.operands = flattened

        elif isinstance(root, OrNode):

            flattened = []

            for operand in root.operands:

                if isinstance(operand, OrNode):
                    flattened.extend(operand.operands)

                else:
                    flattened.append(operand)

            root.operands = flattened

    return mutated


BOOLEAN_MUTATIONS = [
    swap_boolean_operators,
    duplicate_operand,
    remove_operand,
    permute_operands,
    flatten_boolean_tree,
]