# Property Types in FORML

This document describes all **official property types** supported by FORML.

Each property type defines **what kind of model behavior is constrained**, independently of **where** it is evaluated (global, local, pairwise, etc.).

---

## ROBUSTNESS

### Intent
Ensure that small perturbations of the input do not change the model’s prediction.

### Typical Use Cases
- Adversarial robustness  
- Noise tolerance  
- Certification under norm-bounded perturbations  

### Semantic Invariant
> Inputs that are *close enough* must produce equivalent outputs.

---

## STABILITY

### Intent
Ensure smoothness or continuity of the model’s behavior.

### Typical Use Cases
- Preventing erratic predictions  
- Sensitivity control  
- Model regularity guarantees  

### Semantic Invariant
> Small changes in input should result in small (or no) changes in output.

---

## FAIRNESS

### Intent
Ensure non-discriminatory behavior across individuals or groups.

### Typical Use Cases
- Group fairness  
- Individual fairness  
- Regulatory compliance  

### Semantic Invariant
> Comparable individuals or groups must be treated equivalently under defined criteria.

---

## MONOTONICITY

### Intent
Enforce monotonic relationships between inputs and outputs.

### Typical Use Cases
- Credit scoring  
- Risk assessment  
- Interpretable ML systems  

### Semantic Invariant
> Increasing (or decreasing) a given feature must not violate a predefined order on the output.

---

## BOUND

### Intent
Constrain model outputs within numerical limits.

### Typical Use Cases
- Safety constraints  
- Output normalization  
- Regulatory bounds  

### Semantic Invariant
> Model outputs must remain within specified bounds under all considered conditions.

---

## LOGIC

### Intent
Express logical relationships between predictions or conditions.

### Typical Use Cases
- Business rules  
- Domain constraints  
- Symbolic reasoning over predictions  

### Semantic Invariant
> Predictions must satisfy logical formulas or implications.

---

## Property Types Summary

| Property Type   | Core Question Answered                     | Typical Constraints                         |
|-----------------|--------------------------------------------|---------------------------------------------|
| ROBUSTNESS      | Does the model resist perturbations?        | Equality under perturbation                 |
| STABILITY       | Is the model smooth?                        | Output similarity                           |
| FAIRNESS        | Is the model equitable?                    | Equality across individuals or groups       |
| MONOTONICITY    | Does the model respect order?               | Non-decreasing / non-increasing             |
| BOUND           | Are outputs safe?                           | Numerical intervals                         |
| LOGIC           | Does the model obey rules?                  | Logical formulas                            |

---

## Important Design Note

Property Types define **semantic intent**, not execution strategy.

They do **not** prescribe:
- how verification is performed  
- which solver or backend is used  
- whether evaluation is global, local, or pairwise  

These aspects are handled separately by **scopes** and **backends**.

---

## Why This Ordering Matters

By defining property types **before** introducing scopes:

- Readers acquire a **stable mental model**
- The language appears **closed and intentional**
- The DSL feels **designed**, not emergent  

This is how mature languages present their semantic foundations.
