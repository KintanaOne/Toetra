# Parsing Diagnostics

## 1. Purpose

Define the diagnostic model used by the Parsing Layer.

---

## 2. Diagnostic Responsibilities

The Parsing Layer reports:

- syntax errors,
- malformed expressions,
- invalid delimiters,
- unsupported syntax patterns,
- ambiguity-related failures.

---

## 3. Constraints

Diagnostics must:

- remain syntax-oriented,
- avoid semantic assumptions,
- preserve determinism,
- remain reproducible.

---

## 4. Future Extensions

Potential future extensions include:

- source mapping,
- IDE integration,
- error recovery,
- incremental diagnostics.