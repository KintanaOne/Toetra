# FORML

**FORML** is a declarative, human-readable DSL for expressing **formal behavioral properties**
of machine learning models (robustness, fairness, stability, monotonicity, logic…).

It bridges the gap between **high-level requirements** and **formal verification tools**
such as **ERAN** or **Z3**.

---

## Why FORML?

Machine learning models are rarely tested beyond accuracy.

Yet, in practice, we often need answers to questions like:
- Is my model robust to noise or perturbations?
- Does it treat sensitive attributes fairly?
- Are its outputs bounded and logically consistent?

FORML allows these requirements to be expressed **explicitly**, **formally**, and **independently**
of the verification backend.

---

## Minimal Example

```forml
ROBUSTNESS:
at x0 in hyperball(L2, 0.01) := CLASSIFICATION.EQUAL()
```
The model must predict the same class for all small perturbations around x0.

## Key Ideas

- FORML is declarative: you specify what must hold, not how to verify it

- Properties are backend-agnostic

- The language separates:
    - semantic intent (robustness, fairness, logic…)
    - scope (global, local, pairwise)
    - execution (ERAN, Z3, custom tools)

## Documentation

Full documentation is available in the docs/ directory:

- [scopes.md](docs/scope.md) — global, local and pairwise scopes

- [syntax.md — language syntax](docs/syntax.md)
  
- [semantic.md](docs/semantics.md)
  
- [properties.md](docs/properties.md) — semantic definition of property types

- backends.md — supported verification tools

## Project Status

FORML is an early-stage research and engineering project.
The core DSL, parser, and AST are functional.
Backend integrations are experimental and evolving.

## Contributing

- ✨ Contributions, suggestions, or improvements are welcome!
- Open issues to report bugs or suggest features
- Submit pull requests to improve the parser, DSL, or examples
- Star the repository if you find the idea promising

Let’s bring formal verification closer to real-world ML together 💡

# 🔐 License
Project licensed under MIT. See [LICENSE.md](LICENSE) for details.

# 👤 Author
Developed by KintanaOne
(Alias of a data scientist & formal methods enthusiast who believes that ML should be tested as rigorously as software.)