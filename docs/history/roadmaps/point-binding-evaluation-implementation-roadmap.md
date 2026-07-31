# Point-based semantics

> **Status:** Delivered before `1.0.0rc1`

Early specifications could reason about a model output, but the language needed
an explicit way to say which input point produced each evaluation. Point-based
semantics supplied that identity across the complete compiler and runtime.

## Language model

The language introduced:

- first-class named points and global anchors;
- homogeneous quantified bindings;
- point-specific domains and restrictions;
- indexed model evaluations such as `target[x]`;
- deterministic default-point resolution when exactly one point is visible;
- explicit rejection of ambiguous or unsupported binding structures.

## Compiler propagation

Point identity was preserved from parsing through the AST, semantic environment,
IR1, and IR2. Restrictions and domains became assumptions attached to their
owning point, while model evaluations retained stable `(model, point, output)`
identity.

The model bridge emitted one deduplicated model equation per referenced point.
The Z3 translation used collision-free symbols so multi-point properties could
be checked without accidentally merging evaluations.

## Runtime evidence

Inline anchors and reference-dataset anchors were resolved before execution.
Reports grouped assignments and evaluations by point, and replay reconstructed
each counterexample or witness against the real sklearn estimator.

The resulting behavior is protected by the
[point-binding test matrix](../../testing/point-binding-evaluation-test-matrix.md)
and the [point-binding contract](../../contracts/point-binding-and-evaluation.md).
