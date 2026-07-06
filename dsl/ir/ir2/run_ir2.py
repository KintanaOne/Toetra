from __future__ import annotations

from dsl.ir.ir1.run_ir1 import run_ir
from dsl.ir.ir2.builder import IR2Builder
from dsl.ir.ir2.pretty import pretty_print_ir2_tasks
from dsl.ir.normalization.nnf import NNFNormalizer


DEFAULT_SAMPLE = '''
model := "model.onnx"
target := MyTarget

[LOGIC]:
forall => a <= 1 -> b <= 2 using Z3
'''


def run_ir2(source: str):
    ir1_tasks = run_ir(source)
    nnf_tasks = NNFNormalizer().normalize_tasks(ir1_tasks)
    return IR2Builder().build_tasks(nnf_tasks)


if __name__ == "__main__":
    tasks = run_ir2(DEFAULT_SAMPLE)
    pretty_print_ir2_tasks(tasks)
