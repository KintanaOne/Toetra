from __future__ import annotations

from dsl.ir.ir2.explain import IR2ExplainOptions, explain_ir2_tasks
from dsl.ir.ir2.examples.samples import DEFAULT_SAMPLE
from dsl.ir.ir2.pretty import pretty_print_ir2_tasks
from dsl.ir.ir2.run_ir2 import run_ir2


def main() -> None:
    """Print a compact IR2 demo without model assumptions."""

    tasks = run_ir2(DEFAULT_SAMPLE)

    print("\n=== IR2 PRETTY — SIMPLE LOGIC ===\n")
    pretty_print_ir2_tasks(tasks)

    print("\n=== IR2 EXPLAIN — SIMPLE LOGIC ===\n")
    print(
        explain_ir2_tasks(
            tasks,
            options=IR2ExplainOptions(
                include_assumption_formulas=True,
                include_requirements=True,
                include_mermaid=True,
            ),
        )
    )


if __name__ == "__main__":
    main()
