"""Frozen migration diagnostics for pre-P15 scope syntax.

The parser intentionally keeps a small legacy surface so users receive an
 actionable migration error instead of an opaque parse failure.  These forms
must never acquire the new point-aware semantics silently.
"""

LEGACY_CHECK_AT_CODE = "MIGRATION_CHECK_AT_UNDECLARED_ANCHOR"
LEGACY_AT_CODE = "MIGRATION_LEGACY_AT"
LEGACY_PAIRWISE_CODE = "MIGRATION_LEGACY_PAIRWISE"

LEGACY_CHECK_AT_MESSAGE = (
    "Legacy 'check_at {name}' without a declared anchor is no longer supported. "
    "Declare 'anchor {name} := {{ ... }}' or "
    "'anchor {name} := ref(key = ..., value = ...)' before using "
    "'check_at {name}'."
)

LEGACY_AT_MESSAGE = (
    "Legacy 'at {name} in neighborhood(...)' is no longer supported. "
    "Declare a concrete anchor and use "
    "'at {name} with candidate in neighborhood(metric = Linf, eps = ...)' "
    "or the explicit 'forall candidate where candidate in "
    "neighborhood(of = {name}, metric = Linf, eps = ...)' form."
)

LEGACY_PAIRWISE_MESSAGE = (
    'Legacy pairwise syntax "{pair}" is no longer supported. '
    "Use explicit point binders, for example 'forall x0, x1', and express "
    "their relation in a 'where' clause."
)
