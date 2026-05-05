# Vocabulary Registry Architecture

## 1. Purpose

Centralize reusable vocabulary fragments used by grammar generation.

---

## 2. Responsibilities

Vocabulary registries provide:

- logical operators,
- quantifiers,
- metrics,
- functions,
- backend identifiers,
- DSL primitives.

---

## 3. Architecture

```mermaid
flowchart TD

    A[operators.py]
    B[quantifiers.py]
    C[properties.py]
    D[backends.py]
    E[metrics.py]
    F[functions.py]

    A --> H[OFFICIAL_MAPS]
    B --> H
    C --> H
    D --> H
    E --> H
    F --> H

    H --> I[Grammar Header Generation]

    J[structural_keywords.py]
        --> K[Structural Keyword Registry]

```

---

## 4. Invariants

* Vocabulary injection must remain deterministic.
* Registry composition must remain centralized.
* Vocabulary definitions must remain backend-agnostic.
