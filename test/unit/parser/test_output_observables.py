from __future__ import annotations

import pytest
from lark import Tree
from lark.exceptions import UnexpectedInput

from dsl.parser.parser import parse_toetra_code
from test.unit.parser._point_binding_helpers import program, single_tree, token_text


def _single_observable(source: str) -> Tree:
    tree = parse_toetra_code(program(body=source))
    return single_tree(tree, "output_observable")


def test_par_obs_001_parses_indexed_predicted_label() -> None:
    observable = _single_observable('forall x0 => target[x0].label == "approved"')

    output = single_tree(observable, "model_output_ref")
    assert token_text(single_tree(output, "identifier")) == "x0"
    assert len(list(observable.find_data("predicted_label_observable"))) == 1


def test_par_obs_002_parses_indexed_class_probability() -> None:
    observable = _single_observable(
        'forall x0 => target[x0].probability("approved") >= 0.80'
    )

    output = single_tree(observable, "model_output_ref")
    probability = single_tree(observable, "class_probability_observable")

    assert token_text(single_tree(output, "identifier")) == "x0"
    assert token_text(single_tree(probability, "string")) == '"approved"'


@pytest.mark.parametrize(
    "body, observable_rule",
    [
        pytest.param(
            'target.label == "approved"',
            "predicted_label_observable",
            id="PAR-OBS-003-label",
        ),
        pytest.param(
            'target.probability("approved") >= 0.80',
            "class_probability_observable",
            id="PAR-OBS-003-probability",
        ),
    ],
)
def test_par_obs_003_parses_unindexed_observables(
    body: str,
    observable_rule: str,
) -> None:
    observable = _single_observable(body)
    output = single_tree(observable, "model_output_ref")

    assert not list(output.find_data("identifier"))
    assert len(list(observable.find_data(observable_rule))) == 1


@pytest.mark.parametrize(
    "surface",
    [
        pytest.param("target[x0].probability()", id="PAR-OBS-004-missing"),
        pytest.param(
            'target[x0].probability("approved", "rejected")',
            id="PAR-OBS-004-multiple",
        ),
        pytest.param(
            "target[x0].probability(approved)",
            id="PAR-OBS-004-non-literal",
        ),
    ],
)
def test_par_obs_004_rejects_invalid_probability_arguments(surface: str) -> None:
    with pytest.raises(UnexpectedInput):
        parse_toetra_code(program(body=f"forall x0 => {surface} >= 0.8"))


@pytest.mark.parametrize(
    "surface",
    [
        pytest.param("target[x0].logit", id="PAR-OBS-005-logit"),
        pytest.param("target[x0].score", id="PAR-OBS-005-score"),
        pytest.param(
            "target[x0].predict_proba",
            id="PAR-OBS-005-predict-proba",
        ),
        pytest.param("target[x0].classes_", id="PAR-OBS-005-classes"),
        pytest.param(
            'target[x0].decision_function("approved")',
            id="PAR-OBS-005-decision-function",
        ),
    ],
)
def test_par_obs_005_rejects_internal_model_surfaces(surface: str) -> None:
    with pytest.raises(UnexpectedInput):
        parse_toetra_code(program(body=f"forall x0 => {surface} == 0"))
