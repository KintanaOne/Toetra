# Parser Invariants

| ID | Invariant | Description |
|---|---|---|
| PARSER-001 | Header completeness | Model and target are mandatory |
| PARSER-002 | Single scope per property | Properties cannot define multiple scopes |
| PARSER-003 | Assertions are mandatory | Empty assertions are forbidden |
| PARSER-004 | Parentheses integrity | Unbalanced parentheses must fail |
| PARSER-005 | Deterministic parsing | Same input always produces same parse tree |