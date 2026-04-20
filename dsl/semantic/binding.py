from dsl.semantic.errors import UnboundVariableError
from dsl.semantic.tracer import ValidationTracer


class BindingValidator:
    """
    BindingValidator is responsible for resolving variable references in the RHS.

    It ensures that:
    - all variables used in expressions are declared in the LHS context
    - implicit feature access (e.g., `a <= 1`) is resolved to a valid entity
    - user-defined variable names can be mapped to internal symbolic variables

    This phase is equivalent to:
        🔥 name resolution / symbol binding in a compiler

    It may also rewrite the AST in-place:
        - inject missing entities
        - normalize variable names
    """

    def __init__(self, tracer=None):
        self.tracer = tracer or ValidationTracer()

    # ─────────────────────────────
    # ENTRY POINT
    # ─────────────────────────────

    def validate(self, context, rhs):
        """
        Validates and resolves all variable bindings in the RHS.

        Parameters:
            context: dict produced by LHSValidator
            rhs: AST node (logical expression or problem node)
        """

        self.tracer.log(f"Binding validation with context: {context}")

        self._check_node(rhs, context)

    # ─────────────────────────────
    # CORE RECURSIVE WALK
    # ─────────────────────────────

    def _check_node(self, node, context):
        """
        Recursively traverses the AST and resolves:
        - explicit variable references
        - implicit feature accesses
        """

        variables = context["variables"]
        default_entity = context.get("default_entity")

        # ─────────────────────────────
        # CASE 1 — AttributeNode (feature access)
        # ─────────────────────────────

        if hasattr(node, "feature"):

            # --------------------------------
            # 1A — Explicit entity (x.a)
            # --------------------------------
            if getattr(node, "entity", None):

                if node.entity not in variables:

                    # 🔥 Alias resolution (quantifier case)
                    if len(variables) == 1:
                        target_var = next(iter(variables.keys()))

                        self.tracer.log(
                            f"Alias binding: {node.entity} → {target_var}"
                        )

                        # Alias resolution
                        node.entity = target_var

                        # 🔥 keep path consistent
                        if hasattr(node, "path") and node.path:
                            node.path[0] = target_var

                    else:
                        raise UnboundVariableError(
                            f"Variable '{node.entity}' not allowed. "
                            f"Expected one of {list(variables.keys())}"
                        )

            # --------------------------------
            # 1B — Implicit entity (a <= 1)
            # --------------------------------
            else:
                if default_entity:
                    node.entity = default_entity

                    self.tracer.log(
                        f"Implicit binding: {node.feature} → "
                        f"{default_entity}.{node.feature}"
                    )

                elif len(variables) == 1:
                    var = next(iter(variables.keys()))
                    node.entity = var

                    self.tracer.log(
                        f"Implicit binding: {node.feature} → "
                        f"{var}.{node.feature}"
                    )

                else:
                    raise UnboundVariableError(
                        f"Ambiguous feature '{node.feature}' "
                        f"with variables {list(variables.keys())}"
                    )

        # ─────────────────────────────
        # RECURSIVE DESCENT
        # ─────────────────────────────

        for child in self._children(node):
            self._check_node(child, context)

    # ─────────────────────────────
    # CHILD EXTRACTION
    # ─────────────────────────────

    def _children(self, node):
        """
        Extracts child nodes from an AST node.

        Supports:
        - nested objects
        - lists of nodes
        - ignores primitives (int, str, etc.)
        """

        if not hasattr(node, "__dict__"):
            return []

        children = []

        for value in node.__dict__.values():

            if isinstance(value, list):
                children.extend(
                    v for v in value if hasattr(v, "__dict__")
                )

            elif hasattr(value, "__dict__"):
                children.append(value)

        return children