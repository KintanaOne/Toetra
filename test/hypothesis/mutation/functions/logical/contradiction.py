from copy import deepcopy

from toetra._compiler.builder.assertion import (
    AndNode,
    NotNode,
    OrNode,
)

from toetra._compiler.builder.program import ProgramNode

from test.hypothesis.mutation.functions.base import (
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
    severity=MutationSeverity.CRITICAL,
    severity_score=0.95,
    impact={MutationImpact.SEMANTIC_INVALID},
    expected_failures={
        PipelineStage.SEMANTIC_ANALYSIS,
        PipelineStage.EXECUTION,
    },
    preserves_valid_ast=True,
    preserves_typing=True,
    preserves_semantic_equivalence=False,
    preserves_valid_cst=True,
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
    preserves_valid_cst=True,
)
def inject_logical_tautology(ast: ProgramNode) -> ProgramNode:
    """
    Inject tautological expressions.

    Example:
        A becomes A OR NOT(A)
    """

    mutated = deepcopy(ast)

    for p in mutated.body:

        root = deepcopy(p.rule.assertion.root)

        p.rule.assertion.root = OrNode(
            operands=[
                root,
                NotNode(operand=deepcopy(root)),
            ]
        )

    return mutated


@mutation(
    layer=MutationLayer.SEMANTIC,
    nature=MutationNature.INSERTION,
    severity=MutationSeverity.CRITICAL,
    severity_score=0.95,
    impact={MutationImpact.SEMANTIC_INVALID},
    expected_failures={PipelineStage.SEMANTIC_ANALYSIS},
    preserves_valid_ast=True,
    preserves_typing=True,
    preserves_semantic_equivalence=False,
    preserves_valid_cst=True,
    deterministic=True,
    reversible=False,
)
def inject_global_contradiction(ast: ProgramNode) -> ProgramNode:
    """
    A → B AND A → NOT B
    """
    mutated = deepcopy(ast)

    for p in mutated.body:
        root = deepcopy(p.rule.assertion.root)

        contradiction = AndNode(operands=[root, NotNode(operand=deepcopy(root))])

        p.rule.assertion.root = contradiction

    return mutated
