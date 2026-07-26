# test/hypothesis/mutations/semantic/causality.py

"""
Semantic causality mutations.

GOAL:
    Break semantic causal relationships.

ROLE IN Toetra:
    - stress implication semantics
    - reverse semantic directionality
    - validate causal consistency

CHARACTERISTICS:
    ✔ AST valid
    ✔ syntax valid
    ✔ typing preserved
    ❌ semantic causality corrupted
"""

from copy import deepcopy

from toetra._compiler.ast.nodes.assertion import ImplicationNode
from toetra._compiler.ast.nodes.program import ProgramNode
from test.hypothesis.mutation.decorators.mutation import mutation

from test.hypothesis.mutation.metadata.contract import (
    MutationContract,
    PreservationLevel,
)

from test.hypothesis.mutation.metadata.enums import (
    Domain,
    Layer,
    Nature,
    Strategy,
)


@mutation(
    name="reverse_causality",
    layer=Layer.AST,
    nature=Nature.REORDERING,
    strategy=Strategy.CORRUPTED,
    domain=Domain.SEMANTIC,
    severity=0.8,
    contract=MutationContract(
        cst=PreservationLevel.FULL,
        ast=PreservationLevel.FULL,
        typing=PreservationLevel.FULL,
        semantics=PreservationLevel.NONE,
    ),
)
def reverse_causality(
    ast: ProgramNode,
) -> ProgramNode:
    """
    Reverse implication direction.

    A -> B becomes B -> A
    """

    mutated = deepcopy(ast)

    for property_node in mutated.body:

        root = property_node.rule.assertion.root

        if isinstance(root, ImplicationNode):

            root.left, root.right = (
                root.right,
                root.left,
            )

    return mutated
