from __future__ import annotations

from toetra._compiler.ir.ir2.pretty import pretty_ir2_task
from toetra._compiler.ir.ir2.run_ir2 import run_ir2_with_model_schema
from toetra._models.encoder.context import ModelEncodingContext
from tests.support.model_semantics import make_binary_logistic_schema
from tests.support.paths import FIXTURES_ROOT, GOLDEN_ROOT

_INPUT_ROOT = FIXTURES_ROOT / "ir2"
_EXPECTED_ROOT = GOLDEN_ROOT / "ir2"


class _NoopEncoderFactory:
    def encode(self, schema, evaluations, *, context=None):  # noqa: ANN001, ANN201
        del schema, evaluations, context
        return ()


def test_binary_label_lowering_golden() -> None:
    source = (_INPUT_ROOT / "binary_label.toetra").read_text(encoding="utf-8")
    task = run_ir2_with_model_schema(
        source,
        schema=make_binary_logistic_schema(),
        model_context=ModelEncodingContext(include_model_constraints=False),
        encoder_factory=_NoopEncoderFactory(),  # type: ignore[arg-type]
    )[0]
    actual = pretty_ir2_task(task).rstrip() + "\n"
    expected = (_EXPECTED_ROOT / "binary_label.ir2.txt").read_text(encoding="utf-8")
    assert actual == expected
