import random
from copy import deepcopy

from toetra._compiler.builder.program import ProgramNode
from toetra._compiler.builder.assertion import NotNode, AndNode

from tests.property_based.mutation.functions.base import (
    mutation,
    MutationLayer,
    MutationNature,
    MutationSeverity,
    MutationImpact,
    PipelineStage,
)


@mutation(
    layer=MutationLayer.SEMANTIC,
    nature=MutationNature.SUBSTITUTION,
    severity=MutationSeverity.HIGH,
    severity_score=0.8,
    impact={MutationImpact.SEMANTIC_INVALID},
    expected_failures={PipelineStage.SEMANTIC_ANALYSIS},
    preserves_valid_ast=True,
    preserves_typing=True,
    preserves_semantic_equivalence=False,
    preserves_valid_cst=True,
    deterministic=True,
    reversible=False,
)
def corrupt_semantic_context(ast: ProgramNode) -> ProgramNode:
    """
    Replace semantic domain context.
    """
    mutated = deepcopy(ast)

    for p in mutated.body:
        if hasattr(p.rule.assertion, "context") and p.rule.assertion.context:
            ctx = p.rule.assertion.context

            # swap incompatible semantic domain
            ctx.problem = random.choice(list(ctx.problem.__class__))

    return mutated


@mutation(
    layer=MutationLayer.SEMANTIC,
    nature=MutationNature.CORRUPTION,
    severity=MutationSeverity.HIGH,
    severity_score=0.9,
    impact={MutationImpact.SEMANTIC_INVALID},
    expected_failures={PipelineStage.SEMANTIC_ANALYSIS},
    preserves_valid_ast=True,
    preserves_typing=True,
    preserves_semantic_equivalence=False,
    preserves_valid_cst=True,
    deterministic=True,
    reversible=False,
)
def break_relational_consistency(ast: ProgramNode) -> ProgramNode:
    """
    Break relational constraints between assertions.
    """
    mutated = deepcopy(ast)

    body = mutated.body
    if len(body) > 1:
        body.reverse()

    return mutated


@mutation(
    layer=MutationLayer.SEMANTIC,
    nature=MutationNature.CORRUPTION,
    severity=MutationSeverity.CRITICAL,
    severity_score=1.0,
    impact={MutationImpact.SEMANTIC_INVALID},
    expected_failures={PipelineStage.SEMANTIC_ANALYSIS},
    preserves_valid_ast=True,
    preserves_typing=True,
    preserves_semantic_equivalence=False,
    preserves_valid_cst=True,
    deterministic=True,
    reversible=False,
)
def violate_constraints(ast: ProgramNode) -> ProgramNode:
    """
    Inject impossible constraints (domain-level).

    Example:
        A becomes A AND NOT(A)
    """
    mutated = deepcopy(ast)

    for p in mutated.body:
        root = p.rule.assertion.root

        # wrap in impossible constraint
        p.rule.assertion.root = AndNode([root, NotNode(root)])

    return mutated


CONTRADICTION_MUTATIONS = [
    corrupt_semantic_context,
    break_relational_consistency,
    violate_constraints,
]
