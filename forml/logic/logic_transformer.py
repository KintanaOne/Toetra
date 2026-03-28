# forml/logic/logic_transform.py

from pathlib import Path

from forml.logic.core import Var, Model, Not, And, Implies, Expr
from forml.logic.quantifiers import ForAll, Exists
from forml.logic.predicates import dist_l1, dist_l2, argmax_eq, abs_diff_leq, dist_linf
from forml.transformer.transformer import transform_forml_code


# =========================
# AST → IR
# =========================

def convert_program(program) -> Expr:
    """
    Convert transformer AST → Logic IR
    """

    # =========================
    # HEADER → MODEL
    # =========================
    model_decl = program.header.model
    model_path = model_decl.path

    section = program.body.sections[0]
    prop = section.property
    assertion = prop.assertion.expr

    # infer output type
    if assertion.problem == "CLASSIFICATION":
        output_type = "classification"
    elif assertion.problem == "REGRESSION":
        output_type = "regression"
    else:
        raise NotImplementedError

    model = Model(
        name="f",
        path=model_path,
        output_type=output_type
    )

    # =========================
    # VARIABLES
    # =========================
    x = Var("x")
    xp = Var("x'")

    fx = model(x)
    fxp = model(xp)

    # =========================
    # CONDITION (hyperball)
    # =========================
    universal = prop.universal_expr

    if universal.set.func.value != "hyperball":
        raise NotImplementedError("Only hyperball supported")

    # TODO: extract from AST later
    norm = universal.set.args[0]
    eps = universal.set.args[1]
    
    if norm == "L1":
        condition = dist_l1(x, xp, eps)
    elif norm == "L2":
        condition = dist_l2(x, xp, eps)
    elif norm == "Linf":
        condition = dist_linf(x, xp, eps)
    else:
        raise NotImplementedError

    # =========================
    # RELATION
    # =========================
    func = assertion.function.function.value

    if output_type == "classification":
        if func == "EQUAL":
            relation = argmax_eq(fx, fxp)
        else:
            raise NotImplementedError

    elif output_type == "regression":
        if func == "CLOSE":
            relation = abs_diff_leq(fx, fxp, eps)
        else:
            raise NotImplementedError

    else:
        raise NotImplementedError

    # =========================
    # QUANTIFIER
    # =========================
    quantifier = universal.quantifier.value

    if quantifier == "forall":
        return ForAll(
            [x, xp],
            Implies(condition, relation)
        )

    elif quantifier == "exists":
        return Exists(
            [x, xp],
            And(condition, relation)
        )

    else:
        raise NotImplementedError


# =========================
# Property → Counterexample
# =========================

def to_counterexample(expr: Expr) -> Expr:
    if isinstance(expr, ForAll):
        return Exists(expr.vars, _negate(expr.body))
    raise NotImplementedError


def _negate(expr: Expr) -> Expr:
    if isinstance(expr, Implies):
        return And(expr.premise, Not(expr.conclusion))

    if isinstance(expr, And):
        return Not(expr)

    if isinstance(expr, Not):
        return expr.expr

    return Not(expr)


if __name__ == "__main__":
    test_path = Path(__file__).parent.parent / "example/00_simple_correct_example_multi_comment.forml"
    print(test_path)
    if test_path.exists():
        with open(test_path, "r", encoding="utf-8") as f:
            code = f.read()
    program = transform_forml_code(code)

    print(program)
    
    phi = convert_program(program)
    print(phi)

    cex = to_counterexample(phi)
    print(cex)