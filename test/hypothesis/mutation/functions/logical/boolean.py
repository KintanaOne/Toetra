

from __future__ import annotations

import random

from copy import deepcopy

from test.hypothesis.mutation.decorators.mutation import mutation

from test.hypothesis.mutation.metadata.contract import MutationContract, PreservationLevel
from test.hypothesis.mutation.metadata.enums import (
    Domain,
    Layer,
    Nature,
    Strategy,
)

from dsl.ast.nodes.assertion import AndNode, OrNode, NotNode

# =========================================================
# CONTRACTS
# =========================================================

FULL_PRESERVE = MutationContract(
    cst=PreservationLevel.FULL,
    ast=PreservationLevel.FULL,
    typing=PreservationLevel.FULL,
    semantics=PreservationLevel.FULL,
)

PARTIAL_SEMANTIC = MutationContract(
    cst=PreservationLevel.FULL,
    ast=PreservationLevel.FULL,
    typing=PreservationLevel.FULL,
    semantics=PreservationLevel.PARTIAL,
)

NONE_SEMANTIC = MutationContract(
    cst=PreservationLevel.FULL,
    ast=PreservationLevel.FULL,
    typing=PreservationLevel.FULL,
    semantics=PreservationLevel.NONE,
)


# =========================================================
# 1. SWAP AND / OR
# =========================================================

@mutation(
    name="swap_boolean_operators",
    layer=Layer.AST,
    nature=Nature.CORRUPTION,
    strategy=Strategy.MUTATED,
    domain=Domain.LOGICAL,
    severity=0.6,
    contract=PARTIAL_SEMANTIC,
)
def swap_boolean_operators(ast):

    mutated = deepcopy(ast)

    for p in mutated.body:

        root = p.rule.assertion.root

        if isinstance(root, AndNode):
            p.rule.assertion.root = OrNode(operands=root.operands)

        elif isinstance(root, OrNode):
            p.rule.assertion.root = AndNode(operands=root.operands)

    return mutated


# =========================================================
# 2. DUPLICATE OPERAND
# =========================================================

@mutation(
    name="duplicate_operand",
    layer=Layer.AST,
    nature=Nature.CORRUPTION,
    strategy=Strategy.MUTATED,
    domain=Domain.LOGICAL,
    severity=0.3,
    contract=FULL_PRESERVE,
)
def duplicate_operand(ast):

    mutated = deepcopy(ast)

    for p in mutated.body:

        root = p.rule.assertion.root

        if isinstance(root, (AndNode, OrNode)) and root.operands:

            first = deepcopy(root.operands[0])

            root.operands = [first, deepcopy(first)]

    return mutated


# =========================================================
# 3. REMOVE OPERAND
# =========================================================

@mutation(
    name="remove_operand",
    layer=Layer.AST,
    nature=Nature.CORRUPTION,
    strategy=Strategy.CORRUPTED,
    domain=Domain.LOGICAL,
    severity=0.7,
    contract=NONE_SEMANTIC,
)
def remove_operand(ast):

    mutated = deepcopy(ast)

    for p in mutated.body:

        root = p.rule.assertion.root

        if isinstance(root, (AndNode, OrNode)) and len(root.operands) > 1:
            root.operands.pop()

    return mutated


# =========================================================
# 4. PERMUTE OPERANDS
# =========================================================

@mutation(
    name="permute_operands",
    layer=Layer.AST,
    nature=Nature.CORRUPTION,
    strategy=Strategy.MUTATED,
    domain=Domain.LOGICAL,
    severity=0.1,
    contract=FULL_PRESERVE,
)
def permute_operands(ast):

    mutated = deepcopy(ast)

    for p in mutated.body:

        root = p.rule.assertion.root

        if isinstance(root, (AndNode, OrNode)):
            random.shuffle(root.operands)

    return mutated


# =========================================================
# 5. FLATTEN TREE
# =========================================================

@mutation(
    name="flatten_boolean_tree",
    layer=Layer.AST,
    nature=Nature.CORRUPTION,
    strategy=Strategy.MUTATED,
    domain=Domain.LOGICAL,
    severity=0.15,
    contract=FULL_PRESERVE,
)
def flatten_boolean_tree(ast):

    mutated = deepcopy(ast)

    for p in mutated.body:

        root = p.rule.assertion.root

        if isinstance(root, AndNode):

            flattened = []
            for op in root.operands:
                if isinstance(op, AndNode):
                    flattened.extend(op.operands)
                else:
                    flattened.append(op)

            root.operands = flattened

        elif isinstance(root, OrNode):

            flattened = []
            for op in root.operands:
                if isinstance(op, OrNode):
                    flattened.extend(op.operands)
                else:
                    flattened.append(op)

            root.operands = flattened

    return mutated
