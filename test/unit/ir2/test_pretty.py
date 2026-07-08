from dsl.ir.ir1.nodes import ComparisonIR
from dsl.ir.ir2.enums import Polarity
from dsl.ir.ir2.nodes import (
    ClauseIR2,
    CNFFormulaIR2,
    DNFFormulaIR2,
    LiteralIR2,
    TermIR2,
)
from dsl.ir.ir2.pretty import pretty_formula
from dsl.language.vocabulary.operators import EnumComparisonOperator


def _cmp(name: str) -> ComparisonIR:
    return ComparisonIR(
        entity="_x", feature=name, op=EnumComparisonOperator.LTE, value=1
    )


def test_pretty_dnf_single_term_omits_branch_index_and_displays_polarity():
    formula = DNFFormulaIR2(
        terms=(
            TermIR2(
                literals=(
                    LiteralIR2(atom=_cmp("a"), polarity=Polarity.POSITIVE),
                    LiteralIR2(atom=_cmp("b"), polarity=Polarity.NEGATIVE),
                )
            ),
        )
    )

    rendered = pretty_formula(formula)

    assert rendered == "\n".join(
        [
            "DNF",
            "  AND",
            "    LITERAL[positive](_x.a <= 1)",
            "    LITERAL[negative](_x.b <= 1)",
        ]
    )
    assert "term[0]" not in rendered
    assert "branch[0]" not in rendered
    assert "NOT _x.b" not in rendered


def test_pretty_dnf_multiple_terms_uses_human_readable_branches():
    formula = DNFFormulaIR2(
        terms=(
            TermIR2(literals=(LiteralIR2(atom=_cmp("a"), polarity=Polarity.POSITIVE),)),
            TermIR2(literals=(LiteralIR2(atom=_cmp("b"), polarity=Polarity.NEGATIVE),)),
        )
    )

    rendered = pretty_formula(formula)

    assert "branch[0] AND" in rendered
    assert "branch[1] AND" in rendered
    assert "term[0]" not in rendered


def test_pretty_cnf_single_clause_omits_clause_index_and_displays_polarity():
    formula = CNFFormulaIR2(
        clauses=(
            ClauseIR2(
                literals=(
                    LiteralIR2(atom=_cmp("a"), polarity=Polarity.POSITIVE),
                    LiteralIR2(atom=_cmp("b"), polarity=Polarity.NEGATIVE),
                )
            ),
        )
    )

    rendered = pretty_formula(formula)

    assert rendered == "\n".join(
        [
            "CNF",
            "  OR",
            "    LITERAL[positive](_x.a <= 1)",
            "    LITERAL[negative](_x.b <= 1)",
        ]
    )
    assert "clause[0]" not in rendered
