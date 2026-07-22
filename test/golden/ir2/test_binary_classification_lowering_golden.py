from __future__ import annotations

from pathlib import Path

from dsl.ir.ir2.pretty import pretty_ir2_task
from dsl.ir.ir2.run_ir2 import run_ir2_with_model_schema
from model.encoder.context import ModelEncodingContext
from test.fixtures.model_semantic_lowering import make_binary_logistic_schema

_ROOT = Path(__file__).resolve().parent


class _NoopEncoderFactory:
    def encode(self, schema, evaluations, *, context=None):  # noqa: ANN001, ANN201
        del schema, evaluations, context
        return ()


def test_binary_label_lowering_golden() -> None:
    source = (_ROOT / "cases" / "binary_label.forml").read_text(encoding="utf-8")
    task = run_ir2_with_model_schema(
        source,
        schema=make_binary_logistic_schema(),
        model_context=ModelEncodingContext(include_model_constraints=False),
        encoder_factory=_NoopEncoderFactory(),  # type: ignore[arg-type]
    )[0]
    actual = pretty_ir2_task(task).rstrip() + "\n"
    expected = (_ROOT / "expected" / "binary_label.ir2.txt").read_text(encoding="utf-8")
    assert actual == expected
