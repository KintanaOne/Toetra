from __future__ import annotations

from textwrap import dedent

from dsl.backends.defaults import create_default_backend_registry
from dsl.backends.router import BackendRouter
from dsl.backends.z3_backend.runner import VerificationStatus, Z3Runner
from dsl.ir.ir1.run_ir1 import run_ir
from dsl.ir.ir2.builder import IR2Builder
from dsl.ir.ir2.context import IR2BuildContext
from dsl.ir.ir2.enums import NormalFormKind
from dsl.ir.normalization.nnf import NNFNormalizer

PROVED_SAMPLE = dedent("""
    model := "demo.onnx"
    target := MyTarget

    [LOGIC]:
    forall x0 => x0.a <= 1 OR NOT x0.a <= 1 using Z3
    """).strip()


COUNTEREXAMPLE_SAMPLE = dedent("""
    model := "demo.onnx"
    target := MyTarget

    [LOGIC]:
    forall x0 => x0.a <= 1 using Z3
    """).strip()


def run_compiler_pipeline(source: str):
    """
    Full minimal FORML → Z3 path.

    Pipeline:
        DSL source
        -> CST / AST / semantic validation
        -> IR1
        -> NNF
        -> IR2
        -> backend routing
        -> Z3 execution
    """

    ir1_tasks = run_ir(source)

    nnf_tasks = NNFNormalizer().normalize_tasks(ir1_tasks)

    ir2_tasks = IR2Builder().build_tasks(
        nnf_tasks,
        context=IR2BuildContext(
            preferred_normal_form=NormalFormKind.NNF,
            backend_hint=None,
        ),
    )

    registry = create_default_backend_registry()
    router = BackendRouter(registry)
    runner = Z3Runner()

    results = []

    for task in ir2_tasks:
        route = router.route(task)
        result = runner.run(task)

        results.append((task, route, result))

    return results


def print_case(title: str, source: str, expected: VerificationStatus) -> None:
    print("=" * 80)
    print(title)
    print("=" * 80)
    print(source)
    print()

    results = run_compiler_pipeline(source)

    for index, task_route_result in enumerate(results):
        task, route, result = task_route_result

        print(f"Task              : {index}")
        print(f"Backend routed to : {route.backend.value}")
        print(f"Route reason      : {route.reason}")
        print(f"Normal form       : {task.normal_form.value}")
        print(f"Solver status     : {result.solver_status}")
        print(f"FORML status      : {result.status.value}")

        if result.model:
            print("Counterexample    :")
            for name, value in result.model.items():
                print(f"  - {name} = {value}")

        print()

        if result.status != expected:
            raise AssertionError(
                f"Expected {expected.value}, got {result.status.value}"
            )


def main() -> None:
    print_case(
        title="CASE 1 — Property is tautological, therefore PROVED",
        source=PROVED_SAMPLE,
        expected=VerificationStatus.PROVED,
    )

    print_case(
        title="CASE 2 — Property can be violated, therefore COUNTEREXAMPLE",
        source=COUNTEREXAMPLE_SAMPLE,
        expected=VerificationStatus.COUNTEREXAMPLE,
    )

    print("✅ End-to-end Z3 demo succeeded.")


if __name__ == "__main__":
    main()
