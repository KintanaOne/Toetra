"""
Logical mutations (ASSERTION LEVEL)

GOAL:
    Modify the logical meaning of assertions while
    preserving AST structure and syntax validity.

ROLE IN FORML:
    - test logical consistency
    - validate semantic analyzers
    - stress formal verification rules
    - detect silent logical corruption

CHARACTERISTICS:
    ✔ AST valid
    ✔ syntax valid
    ✔ typing usually preserved
    ❌ logical meaning corrupted
"""

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
    mutation,
    MutationImpact,
    MutationNature,
    MutationSeverity,
    PipelineStage,
)

# =========================================================
# MUTATION 1 : reverse implication
# =========================================================


@mutation(
    nature=MutationNature.LOGICAL,
    severity=MutationSeverity.HIGH,
    severity_score=0.75,
    impact={MutationImpact.SEMANTIC_INVALID},
    expected_failures={PipelineStage.SEMANTIC_ANALYSIS},
    preserves_valid_ast=True,
    preserves_typing=True,
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


# =========================================================
# MUTATION 2 : negate assertion
# =========================================================


@mutation(
    nature=MutationNature.LOGICAL,
    severity=MutationSeverity.HIGH,
    severity_score=0.8,
    impact={MutationImpact.SEMANTIC_INVALID},
    expected_failures={PipelineStage.SEMANTIC_ANALYSIS},
    preserves_valid_ast=True,
    preserves_typing=True,
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


# =========================================================
# MUTATION 3 : swap boolean operators
# =========================================================


@mutation(
    nature=MutationNature.LOGICAL,
    severity=MutationSeverity.MEDIUM,
    severity_score=0.6,
    impact={MutationImpact.SEMANTIC_INVALID},
    expected_failures={PipelineStage.SEMANTIC_ANALYSIS},
    preserves_valid_ast=True,
    preserves_typing=True,
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


# =========================================================
# MUTATION 4 : remove negation
# =========================================================


@mutation(
    nature=MutationNature.LOGICAL,
    severity=MutationSeverity.MEDIUM,
    severity_score=0.55,
    impact={MutationImpact.SEMANTIC_INVALID},
    expected_failures={PipelineStage.SEMANTIC_ANALYSIS},
    preserves_valid_ast=True,
    preserves_typing=True,
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


# =========================================================
# MUTATION 5 : duplicate operand
# =========================================================


@mutation(
    nature=MutationNature.LOGICAL,
    severity=MutationSeverity.LOW,
    severity_score=0.3,
    impact={MutationImpact.NONE},
    expected_failures=set(),
    preserves_valid_ast=True,
    preserves_typing=True,
    preserves_semantic_equivalence=True,
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


# =========================================================
# MUTATION 6 : remove operand
# =========================================================


@mutation(
    nature=MutationNature.LOGICAL,
    severity=MutationSeverity.HIGH,
    severity_score=0.7,
    impact={MutationImpact.SEMANTIC_INVALID},
    expected_failures={PipelineStage.SEMANTIC_ANALYSIS},
    preserves_valid_ast=True,
    preserves_typing=True,
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


# =========================================================
# MUTATION 7 : permute operands
# =========================================================


@mutation(
    nature=MutationNature.LOGICAL,
    severity=MutationSeverity.INFO,
    severity_score=0.1,
    impact={MutationImpact.NONE},
    expected_failures=set(),
    preserves_valid_ast=True,
    preserves_typing=True,
    preserves_semantic_equivalence=True,
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


# =========================================================
# MUTATION 8 : inject tautology
# =========================================================


@mutation(
    nature=MutationNature.LOGICAL,
    severity=MutationSeverity.HIGH,
    severity_score=0.8,
    impact={MutationImpact.SEMANTIC_INVALID},
    expected_failures={PipelineStage.SEMANTIC_ANALYSIS},
    preserves_valid_ast=True,
    preserves_typing=True,
)
def inject_tautology(ast: ProgramNode) -> ProgramNode:
    """
    Inject tautological expressions.

    Example:
        A becomes A OR NOT(A)
    """

    mutated = deepcopy(ast)

    for p in mutated.body:

        root = deepcopy(p.rule.assertion.root)

        tautology = OrNode(
            operands=[
                root,
                NotNode(operand=deepcopy(root)),
            ]
        )

        p.rule.assertion.root = tautology

    return mutated


# =========================================================
# MUTATION 9 : inject contradiction
# =========================================================


@mutation(
    nature=MutationNature.LOGICAL,
    severity=MutationSeverity.CRITICAL,
    severity_score=0.95,
    impact={MutationImpact.SEMANTIC_INVALID},
    expected_failures={
        PipelineStage.SEMANTIC_ANALYSIS,
        PipelineStage.EXECUTION,
    },
    preserves_valid_ast=True,
    preserves_typing=True,
)
def inject_contradiction(ast: ProgramNode) -> ProgramNode:
    """
    Inject contradictory expressions.

    Example:
        A becomes A AND NOT(A)
    """

    mutated = deepcopy(ast)

    for p in mutated.body:

        root = deepcopy(p.rule.assertion.root)

        contradiction = AndNode(
            operands=[
                root,
                NotNode(operand=deepcopy(root)),
            ]
        )

        p.rule.assertion.root = contradiction

    return mutated


# =========================================================
# MUTATION 10 : double negation
# =========================================================


@mutation(
    nature=MutationNature.LOGICAL,
    severity=MutationSeverity.INFO,
    severity_score=0.1,
    impact={MutationImpact.NONE},
    expected_failures=set(),
    preserves_valid_ast=True,
    preserves_typing=True,
    preserves_semantic_equivalence=True,
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


# =========================================================
# MUTATION 11 : flatten boolean tree
# =========================================================


@mutation(
    nature=MutationNature.LOGICAL,
    severity=MutationSeverity.INFO,
    severity_score=0.15,
    impact={MutationImpact.NONE},
    expected_failures=set(),
    preserves_valid_ast=True,
    preserves_typing=True,
    preserves_semantic_equivalence=True,
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


# =========================================================
# REGISTRY
# =========================================================

LOGICAL_MUTATIONS = [
    reverse_implication,
    negate_assertion,
    swap_boolean_operators,
    remove_negation,
    duplicate_operand,
    remove_operand,
    permute_operands,
    inject_tautology,
    inject_contradiction,
    inject_double_negation,
    flatten_boolean_tree,
]


# =========================================================
# ENGINE
# =========================================================


def apply_logical_mutations(
    ast: ProgramNode,
    n: int = 1,
) -> ProgramNode:
    """
    Apply N logical mutations.
    """

    mutated = ast

    for _ in range(n):
        mutation_fn = random.choice(LOGICAL_MUTATIONS)
        mutated = mutation_fn(mutated)

    return mutated
