from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

from toetra._compiler.ir.ir1.nodes import ModelEvaluationIR, PointBindingIR
from toetra._compiler.ir.ir2.model.affine import AffineModelQuantityConstraintIR2
from toetra._models.encoder.factory import ModelEncoderFactory
from toetra._models.introspector.sklearn_introspector import SklearnIntrospector


def test_encoded_affine_quantity_matches_sklearn_decision_function(tmp_path) -> None:
    rng = np.random.default_rng(7)
    training = rng.normal(size=(80, 3))
    labels = (1.3 * training[:, 0] - 0.7 * training[:, 1] + 0.2 > 0).astype(int)
    frame = pd.DataFrame(training, columns=pd.Index(["a", "b", "c"]))
    frame["decision"] = labels

    model = LogisticRegression(random_state=0, max_iter=1000).fit(
        frame[["a", "b", "c"]], frame["decision"]
    )
    dataset = tmp_path / "training.csv"
    frame.to_csv(dataset, index=False)
    schema = SklearnIntrospector(
        model=model,
        source_path=dataset,
        target_name="decision",
    ).introspect()
    evaluation = ModelEvaluationIR(
        model_identity="binary.joblib",
        point=PointBindingIR(name="x", binding_kind="anchor"),
        output_name="decision",
    )
    atom = ModelEncoderFactory().encode(schema, (evaluation,))[0].formula.expression
    assert isinstance(atom, AffineModelQuantityConstraintIR2)

    samples = rng.normal(size=(50, 3))
    encoded = np.array(
        [
            sum(
                term.coefficient * row[index]
                for index, term in enumerate(atom.expression.terms)
            )
            + atom.expression.bias
            for row in samples
        ]
    )
    concrete = model.decision_function(
        pd.DataFrame(samples, columns=pd.Index(["a", "b", "c"]))
    )

    np.testing.assert_allclose(encoded, concrete, rtol=0.0, atol=1e-12)
