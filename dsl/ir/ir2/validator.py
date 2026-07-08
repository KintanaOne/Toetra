from __future__ import annotations

from dsl.ir.ir2.enums import NormalFormKind
from dsl.ir.ir2.errors import IR2ValidationError
from dsl.ir.ir2.guard import NNFGuard
from dsl.ir.ir2.nodes import (
    CNFFormulaIR2,
    DNFFormulaIR2,
    NNFFormulaIR2,
    VerificationTaskIR2,
)


class IR2Validator:
    """Validates VerificationTaskIR2 invariants."""

    def validate(self, task: VerificationTaskIR2) -> None:
        if not isinstance(task.spec_formula, NNFFormulaIR2):
            raise IR2ValidationError("spec_formula must be NNFFormulaIR2.")

        NNFGuard.assert_expr_is_nnf(task.spec_formula.expression)

        if task.normal_form == NormalFormKind.NNF:
            if not isinstance(task.verification_condition, NNFFormulaIR2):
                raise IR2ValidationError("normal_form=NNF requires NNFFormulaIR2.")
            NNFGuard.assert_expr_is_nnf(task.verification_condition.expression)

        elif task.normal_form == NormalFormKind.CNF:
            if not isinstance(task.verification_condition, CNFFormulaIR2):
                raise IR2ValidationError("normal_form=CNF requires CNFFormulaIR2.")

        elif task.normal_form == NormalFormKind.DNF:
            if not isinstance(task.verification_condition, DNFFormulaIR2):
                raise IR2ValidationError("normal_form=DNF requires DNFFormulaIR2.")

        else:
            raise IR2ValidationError(f"Unsupported normal form: {task.normal_form}")

        if task.requirements.normal_form != task.normal_form:
            raise IR2ValidationError(
                "requirements.normal_form must match task.normal_form."
            )
