# Body Structure

## Overview

The **body** of a FORML program is where the core specifications are declared. It contains one or more **properties** that define the conditions the model must satisfy.

Each property follows this general form:

```
[PROPERTY_TYPE] : property_expr -> assertion [using backend]
```

* `PROPERTY_TYPE` categorizes the property (`ROBUSTNESS`, `FAIRNESS`, etc.)
* `property_expr` defines the semantic context (global, local, pairwise, pointwise)
* `assertion` is the logical condition to be satisfied
* `using backend` optionally specifies a verification backend or abstractor

---

## 1️⃣ Structure of a Property

Each property is composed of four main blocks:

| Block                                     | Description                                                                                       |
| ----------------------------------------- | ------------------------------------------------------------------------------------------------- |
| **Property Type**                         | Defines the category of the property (ROBUSTNESS, FAIRNESS, STABILITY, PAIRWISE, POINTWISE, etc.) |
| **Property Expression (`property_expr`)** | Specifies the semantic context: which inputs, points, or pairs the assertion applies to           |
| **Assertion**                             | The condition that must hold within the context defined by `property_expr`                        |
| **Abstractor / Backend**                  | Optional; selects a verification engine or abstraction technique                                  |

> ⚠️ Each property can contain **only one type** of `property_expr`.

---

## 2️⃣ Types of `property_expr`

| Block         | Description                                                                    | Example                            |
| ------------- | ------------------------------------------------------------------------------ | ---------------------------------- |
| **Quantifier** | Applies to **all elements** of a set; allows global generalization             | `forall with feature("valA", "valB")` OR `exists with feature("valA", "valB")`|
| **Anchor**    | Focused on a **specific reference point** `x₀`, optionally with a neighborhood | `at x0 in neighborhood(L2,0.01)`      |
| **Check**     | Strictly **pointwise**; evaluated exactly at one point                         | `check_at x0`                      |
| **Pairwise**  | Relational property between two entities                                       | `x1 ~ x2 in neighborhood(L2,0.01)` ` |

---

## 3️⃣ Assertion

* The **assertion** defines what must be true in the context of the property expression.
* Can be a **problem expression** like `CLASSIFICATION.EQUAL()`, `PREDICTION.BETWEEN()`
* Or a **logic expression** like `(x == 1 -> y != 0)`
* Always applied **within the semantic context** of the property expression.

---

## 4️⃣ Abstractor / Backend

* Optional block specifying the verification tool or abstraction method.
* Examples: `using ERAN("zonotope")`, `using Z3`
* Allows fine control over how the property is evaluated.

---

## 5️⃣ Semantic Table

| Property Type  | Global Syntax                                                          | Global Semantics                                                             | Local Syntax (`x₀`)                                                    | Local Semantics                                                                      | Support Tool / Backend | `.forml` Example                                                                           |
| -------------- | ---------------------------------------------------------------------- | ---------------------------------------------------------------------------- | ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------ | ---------------------- | ------------------------------------------------------------------------------------------ |
| **ROBUSTNESS** | `[ROBUSTNESS]: forall in neighborhood(L2,0.01) -> CLASSIFICATION.EQUAL()` | All inputs in the set must yield the same class under small L2 perturbations | `[ROBUSTNESS]: at x0 in neighborhood(L2,0.01) -> CLASSIFICATION.EQUAL()`    | For a specific input `x₀`, its perturbed neighbors must yield same prediction        | ERAN, ZONOTOPE         | `[ROBUSTNESS]: at x0 in neighborhood(L2,0.01) -> CLASSIFICATION.EQUAL() using ERAN("zonotope")` |
| **FAIRNESS**   | `[FAIRNESS]: forall in groupA -> CLASSIFICATION.EQUAL()`               | All inputs in groupA must satisfy equality/fairness constraints              | `[FAIRNESS]: at x0 in groupA -> CLASSIFICATION.EQUAL()`                  | For a specific input `x₀` in groupA, its neighborhood or point must satisfy fairness | Z3, Custom             | `[FAIRNESS]: at x0 in groupA -> CLASSIFICATION.EQUAL()`                                      |
| **STABILITY**  | `[STABILITY]: forall in neighborhood(L2,0.05) -> CLASSIFICATION.EQUAL()`  | Small perturbations of all inputs should not change predictions              | `[STABILITY]: at x0 in neighborhood(L2,0.05) -> CLASSIFICATION.EQUAL()`     | Only the perturbations around `x₀` must preserve prediction                          | ERAN, Zonotope         | `[STABILITY]: at x0 in neighborhood(L2,0.05) -> CLASSIFICATION.EQUAL()`                         |
| **PAIRWISE**   | `x ~ x' in neighborhood(L2, eps=0.01) -> CLASSIFICATION.EQUAL() using Z3` | All pairs of inputs within distance threshold must satisfy assertion         | `x ~ x' in neighborhood(L2, eps=0.01) -> CLASSIFICATION.EQUAL() using Z3` | Only the selected pair `x₁`, `x₂` is checked                                         | ERAN, Custom           | `x ~ x' in neighborhood(L2, eps=0.01) -> CLASSIFICATION.EQUAL() using Z3`                     |
| **POINTWISE**  | `[POINTWISE]: check_at x0 -> CLASSIFICATION.EQUAL()`                     | Assertion evaluated exactly at one point, no generalization                  | `[POINTWISE]: check_at x0 -> CLASSIFICATION.EQUAL()`                     | Same as global since it’s strictly one point                                         | Any backend            | `[POINTWISE]: check_at x0 -> CLASSIFICATION.EQUAL()`                                         |

---

## 6️⃣ Example Full Property

```
[ROBUSTNESS] :
at x0 in neighborhood(L2,0.01) -> CLASSIFICATION.EQUAL() using ERAN("zonotope")
```

* **Property Type** → `ROBUSTNESS`
* **Property Expression** → `at x0 in neighborhood(L2,0.01)` (local focus)
* **Assertion** → `CLASSIFICATION.EQUAL()`
* **Backend** → `ERAN("zonotope")`

This structure ensures clarity and consistency when writing properties in FORML.
