# AST Invariants

| ID | Invariant | Description |
|---|---|---|
| AST-001 | Assertion root non-null | Assertions must always contain a root node |
| AST-002 | Implication is binary | ImplicationNode requires left/right |
| AST-003 | NOT is unary | NotNode wraps exactly one operand |
| AST-004 | Pairwise contains two identifiers | PairwiseExprNode requires x and x' |