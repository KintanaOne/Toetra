from __future__ import annotations

from decimal import Decimal

import numpy as np
from sklearn.linear_model import LogisticRegression

from dsl.ir.ir1.run_ir1 import run_ir
from model.semantics.lowering import ModelSemanticLowerer
from test.fixtures.model_semantic_lowering import make_binary_logistic_schema


def _fitted_unit_logistic() -> LogisticRegression:
    model = LogisticRegression()
    model.classes_ = np.asarray(["rejected", "approved"])
    model.coef_ = np.asarray([[1.0]])
    model.intercept_ = np.asarray([0.0])
    model.n_features_in_ = 1
    return model


def test_directed_probability_lowering_agrees_with_predict_proba_away_from_bound() -> (
    None
):
    schema = make_binary_logistic_schema()
    task = run_ir(
        """
        model := "credit.joblib"
        target := decision
        [LOGIC]:
        forall applicant =>
            target[applicant].probability("approved") >= 0.8
        """,
        model_schema=schema,
    )[0]
    evidence = ModelSemanticLowerer().lower_task(task, schema=schema).evidence[0]
    selected = Decimal(evidence.canonical_constraint.threshold)
    model = _fitted_unit_logistic()

    for decision_value in (float(selected) + 0.5, float(selected) + 2.0):
        probability = float(model.predict_proba([[decision_value]])[0, 1])
        assert Decimal(str(decision_value)) >= selected
        assert probability >= 0.8

    for decision_value in (float(selected) - 0.5, float(selected) - 2.0):
        probability = float(model.predict_proba([[decision_value]])[0, 1])
        assert Decimal(str(decision_value)) < selected
        assert probability < 0.8
