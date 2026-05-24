"""
Multi-layer invalid FORML program generation.

Pipeline:
    valid_program (string)
        ↓
    lexical invalid strategy
        ↓
    CST
        ↓
    structural invalid strategy
        ↓
    AST
        ↓
    semantic invalid strategy

This module orchestrates invalid generation across
FORML pipeline layers.
"""

import random
from hypothesis.strategies import composite

from dsl.parser.parser import parse_forml_code
from dsl.builder.program import parse_program

from test.hypothesis.strategies.valid.valid_lexical import valid_lexical_program

# ================================
# STRATEGY LAYERS (NOT MUTATIONS)
# ================================

from test.hypothesis.strategies.invalid.invalid_lexical import invalid_lexical_program
from test.hypothesis.strategies.invalid.invalid_syntactic import invalid_syntactic_program
from test.hypothesis.strategies.invalid.invalid_logical import invalid_ast_program


# =========================================================
# MAIN STRATEGY
# =========================================================

@composite
def invalid_program(
    draw,
    string_ratio: float = 0.4,
    cst_ratio: float = 0.3,
    ast_ratio: float = 0.3,
):
    """
    Generate invalid FORML programs across multiple layers.

    Each layer has its own invalid strategy responsible
    for producing controlled corruption.
    """

    assert 0 <= string_ratio <= 1, "string_ratio must be in [0, 1]"
    assert 0 <= cst_ratio <= 1, "cst_ratio must be in [0, 1]"
    assert 0 <= ast_ratio <= 1, "ast_ratio must be in [0, 1]"
    assert (string_ratio + cst_ratio + ast_ratio) <= 1, "Total ratio must be <= 1"

    # -----------------------------------------------------
    # STEP 1: valid program
    # -----------------------------------------------------

    program = draw(valid_lexical_program())

    # -----------------------------------------------------
    # STEP 2: string corruption
    # -----------------------------------------------------

    if random.random() < string_ratio:
        program = draw(invalid_lexical_program(program))

    # -----------------------------------------------------
    # STEP 3: parse CST
    # -----------------------------------------------------

    try:
        cst = parse_forml_code(program)
    except Exception:
        return program

    # -----------------------------------------------------
    # STEP 4: cst corruption
    # -----------------------------------------------------

    if random.random() < cst_ratio:
        cst = draw(invalid_syntactic_program(cst))

    # -----------------------------------------------------
    # STEP 5: parse AST
    # -----------------------------------------------------

    try:
        ast = parse_program(cst)
    except Exception:
        return cst

    # -----------------------------------------------------
    # STEP 6: ast corruption
    # -----------------------------------------------------

    if random.random() < ast_ratio:
        ast = draw(invalid_ast_program(ast))

    return ast