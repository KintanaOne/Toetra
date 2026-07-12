from __future__ import annotations

from dsl.ir.ir1.nodes import (
    ConstantExpressionIR,
    DomainEntryIR,
    FiniteSetDomainIR,
    IntervalDomainIR,
    SymbolLiteralIR,
)
from dsl.ir.ir1.run_ir1 import run_ir
from dsl.language.vocabulary.domains import EnumBoundaryKind
from dsl.semantic.types.enums import EnumDataType


def test_typed_domain_survives_ast_to_ir1_without_legacy_name_values_shape():
    source = """
model := "model.onnx"
target := MyTarget

[LOGIC]:
forall applicant
    with domain(
        applicant.age: ]18, 65],
        applicant.segment: {retail, corporate},
        applicant.score: {0.0, 7.0}
    )
    => target <= 7
"""

    (task,) = run_ir(source)

    assert task.scope.variables == {"applicant": "symbolic"}
    assert task.scope.domain is not None
    assert len(task.scope.domain.entries) == 3

    age, segment, score = task.scope.domain.entries
    assert age == DomainEntryIR(
        entity="applicant",
        feature="age",
        constraint=IntervalDomainIR(
            lower=ConstantExpressionIR(18, EnumDataType.INT),
            upper=ConstantExpressionIR(65, EnumDataType.INT),
            lower_boundary=EnumBoundaryKind.OPEN,
            upper_boundary=EnumBoundaryKind.CLOSED,
        ),
    )
    assert segment == DomainEntryIR(
        entity="applicant",
        feature="segment",
        constraint=FiniteSetDomainIR(
            values=(SymbolLiteralIR("retail"), SymbolLiteralIR("corporate"))
        ),
    )
    assert score == DomainEntryIR(
        entity="applicant",
        feature="score",
        constraint=FiniteSetDomainIR(
            values=(
                ConstantExpressionIR(0.0, EnumDataType.FLOAT),
                ConstantExpressionIR(7.0, EnumDataType.FLOAT),
            )
        ),
    )
