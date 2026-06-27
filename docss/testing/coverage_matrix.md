# FORML Invariant Coverage Matrix

| Invariant | Description | Unit | Hypothesis | Mutation | Fuzzing | Status |
|---|---|---|---|---|---|---|
| Header requires model | Program must define model | ✅ | ✅ | ❌ | ❌ | Stable |
| Header requires target | Program must define target | ✅ | ✅ | ❌ | ❌ | Stable |
| Assertion root is never null | AST assertions must always exist | ✅ | ✅ | ❌ | ❌ | Stable |
| Pairwise scope requires x and x' | Pairwise expressions need two identifiers | ✅ | ✅ | ✅ | ❌ | Stable |
| Logic precedence is deterministic | AND/OR/NOT precedence must be preserved | ✅ | ✅ | Planned | ❌ | Stable |
| Invalid parentheses are rejected | Parser must fail explicitly | ✅ | ✅ | Planned | ❌ | Stable |
| Quantifier must be valid | Quantifier ∈ {forall, exists} | ✅ | ✅ | ❌ | ❌ | Stable |
| Backend attachment is optional | Property may omit backend | ✅ | ✅ | ❌ | ❌ | Stable |
| Domain values must be non-empty | Domains cannot be malformed | ✅ | Planned | Planned | ❌ | Partial |
| Parser is deterministic | Same input → same AST | ❌ | ✅ | ❌ | ❌ | Stable |
| Roundtrip preserves AST | serialize(parse(x)) ≡ x | ❌ | ✅ | ❌ | ❌ | Stable |