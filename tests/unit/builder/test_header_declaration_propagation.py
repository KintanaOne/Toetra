from toetra._compiler.builder.core.pretty_ast import pretty
from toetra._compiler.builder.header import parse_header
from toetra._compiler.builder.program import parse_program
from toetra._compiler.builder.core.utils import find_child
from toetra._compiler.parser.parser import parse_toetra_code

_SOURCE = """
model := "models/model.joblib"
target := risk_score
dataset := "data/reference.csv"
maximum_risk := 0.20
strict_mode := true
anchor baseline := { age: 42, income: 58000.0 }

[BOUND]:
target[baseline] <= maximum_risk using Z3
"""


def test_header_declarations_reach_ast_without_loss() -> None:
    program = parse_program(parse_toetra_code(_SOURCE))

    assert program.header.model == "models/model.joblib"
    assert program.header.target == "risk_score"
    assert program.header.dataset == "data/reference.csv"
    assert [item.name for item in program.header.specification_constants] == [
        "maximum_risk",
        "strict_mode",
    ]
    assert [item.name for item in program.anchors] == ["baseline"]


def test_pretty_ast_preserves_header_dataset_and_constants() -> None:
    program = parse_program(parse_toetra_code(_SOURCE))
    rendered = pretty(program)

    assert "model := models/model.joblib" in rendered
    assert "target := risk_score" in rendered
    assert "dataset := data/reference.csv" in rendered
    assert "maximum_risk := 0.2" in rendered
    assert "strict_mode := True" in rendered
    assert "anchor baseline" in rendered


def test_header_builder_accepts_program_or_header_subtree() -> None:
    program_tree = parse_toetra_code(_SOURCE)
    header_tree = find_child(program_tree, "header")

    assert header_tree is not None
    assert parse_header(program_tree) == parse_header(header_tree)
