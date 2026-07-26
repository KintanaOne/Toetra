from __future__ import annotations

from toetra._compiler.parser.parser import parse_toetra_code


def test_named_argument_words_remain_identifiers_outside_argument_positions() -> None:
    source = """
    model := "demo.onnx"
    target := MyTarget

    eps := 0.05

    anchor x0 := {
        key: 1,
        value: 2,
        of: 3,
        metric: 4,
        eps: 5
    }

    [LOGIC]:
    x0.key + x0.value + x0.of + x0.metric + x0.eps >= eps
    """

    parse_toetra_code(source)
