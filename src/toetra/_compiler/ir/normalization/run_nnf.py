from __future__ import annotations

from toetra._compiler.ir.ir1.pretty import pretty_print_tasks
from toetra._compiler.ir.ir1.run_ir1 import run_ir
from toetra._compiler.ir.normalization.nnf import NNFNormalizer

DEFAULT_SAMPLE = """
model := "model.onnx"
target := MyTarget

[LOGIC]:
forall x0 => NOT (a <= 1 AND b <= 2) using Z3
"""


def run_nnf(source: str):
    """
    Full pipeline until NNF.

    Steps:
        1. Parse CST
        2. Build AST
        3. Semantic validation
        4. Translate to IR1
        5. Normalize IR1 query to NNF
    """

    tasks = run_ir(source)
    return NNFNormalizer().normalize_tasks(tasks)


if __name__ == "__main__":
    tasks = run_nnf(DEFAULT_SAMPLE)
    print("\n=== NNF OUTPUT ===\n")
    pretty_print_tasks(tasks)
