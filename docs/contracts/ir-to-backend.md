# IR to Backend Contract

> Status: P0 / Planned / Critical  
> Scope: LoweredQuery to BackendQuery  
> Implementation: Not yet implemented  
> Audience: backend authors, solver integration authors, architecture maintainers

## Purpose

The IR to Backend contract defines the backend boundary.

It answers the question:

```text
What exactly is sent to a verification backend?
```

This is the first layer where backend-specific artifacts may be produced.

---

## Input

```text
LoweredQuery
+
BackendSelection
+
ModelEncodingStrategy
```

The backend compiler may also receive:

- backend capability metadata;
- diagnostic context;
- execution configuration;
- model encoding constraints;
- traceability metadata.

---

## Output

```text
BackendQuery
```

A `BackendQuery` is backend-specific.

Examples:

| Backend | Possible BackendQuery |
|---|---|
| Z3 | Z3 expressions, solver declarations, assertions. |
| ERAN | ERAN-compatible robustness query/configuration. |
| future backend | backend-specific verification artifact. |

---

## Boundary Rule

Before this boundary:

```text
FORML artifacts are backend-independent or backend-preparable.
```

After this boundary:

```text
Artifacts may be backend-specific.
```

No solver-specific object should leak into earlier layers.

---

## Guarantees

If backend compilation succeeds:

- the selected backend supports the requested query;
- all required model encodings exist;
- unsupported features were rejected or rewritten earlier;
- the backend query is executable by the target backend;
- traceability to FORML assertions is preserved.

---

## Non-Goals

The IR to Backend contract does not:

- define the full solver API;
- execute verification;
- perform runtime monitoring;
- choose the backend alone;
- repair semantically invalid properties.

---

## Failure Modes

Expected failures include:

- unsupported backend;
- unsupported operator/function;
- missing model encoding;
- unsupported normal form;
- incompatible property/backend pair;
- backend capability mismatch;
- invalid lowered query.

---

## Backend Diagnostics

Failures at this boundary should produce actionable diagnostics.

Diagnostics should explain:

- which backend was selected;
- which constraint failed;
- which FORML property originated it;
- whether another backend may support it;
- whether rewriting/minimization could help.

---

## Miova Hooks

Miova may mutate:

- backend selection metadata;
- lowered query structure;
- model encoding constraints;
- backend capability declarations;
- backend query output.

Expected outcome:

```text
Invalid backend artifact → backend-boundary rejection
Valid backend artifact   → runtime execution may continue
```
