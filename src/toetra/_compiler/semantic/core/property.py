from toetra._language.vocabulary.properties import EnumProperty
from toetra._compiler.semantic.context.points import PointEnvironment
from toetra._compiler.semantic.rules.backend import validate_backend_for_property
from toetra._compiler.semantic.rules.compatibility import (
    validate_property_point_contract,
)
from toetra._compiler.semantic.runtime.annotations import SemanticAnnotations

from toetra._compiler.semantic.errors.errors import (
    InvalidPropertyError,
    SemanticError,
)

from toetra._compiler.semantic.runtime.tracer import ValidationTracer

from toetra._compiler.semantic.core.lhs import LHSValidator
from toetra._compiler.semantic.core.binding import BindingValidator
from toetra._compiler.semantic.core.domain import DomainValidator
from toetra._compiler.semantic.core.logic import LogicValidator
from toetra._compiler.semantic.core.restrictions import RestrictionSemanticsBuilder
from toetra._compiler.semantic.core.specification_constants import (
    register_specification_constants,
)


class PropertyValidator:
    """
    PropertyValidator

    Responsibility:
    ----------------
    Validate a complete Toetra property.

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

    def validate(
        self,
        prop,
        model_schema=None,
        model_target=None,
        model_identity=None,
        specification_constants=(),
        global_points: PointEnvironment | None = None,
    ):

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

            context = LHSValidator(
                tracer=self.tracer,
                model_schema=model_schema,
            ).validate(
                scope,
                point_environment=(
                    global_points.fork_for_property()
                    if global_points is not None
                    else PointEnvironment()
                ),
            )

            context.model_target = model_target
            if not model_identity:
                raise SemanticError(
                    "Missing declared model identity in property semantic context"
                )
            context.model_identity = model_identity

            register_specification_constants(
                context,
                specification_constants,
            )

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

            root = BindingValidator(
                tracer=self.tracer,
                model_schema=model_schema,
            ).validate(context, root)
            assertion.root = root

            DomainValidator(model_schema=model_schema).validate(
                context.domain,
                context,
            )

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

            logic_validator = LogicValidator(
                tracer=self.tracer,
                model_schema=model_schema,
            )
            logic_validator.validate(root, context)

            if context.canonical_restriction is not None:
                logic_validator.validate(context.canonical_restriction, context)

            restriction_semantics = RestrictionSemanticsBuilder().build(
                context=context,
                assertion=root,
            )
            context.restriction_semantics = restriction_semantics

            prop.semantic.assertion_root = root
            prop.semantic.restriction_root = context.canonical_restriction
            if restriction_semantics is None:
                prop.semantic.logical_root = root
            else:
                prop.semantic.logical_root = restriction_semantics.language_formula
                prop.semantic.verification_root = (
                    restriction_semantics.verification_body
                )
                prop.semantic.verification_semantics = (
                    restriction_semantics.verification_semantics.value
                )

            # ==================================================
            # PROPERTY ↔ COMPOSED POINT CONTRACT
            # ==================================================

            property_type = self._normalize_property_type(prop.type)
            validate_property_point_contract(property_type, context)

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

        except SemanticError as e:

            raise InvalidPropertyError(
                message=f"Property '{prop.type}' invalid: {e.message}",
                node=prop,
                context="PropertyValidator",
                code=e.code,
                hint=e.hint,
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
