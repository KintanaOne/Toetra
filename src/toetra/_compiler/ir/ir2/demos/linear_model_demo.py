from __future__ import annotations

from toetra._compiler.ir.ir2.context import IR2BuildContext
from toetra._compiler.ir.ir2.enums import NormalFormKind
from toetra._compiler.ir.ir2.explain import IR2ExplainOptions, explain_ir2_tasks
from toetra._compiler.ir.ir2.examples.samples import REAL_LINEAR_MODEL_SAMPLE
from toetra._compiler.ir.ir2.dsl.nodes import VerificationTaskIR2
from toetra._compiler.ir.ir2.pretty import pretty_print_ir2_tasks
from toetra._compiler.ir.ir2.run_ir2 import run_ir2_with_model_schema
from toetra._compiler.semantic.types.enums import EnumDataType
from toetra._models.detector.detector import ModelDetector
from toetra._models.introspector.introspector_factory import IntrospectorFactory
from toetra._models.schema.feature_schema import FeatureSchema
from toetra._models.schema.model_schema import ModelSchema


def build_demo_linear_regression_schema() -> ModelSchema:
    """Train and introspect a real sklearn LinearRegression model.

    This helper intentionally goes through the model subsystem instead of
    hand-writing ``ModelSchema.metadata['linear']``. The only external schema
    supplied here is feature/target typing, because the demo has no CSV file to
    infer dtypes from.
    """

    import pandas as pd
    from sklearn.linear_model import LinearRegression

    x = pd.DataFrame(
        {
            "a": [0.0, 1.0, 2.0, 3.0, 4.0],
            "b": [1.0, 0.0, 1.0, 0.0, 2.0],
        }
    )
    y = 2.0 * x["a"] - 1.0 * x["b"] + 0.5

    model = LinearRegression()
    model.fit(x, y)

    framework = ModelDetector().detect(model)
    input_schema = ModelSchema(
        framework=framework,
        model_type=type(model).__name__,
        features={
            "a": FeatureSchema(name="a", dtype=EnumDataType.FLOAT),
            "b": FeatureSchema(name="b", dtype=EnumDataType.FLOAT),
        },
        target="MyTarget",
        task="regression",
    )

    introspector = IntrospectorFactory.create(
        framework,
        model,
        dataset_path=None,
        schema=input_schema,
        serialization_format="in-memory-demo",
        target_name="MyTarget",
    )

    return introspector.introspect()


def run_ir2_with_demo_linear_regression_model() -> list[VerificationTaskIR2]:
    """Compile the visual demo using a real trained LinearRegression model."""

    schema = build_demo_linear_regression_schema()

    return run_ir2_with_model_schema(
        REAL_LINEAR_MODEL_SAMPLE,
        schema=schema,
        ir2_context=IR2BuildContext(
            preferred_normal_form=NormalFormKind.NNF,
            allow_nnf_fallback=True,
        ),
    )


def print_demo_linear_regression_ir2() -> None:
    """Print a visual end-to-end IR2 demo with real model assumptions."""

    schema = build_demo_linear_regression_schema()
    linear_metadata = schema.metadata_by_name.get("linear", {})

    tasks = run_ir2_with_model_schema(
        REAL_LINEAR_MODEL_SAMPLE,
        schema=schema,
        ir2_context=IR2BuildContext(
            preferred_normal_form=NormalFormKind.NNF,
            allow_nnf_fallback=True,
        ),
    )

    print("\n=== IR2 REAL MODEL DEMO ===\n")
    print("Trained model    : sklearn.LinearRegression")
    print(f"Target           : {schema.target}")
    print(f"Features         : {', '.join(schema.feature_names)}")
    print(f"Linear coef      : {linear_metadata.get('coef')}")
    print(f"Linear intercept : {linear_metadata.get('intercept')}")

    print("\n=== IR2 PRETTY WITH MODEL Γ ===\n")
    pretty_print_ir2_tasks(tasks)

    print("\n=== IR2 EXPLAIN WITH MODEL Γ ===\n")
    print(
        explain_ir2_tasks(
            tasks,
            options=IR2ExplainOptions(
                include_assumption_formulas=True,
                include_requirements=True,
                include_mermaid=True,
            ),
        )
    )


def main() -> None:
    print_demo_linear_regression_ir2()


if __name__ == "__main__":
    main()
