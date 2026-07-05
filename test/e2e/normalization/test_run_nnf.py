from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from test.fixtures.normalization.nnf.helpers import assert_is_nnf, import_run_nnf, sexpr



def test_run_nnf_entrypoint_returns_normalized_tasks():
    source = '''
model := "model.onnx"
target := MyTarget

[LOGIC]:
check_at x0 => NOT ((x0.a <= 1 AND x0.b <= 2) -> x0.c <= 3) using Z3
'''

    run_nnf = import_run_nnf()
    tasks = run_nnf(source)

    assert len(tasks) == 1
    expr = tasks[0].query.expression

    assert sexpr(expr) == "AND(CMP(x0.a <= 1), CMP(x0.b <= 2), NOT(CMP(x0.c <= 3)))"
    assert_is_nnf(expr)



def test_run_nnf_module_is_executable_from_repo_root():
    repo_root = Path(__file__).resolve().parents[3]

    completed = subprocess.run(
        [sys.executable, "-m", "dsl.ir.normalization.run_nnf"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip(), "run_nnf module should print a non-empty output"



def test_run_nnf_entrypoint_handles_quantifier_scope():
    source = '''
model := "model.onnx"
target := MyTarget

[LOGIC]:
forall => NOT (a <= 1 AND b <= 2) using Z3
'''

    run_nnf = import_run_nnf()
    tasks = run_nnf(source)

    assert len(tasks) == 1
    task = tasks[0]

    assert task.scope.kind == "quantifier"
    assert task.scope.variables == {"_x": "symbolic"}
    assert sexpr(task.query.expression) == (
        "OR(NOT(CMP(_x.a <= 1)), NOT(CMP(_x.b <= 2)))"
    )
    assert_is_nnf(task.query.expression)
