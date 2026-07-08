from dsl.language.vocabulary.properties import EnumProperty
from dsl.semantic.rules.backend import validate_backend_for_property
from dsl.semantic.rules.compatibility import PROPERTY_SCOPE_COMPATIBILITY
from dsl.semantic.runtime.annotations import SemanticAnnotations

from dsl.semantic.errors.errors import (
    InvalidPropertyError,
    SemanticError,
)

from dsl.semantic.runtime.tracer import ValidationTracer

from dsl.semantic.core.lhs import LHSValidator
from dsl.semantic.core.binding import BindingValidator
from dsl.semantic.core.logic import LogicValidator


class PropertyValidator:
    """
    PropertyValidator

    Responsibility:
    ----------------
    Validate a complete FORML property.

    Validation pipeline:
    --------------------
    1. LHS validation
        → builds SemanticContext

    2. Binding validation
        → resolves symbols / entities

    3. Logic validation
        → validates semantic correctness

    Runtime semantic artifacts:
    ---------------------------
    The validator progressively enriches the property with
    semantic metadata stored in:

        prop.semantic : SemanticAnnotations

    This semantic layer is later reused by:
    - IR lowering
    - backend compilation
    - optimization passes
    - symbolic reasoning
    - dependency analysis
    """

    def __init__(self, tracer=None):
        self.tracer = tracer or ValidationTracer()

    # ─────────────────────────────────────────────
    # ENTRY POINT
    # ─────────────────────────────────────────────

    def validate(self, prop, model_schema=None):

        self.tracer.log(f"Validating Property: {prop.type}")

        # --------------------------------------------------
        # Structural sanity checks
        # --------------------------------------------------

        if not hasattr(prop, "rule") or prop.rule is None:

            raise InvalidPropertyError(
                message="Missing rule", node=prop, context="PropertyValidator"
            )

        rule = prop.rule

        scope = rule.scope
        assertion = rule.assertion
        root = assertion.root

        # --------------------------------------------------
        # Create semantic annotation container
        # --------------------------------------------------

        prop.semantic = SemanticAnnotations()

        try:

            # ==================================================
            # 1. LHS VALIDATION
            # ==================================================
            #
            # Produces the semantic execution context:
            #
            # - variables
            # - symbol table
            # - neighborhoods
            # - domains
            # - quantifiers
            #
            # This context becomes the semantic root
            # for all later compilation stages.
            #
            # ==================================================

            context = LHSValidator(tracer=self.tracer).validate(scope)

            prop.semantic.context = context

            # --------------------------------------------------
            # Cache symbol table
            # --------------------------------------------------

            prop.semantic.symbol_table = context.symbol_table

            # ==================================================
            # 2. BINDING VALIDATION
            # ==================================================
            #
            # Resolves:
            #
            # - explicit variables
            # - implicit entities
            # - aliases
            # - symbol references
            #
            # Mutates AST nodes with:
            #
            # - resolved_entity
            # - resolved_symbol
            #
            # ==================================================

            BindingValidator(tracer=self.tracer).validate(context, root)

            # ==================================================
            # 3. LOGIC VALIDATION
            # ==================================================
            #
            # Verifies semantic correctness of:
            #
            # - logical operators
            # - comparisons
            # - problem constraints
            # - type compatibility
            #
            # ==================================================

            LogicValidator(
                tracer=self.tracer,
                model_schema=model_schema,
            ).validate(root, context)

            # ==================================================
            # PROPERTY ↔ SCOPE COMPATIBILITY
            # ==================================================

            property_type = self._normalize_property_type(prop.type)

            allowed_scopes = PROPERTY_SCOPE_COMPATIBILITY.get(property_type)

            if allowed_scopes is None:
                raise InvalidPropertyError(
                    f"No scope compatibility rule defined for property '{property_type.value}'"
                )

            if context.type not in allowed_scopes:

                allowed = ", ".join(s.value for s in allowed_scopes)

                raise InvalidPropertyError(
                    f"Property '{prop.type}' does not support "
                    f"scope '{context.type.value}'. "
                    f"Allowed scopes: {allowed}"
                )

            validate_backend_for_property(
                property_type=property_type,
                backend=prop.backend.name if prop.backend else None,
            )

            # ==================================================
            # 4. CACHE SEMANTIC ROOT
            # ==================================================
            #
            # Future semantic passes will reuse this
            # normalized logical tree.
            #
            # Examples:
            #
            # - IR lowering
            # - graph analysis
            # - SMT lowering
            # - optimization
            #
            # ==================================================

            prop.semantic.logical_root = root

        except SemanticError as e:

            raise InvalidPropertyError(
                message=f"Property '{prop.type}' invalid: {e}",
                node=prop,
                context="PropertyValidator",
            ) from e

        self.tracer.log(f"✔ Property '{prop.type}' validated")

        return True

    def _normalize_property_type(self, property_type) -> EnumProperty:
        if isinstance(property_type, EnumProperty):
            return property_type

        try:
            return EnumProperty.from_str(str(property_type))
        except ValueError as e:
            raise InvalidPropertyError(
                f"Unknown property type '{property_type}'"
            ) from e
