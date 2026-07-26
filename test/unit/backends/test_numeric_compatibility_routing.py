from __future__ import annotations

from toetra._backends.capabilities import BackendCapabilities
from toetra._backends.defaults import create_default_backend_registry
from toetra._backends.execution import BackendExecutionCapabilities
from toetra._backends.registry import BackendRegistry
from toetra._backends.router import BackendRouter
from toetra._compatibility.defaults import (
    SKLEARN_AFFINE_TO_EXACT_REAL_RULE_ID,
    SKLEARN_BINARY_LOGISTIC_TO_EXACT_REAL_RULE_ID,
)
from toetra._compatibility.descriptors import (
    BackendProfileDescriptor,
    FrameworkModelDescriptor,
    ModelEncoderDescriptor,
    NumericSemanticDescriptor,
)
from toetra._compatibility.enums import (
    BackendKind,
    CompatibilityClassification,
    ConclusionKind,
    ConclusionScope,
    NumericFamily,
    SupportStatus,
)
from toetra._compatibility.model import (
    CompatibilityRule,
    CompatibilityRulePattern,
    NumericCompatibilityContext,
)
from toetra._compatibility.registry import NumericCompatibilityRegistry
from toetra._compiler.ir.ir1.nodes import (
    AttributeExpressionIR,
    ComparisonIR,
    ConstantExpressionIR,
    ScopeIR,
)
from toetra._compiler.ir.ir2.enums import NormalFormKind, VerificationSemantics
from toetra._compiler.ir.ir2.dsl.nodes import (
    NNFFormulaIR2,
    VerificationTaskIR2,
)
from toetra._compiler.ir.ir2.run_ir2 import run_ir2_with_model_schema
from toetra._compiler.ir.ir2.requirements import IR2Requirements
from toetra._language.vocabulary.backends import EnumBackend
from toetra._language.vocabulary.operators import EnumComparisonOperator
from toetra._language.vocabulary.properties import EnumProperty
from toetra._compiler.semantic.types.enums import EnumDataType
from toetra._models.compatibility import framework_model_descriptor
from toetra._models.encoder.profile import model_encoder_descriptor
from toetra._models.encoder.sklearn.logistic import SklearnLogisticRegressionEncoder
from test.fixtures.binary_classification import (
    binary_label_property,
    make_sklearn_logistic_schema,
)


def _task(backend: EnumBackend = EnumBackend.Z3) -> VerificationTaskIR2:
    atom = ComparisonIR(
        left=AttributeExpressionIR(entity="x0", feature="a"),
        op=EnumComparisonOperator.LTE,
        right=ConstantExpressionIR(value=1.0, dtype=EnumDataType.FLOAT),
    )
    requirements = IR2Requirements(
        requires_boolean_logic=True,
        requires_numeric_comparisons=True,
        requires_problem_predicates=False,
        requires_model_assertions=True,
        requires_domains=False,
        requires_neighborhoods=False,
        normal_form=NormalFormKind.NNF,
        required_verification_semantics=VerificationSemantics.REFUTATION,
        requires_affine_arithmetic=True,
        required_scalar_sorts=frozenset({EnumDataType.FLOAT}),
    )
    return VerificationTaskIR2(
        property_type=EnumProperty.LOGIC,
        scope=ScopeIR(
            kind="pointwise",
            variables={"x0": "point"},
            neighborhood=None,
            domain=None,
        ),
        backend=backend,
        assumptions=(),
        spec_formula=NNFFormulaIR2(expression=atom),
        verification_condition=NNFFormulaIR2(expression=atom),
        semantics=VerificationSemantics.REFUTATION,
        normal_form=NormalFormKind.NNF,
        requirements=requirements,
    )


def test_router_attaches_the_generic_numeric_compatibility_assessment() -> None:
    context = NumericCompatibilityContext(
        source_model=FrameworkModelDescriptor(
            framework_adapter_id="sklearn",
            framework_version="any",
            model_family="affine_regression",
            source_execution_profile_id="ieee754_binary64",
            numeric_semantics=NumericSemanticDescriptor.binary_float(64),
        ),
        model_encoder=ModelEncoderDescriptor(
            encoder_id="toetra.affine-equation",
            version="1",
            semantic_target="toetra.real_affine_extracted_model",
        ),
    )

    route = BackendRouter(create_default_backend_registry()).route(
        _task(), numeric_compatibility_context=context
    )

    assessment = route.numeric_compatibility
    assert assessment is not None
    assert assessment.matched_rule_id == SKLEARN_AFFINE_TO_EXACT_REAL_RULE_ID
    assert assessment.classification is CompatibilityClassification.LOSSY
    assert assessment.conclusion_scope is ConclusionScope.SEMANTIC_TARGET_ONLY
    assert "real_affine_extracted_model" in route.reason


def test_router_supports_a_non_sklearn_non_z3_compatibility_route() -> None:
    backend_profile = BackendProfileDescriptor(
        backend_kind=BackendKind.ABSTRACT_INTERPRETATION,
        adapter_id="relu-abstractor",
        profile_id="interval-relu-overapprox",
        numeric_semantics=NumericSemanticDescriptor(family=NumericFamily.INTERVAL),
    )
    backend_registry = BackendRegistry()
    backend_registry.register(
        BackendCapabilities(
            backend=EnumBackend.ERAN,
            supports_boolean_logic=True,
            supports_numeric_comparisons=True,
            supports_problem_predicates=False,
            supports_model_assertions=True,
            supports_domains=True,
            supports_neighborhoods=False,
            supported_normal_forms=(NormalFormKind.NNF,),
            supported_verification_semantics=(VerificationSemantics.REFUTATION,),
            supports_affine_arithmetic=True,
            supported_scalar_sorts=frozenset({EnumDataType.FLOAT}),
            numeric_profile=backend_profile,
            execution_capabilities=BackendExecutionCapabilities(supports_timeout=True),
        )
    )

    compatibility_registry = NumericCompatibilityRegistry()
    compatibility_registry.register(
        CompatibilityRule(
            rule_id="pytorch-relu-interval-overapprox",
            pattern=CompatibilityRulePattern(
                framework_adapter_id="pytorch",
                model_family="relu_network",
                model_encoder_id="toetra.relu-network",
                backend_kind=BackendKind.ABSTRACT_INTERPRETATION.value,
                backend_adapter_id="relu-abstractor",
                backend_profile_id="interval-relu-overapprox",
            ),
            support_status=SupportStatus.EXPERIMENTAL,
            classification=CompatibilityClassification.SOUND_OVER_APPROXIMATION,
            semantic_target="pytorch.relu.source-semantics",
            evidence_id="test-evidence",
            permitted_conclusions=frozenset({ConclusionKind.UNIVERSAL_PROOF}),
            conclusion_scope=ConclusionScope.SOURCE_ARTIFACT,
        )
    )
    context = NumericCompatibilityContext(
        source_model=FrameworkModelDescriptor(
            framework_adapter_id="pytorch",
            framework_version="2.x",
            model_family="relu_network",
            source_execution_profile_id="ieee754_binary32",
            numeric_semantics=NumericSemanticDescriptor.binary_float(32),
        ),
        model_encoder=ModelEncoderDescriptor(
            encoder_id="toetra.relu-network",
            version="1",
            semantic_target="pytorch.relu.source-semantics",
        ),
    )

    route = BackendRouter(
        backend_registry,
        numeric_compatibility_registry=compatibility_registry,
    ).route(_task(EnumBackend.ERAN), numeric_compatibility_context=context)

    assert route.backend is EnumBackend.ERAN
    assert route.numeric_compatibility is not None
    assert (
        route.numeric_compatibility.classification
        is CompatibilityClassification.SOUND_OVER_APPROXIMATION
    )
    assert (
        route.numeric_compatibility.conclusion_scope is ConclusionScope.SOURCE_ARTIFACT
    )


def test_router_attaches_binary_logistic_label_compatibility_assessment() -> None:
    schema = make_sklearn_logistic_schema(coefficient=2.0, intercept=-1.0)
    task = run_ir2_with_model_schema(
        binary_label_property(),
        schema=schema,
    )[0]
    context = NumericCompatibilityContext(
        source_model=framework_model_descriptor(schema),
        model_encoder=model_encoder_descriptor(SklearnLogisticRegressionEncoder()),
    )
    route = BackendRouter(create_default_backend_registry()).route(
        task,
        numeric_compatibility_context=context,
    )
    assessment = route.numeric_compatibility
    assert assessment is not None
    assert assessment.matched_rule_id == SKLEARN_BINARY_LOGISTIC_TO_EXACT_REAL_RULE_ID
    assert assessment.classification is CompatibilityClassification.LOSSY
    assert assessment.semantic_target == "toetra.oriented-decision-value"
    assert assessment.conclusion_scope is ConclusionScope.SEMANTIC_TARGET_ONLY
