# Documentation snippets

> Status: Current contributor contract for `1.0.0rc3`
>
> Scope: selected public Python and Toetra examples

The executable-documentation contract makes a small, deliberate set of public
examples machine-checked. The objective is not to treat every fenced block as a program:
the repository also contains grammar fragments, output samples, pseudocode,
future syntax, and intentionally invalid examples.

## Ownership model

Each checked example has one canonical source under `docs/snippets/` and one
entry in [`manifest.toml`](../snippets/manifest.toml). The manifest records:

| Field | Meaning |
|---|---|
| `id` | stable diagnostic identity |
| `path` | canonical source relative to the repository root |
| `language` | rendered fence language |
| `check` | `python-compile` or `toetra-parse` |
| `include_in` | MkDocs pages that include the canonical bytes |
| `copy_in` | non-MkDocs documents that carry a checked copy |

Canonical sources are ordinary `.py` or `.toetra` files. They can be inspected,
parsed, formatted, and reviewed without extracting Markdown first.

## MkDocs pages

MkDocs pages include the canonical source inside a code fence:

````text
```toetra
<include the canonical docs/snippets/<name>.toetra source>
```
````

The snippets extension is configured with `check_paths: true`; a missing include
therefore also fails the strict site build. `check_snippets.py` additionally
requires every `include_in` declaration to appear exactly once in its owning
page.

## Checked copies

GitHub does not expand MkDocs snippet directives in `README.md`. Some public
contract checks also parse raw Markdown before MkDocs expansion. A checked copy
is therefore allowed at those boundaries when it is immediately preceded by
its stable marker:

````text
<!-- toetra-doc-snippet: <id> -->
```toetra
...
```
````

The checker compares the copied block with the canonical file after normalizing
only the outer blank lines and final newline. A change in indentation, tokens,
or statements is reported against both the snippet ID and owning document.

Do not add this marker to illustrative, partial, invalid, or prospective code.
Those blocks remain normal documentation and must state their support level in
the surrounding prose.

## Validation

Run the focused gate while editing examples:

```bash
make snippets-check
```

The durable documentation gate owns it:

```bash
make docs-check
```

`make ci` already includes `docs-check`, so drift cannot pass the normal CI
boundary. No release-phase-specific target is required.

The checker:

1. validates the manifest and canonical-source inventory;
2. compiles selected Python sources without executing user paths;
3. parses selected Toetra sources through the real CST-to-AST builder;
4. verifies every declared include and checked copy;
5. rejects orphan markers and unregistered canonical files.

Python snippets that require models or datasets are compiled rather than
executed. End-to-end runtime behavior remains owned by the demonstrations and
`make demo-check`.

## Adding or changing a snippet

1. Change the canonical file first.
2. Add or update its manifest entry.
3. Prefer a MkDocs include over copying.
4. When a raw-Markdown copy is necessary, preserve the marker and exact content.
5. Run `make snippets-check`, `make docs-check`, and the relevant demo.

A failure names the canonical source or owning page. Fix the source, manifest,
or document; do not weaken the checker to accept two competing examples.
