from __future__ import annotations

import pytest

from toetra._cli.output import normalize_output_text


@pytest.mark.parametrize(
    "source",
    [
        "value",
        "value\n",
        "value\n\n",
        "value\r\n",
        "value\r\n\r\n",
        "value\r\n\n",
    ],
)
def test_normalize_output_text_uses_one_lf_terminator(source: str) -> None:
    assert normalize_output_text(source) == "value\n"
