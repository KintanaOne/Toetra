# FORML Parsing Coverage Matrix

## 1. Program Structure

| Case | Description                        | Expected |
| ---- | ---------------------------------- | -------- |
| P1   | Minimal valid program (1 property) | ✅        |
| P2   | Missing model                      | ❌        |
| P3   | Missing target                     | ❌        |
| P4   | Multiple properties                | ✅        |
| P5   | Empty body                         | ❌        |
| P6   | Only header (no property)          | ❌        |
| P7   | Header with comments/padding       | ✅        |

---

## 2. Property Expressions (Scope)

## Critical rule

```ebnf
property_expr = quantifier_expr | at_expr | check_expr | pairwise_expr ;
```
so :
| Case | Description                          | Expected |
| ---- | ------------------------------------ | -------- |
| PE1  | Single valid property_expr           | ✅        |
| PE2  | Multiple property_expr (invalid mix) | ❌        |
| PE3  | Missing property_expr                | ❌        |


### 2.1 check_at

| Case | Input | Expected |
|------|------|----------|
| C1 | `check_at x -> ...` | ✅ |
| C2 | missing identifier | ❌ |
| C3 | invalid identifier | ❌ |

---

### 2.2 at

| Case | Input               | Expected |
| ---- | ------------------- | -------- |
| C1   | `check_at x -> ...` | ✅        |
| C2   | missing identifier  | ❌        |
| C3   | invalid identifier  | ❌        |


---

### 2.3 pairwise

| Case | Input                         | Expected |
| ---- | ----------------------------- | -------- |
| PW1  | `x ~ x' in neighborhood(...)` | ✅        |
| PW2  | missing `'`                   | ❌        |
| PW3  | missing `in`                  | ❌        |
| PW4  | invalid pair structure        | ❌        |


---

### 2.4 forall

| Case | Input                         | Expected |
| ---- | ----------------------------- | -------- |
| PW1  | `x ~ x' in neighborhood(...)` | ✅        |
| PW2  | missing `'`                   | ❌        |
| PW3  | missing `in`                  | ❌        |
| PW4  | invalid pair structure        | ❌        |


---

## 3. Assertions

### 3.1 Atomic

| Case | Input            | Expected |
| ---- | ---------------- | -------- |
| AT1  | `x.feature <= 0` | ✅        |
| AT2  | `x <= 0`         | ✅        |
| AT3  | `x.feature == 1` | ✅        |
| AT4  | missing operator | ❌        |
| AT5  | missing value    | ❌        |


---

### 3.2 Logical operators

| Case | Input           | Expected |
| ---- | --------------- | -------- |
| L1   | `A AND B`       | ✅        |
| L2   | `A OR B`        | ✅        |
| L3   | `NOT A`         | ✅        |
| L4   | `NOT (A AND B)` | ✅        |
| L5   | `A AND`         | ❌        |
| L6   | `AND A`         | ❌        |


---

### 3.3 Logical precedence

| Case | Input                             | Expected |
| ---- | --------------------------------- | -------- |
| LP1  | `A OR B AND C` → `A OR (B AND C)` | ✅        |
| LP2  | `NOT A AND B` → `(NOT A) AND B`   | ✅        |
| LP3  | `(A OR B) AND C`                  | ✅        |


### 3.4 Implication

| Case | Input          | Expected |
| ---- | -------------- | -------- |
| I1   | `A -> B`       | ✅        |
| I2   | `A AND B -> C` | ✅        |
| I3   | `A -> B -> C`  | ✅        |
| I4   | `-> B`         | ❌        |
| I5   | `A ->`         | ❌        |


---

### 3.5 Parentheses

| Case | Input                | Expected |
| ---- | -------------------- | -------- |
| P1   | `(A AND B)`          | ✅        |
| P2   | `(A AND)`            | ❌        |
| P3   | nested parentheses   | ✅        |
| P4   | unclosed parentheses | ❌        |


---

## 4. Attributes

| Case  | Input       | Expected |
| ----- | ----------- | -------- |
| ATTR1 | `x.feature` | ✅        |
| ATTR2 | `x.a.b.c`   | ✅        |
| ATTR3 | `x`         | ✅        |
| ATTR4 | `.feature`  | ❌        |
| ATTR5 | `x.`        | ❌        |


---

## 5. Neighborhood

| Case | Input                       | Expected |
| ---- | --------------------------- | -------- |
| N1   | `neighborhood(L2)`          | ✅        |
| N2   | `neighborhood(L2, eps=0.1)` | ✅        |
| N3   | multiple args               | ✅        |
| N4   | missing metric              | ❌        |
| N5   | malformed args              | ❌        |


---

## 6. Problem Expressions

| Case | Input                    | Expected |
| ---- | ------------------------ | -------- |
| PR1  | `CLASSIFICATION.EQUAL()` | ✅        |
| PR2  | `REGRESSION.ERROR()`     | ✅        |
| PR3  | missing function         | ❌        |
| PR4  | missing parentheses      | ❌        |
| PR5  | unknown problem          | ❌        |


---

## 7. Full Properties

| Case | Description                   | Expected |
| ---- | ----------------------------- | -------- |
| FP1  | pairwise + assertion          | ✅        |
| FP2  | check_at + logic              | ✅        |
| FP3  | forall + implication          | ✅        |
| FP4  | at + neighborhood + logic     | ✅        |
| FP5  | property + using (abstractor) | ✅        |
| FP6  | invalid mix of property_expr  | ❌        |
