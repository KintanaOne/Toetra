from __future__ import annotations

from dataclasses import dataclass

import pytest

from dsl.ir.ir1.nodes import LogicalIR

from test.fixtures.normalization.nnf.helpers import normalizer


@dataclass
class UnknownLogicalIR(LogicalIR):
    payload: str


def test_unknown_logical_ir_node_is_rejected_explicitly():
    with pytest.raises(TypeError):
        normalizer().normalize_expr(UnknownLogicalIR(payload="unsupported"))
