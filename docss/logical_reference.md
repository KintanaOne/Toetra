# Logical Symbols Reference (FORM L)

## First-Order Logic (FOL)

| Concept        | Symbol | ASCII        | Example                         |
|----------------|--------|--------------|----------------------------------|
| For all        | ∀      | `forall`     | `forall x: P(x)`                |
| Exists         | ∃      | `exists`     | `exists x: P(x)`                |
| Not            | ¬      | `not` / `!`  | `not P(x)`                      |
| And            | ∧      | `and` / `&&` | `P(x) and Q(x)`                 |
| Or             | ∨      | `or` / `||`  | `P(x) or Q(x)`                  |
| LOGIC_IMPLY    | →      | `->`         | `P(x) -> Q(x)`                  |
| Equivalent     | ↔      | `<->`        | `P(x) <-> Q(x)`                 |
| Equality       | =      | `=`          | `f(x) = y`                      |
| Not equal      | ≠      | `!=`         | `x != y`                        |

---

## Modal Logic

| Concept              | Symbol | ASCII        | Meaning                        | Example                     |
|----------------------|--------|--------------|--------------------------------|-----------------------------|
| Necessity            | □      | `box`        | Always true                    | `box P(x)`                  |
| Possibility          | ◇      | `diamond`    | Possibly true                  | `diamond P(x)`              |
| Necessity (relation) | □₍R₎   | `box_R`      | True for all related worlds    | `box_epsilon P(x)`          |
| Possibility (rel.)   | ◇₍R₎   | `diamond_R`  | True in some related world     | `diamond_epsilon P(x)`      |

---

## Sets & Relations

| Concept        | Symbol | ASCII        | Example                              |
|----------------|--------|--------------|--------------------------------------|
| Membership     | ∈      | `in`         | `x in hyperball(epsilon)`           |
| Subset         | ⊆      | `subset`     | `A subset B`                         |
| Relation       | R(x,y) | `R(x,y)`     | `R(x, x')`                           |
| Distance       | d(x,y) | `dist(x,y)`  | `dist(x, x') <= epsilon`            |

---

## FORML Canonical Patterns

| Description            | Logical Form (Symbolic)                          | ASCII Form |
|------------------------|--------------------------------------------------|------------|
| Robustness (FOL)       | ∀x,x' : d(x,x') ≤ ε → f(x) = f(x')               | `forall x,x': dist(x,x') <= epsilon -> f(x) = f(x')` |
| Robustness (Modal)     | □₍ε₎ (f(x) = f(x'))                              | `box_epsilon: f(x) = f(x')` |
| Membership constraint  | x ∈ S                                           | `x in S` |

---

## Recommended Internal DSL (ASCII Only)

Use this syntax internally in FORML:

```text
forall x, x':
    dist(x, x') <= epsilon ->
    f(x) = f(x')
```

## EXEMPLES
```forml
[ROBUSTNESS]:
forall in hyperball("L2", 0.01) -> CLASSIFICATION.EQUAL();
```

```text
∀x
    ∀x' :
        x' ∈ hyperball(x, "L2", 0.01) → f(x) = f(x')
```

---

```forml
[ROBUSTNESS]:
at x in hyperball("L2", 0.01) -> CLASSIFICATION.EQUAL();
```

```text
∀x' :
        x' ∈ hyperball(x, "L2", 0.01) → f(x) = f(x')
```
