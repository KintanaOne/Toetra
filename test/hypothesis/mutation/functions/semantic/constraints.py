"""
Semantic constraint violation mutations.

GOAL:
    Inject impossible domain-level constraints.

ROLE IN FORML:
    - break business rule consistency
    - stress semantic interpretation layer
    - test cross-field validation logic

IMPORTANT:
    This is NOT logical contradiction (A AND NOT A)
    This is domain contradiction (invalid real-world constraints)
"""

from __future__ import annotations

from copy import deepcopy

from test.hypothesis.mutation.decorators.mutation import mutation

from test.hypothesis.mutation.functions.semantic.helper.engine import (
    SemanticConstraintEngine,
)
from test.hypothesis.mutation.functions.semantic.helper.extractor import (
    SemanticConstraintExtractor,
)
from test.hypothesis.mutation.functions.semantic.helper.rebuilder import (
    SemanticASTRebuilder,
)
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

# =========================================================
# MUTATION 1 : domain constraint contradiction
# =========================================================


@mutation(
    name="semantic.inject_impossible_constraint",
    layer=Layer.AST,
    nature=Nature.CORRUPTION,
    strategy=Strategy.CORRUPTED,
    domain=Domain.SEMANTIC,
    severity=0.85,
    contract=MutationContract(
        cst=PreservationLevel.FULL,
        ast=PreservationLevel.FULL,
        typing=PreservationLevel.FULL,
        semantics=PreservationLevel.NONE,
    ),
)
def inject_impossible_constraint(ast):

    mutated = deepcopy(ast)

    extractor = SemanticConstraintExtractor()
    engine = SemanticConstraintEngine()
    rebuilder = SemanticASTRebuilder()

    for property_node in mutated.body:

        # =====================================================
        # 1. AST → Semantic IR
        # =====================================================
        constraints = extractor.extract(ast)

        # =====================================================
        # 2. SEMANTIC CORRUPTION
        # =====================================================
        corrupted = engine.inject_contradiction(constraints)

        # =====================================================
        # 3. (TEMP) re-encode back into AST
        #     (we'll improve this later)
        # =====================================================
        property_node.rule.assertion.root = rebuilder.rebuild(corrupted)

    return mutated


# =========================================================
# DOMAIN VIOLATION GENERATOR (placeholder abstraction)
# =========================================================


def create_fake_domain_violation(node):
    """
    Generates a semantic contradiction predicate.

    NOTE:
        In a real FORML system, this should be replaced by:
        - schema-based constraint inversion
        - field-level rule violation
        - ontology-driven contradiction generation
    """

    # placeholder: DO NOT use logical NOT
    return node  # to be replaced by real semantic inversion engine
