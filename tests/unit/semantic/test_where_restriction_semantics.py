from __future__ import annotations

from toetra._compiler.ast.nodes.assertion import AndNode, ImplicationNode, NotNode
from toetra._compiler.semantic.context.restrictions import VerificationSemantics
from tests.support.semantic_restrictions import parse_and_validate


def _source(quantifier: str, restriction: str = "x1.a >= x0.a") -> str:
    return f"""
        model := "model.joblib"
        target := score

        [LOGIC]:
        {quantifier} x0, x1
        where {restriction}
        => target[x1] >= target[x0]
        """


def test_low_where_001_universal_restriction_builds_implication() -> None:
    program = parse_and_validate(_source("forall"))
    semantic = program.body[0].semantic
    assert semantic is not None
    assert isinstance(semantic.logical_root, ImplicationNode)
    assert semantic.context is not None
    assert semantic.context.restriction_semantics is not None
    assert semantic.context.restriction_semantics.quantifier == "forall"


def test_low_where_002_existential_restriction_builds_conjunction() -> None:
    program = parse_and_validate(_source("exists"))
    semantic = program.body[0].semantic
    assert semantic is not None
    assert isinstance(semantic.logical_root, AndNode)
    assert semantic.context is not None
    restriction_semantics = semantic.context.restriction_semantics
    assert restriction_semantics is not None
    assert restriction_semantics.quantifier == "exists"


def test_low_where_003_universal_verification_body_is_r_and_not_p() -> None:
    program = parse_and_validate(_source("forall"))
    semantic = program.body[0].semantic
    assert semantic is not None
    assert semantic.verification_semantics == VerificationSemantics.REFUTATION.value
    assert isinstance(semantic.verification_root, AndNode)
    assert len(semantic.verification_root.operands) == 2
    assert isinstance(semantic.verification_root.operands[1], NotNode)


def test_low_where_004_existential_verification_body_is_r_and_p() -> None:
    program = parse_and_validate(_source("exists"))
    semantic = program.body[0].semantic
    assert semantic is not None
    assert semantic.verification_semantics == VerificationSemantics.SATISFACTION.value
    assert isinstance(semantic.verification_root, AndNode)
    assert semantic.verification_root is semantic.logical_root


def test_low_where_005_compound_restriction_structure_is_preserved() -> None:
    program = parse_and_validate(_source("forall", "(x1.a >= x0.a and x1.b == x0.b)"))
    semantic = program.body[0].semantic
    assert semantic is not None
    assert isinstance(semantic.restriction_root, AndNode)
    assert len(semantic.restriction_root.operands) == 2
