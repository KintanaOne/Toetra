from __future__ import annotations

from typing import Iterable

from dsl.ir.ir1.model_quantities import ModelQuantityExpressionIR
from dsl.ir.ir1.nodes import (
    ModelEvaluationIR,
    PointBindingIR,
    ScopeIR,
    TargetExpressionIR,
)
from dsl.ir.ir1.scalar import iter_scalar_expressions
from dsl.ir.ir2.dsl.nodes import (
    CNFFormulaIR2,
    DNFFormulaIR2,
    FormulaIR2,
    LiteralIR2,
    NNFFormulaIR2,
    PointIdentityMapIR2,
    QuantifierStructureIR2,
)


class PointAwareIR2Analyzer:
    """Build point/evaluation/quantifier artifacts for one IR2 task."""

    def point_mappings(self, scope: ScopeIR) -> tuple[PointIdentityMapIR2, ...]:
        return tuple(
            PointIdentityMapIR2(source_name=point.name, ir_point=point)
            for point in self._unique_points(scope.points)
        )

    def quantifier_structure(self, scope: ScopeIR) -> QuantifierStructureIR2:
        binders = tuple(scope.binders)
        if not binders and scope.kind == "quantifier" and scope.quantifier is not None:
            return QuantifierStructureIR2(
                binder_sequence=(self._normalize_quantifier(scope.quantifier),)
            )
        sequence = tuple(
            self._normalize_quantifier(binder.quantifier) for binder in binders
        )
        return QuantifierStructureIR2(
            binders=binders,
            binder_sequence=sequence,
            alternation_depth=self._alternation_depth(sequence),
        )

    def model_evaluations(
        self,
        *,
        spec_formula: NNFFormulaIR2,
    ) -> tuple[ModelEvaluationIR, ...]:
        evaluations: list[ModelEvaluationIR] = []
        seen: set[ModelEvaluationIR] = set()
        for evaluation in self._iter_model_evaluations(spec_formula):
            if evaluation not in seen:
                seen.add(evaluation)
                evaluations.append(evaluation)
        return tuple(evaluations)

    def _iter_model_evaluations(
        self, formula: FormulaIR2
    ) -> Iterable[ModelEvaluationIR]:
        for literal in self._iter_literals_or_atoms(formula):
            atom = literal.atom if isinstance(literal, LiteralIR2) else literal
            for root in (getattr(atom, "left", None), getattr(atom, "right", None)):
                if root is None:
                    continue
                for expression in iter_scalar_expressions(root):
                    if isinstance(expression, ModelQuantityExpressionIR):
                        yield expression.evaluation
                    elif (
                        isinstance(expression, TargetExpressionIR)
                        and expression.evaluation is not None
                    ):
                        yield expression.evaluation

    def _iter_literals_or_atoms(self, formula: FormulaIR2) -> Iterable[object]:
        if isinstance(formula, NNFFormulaIR2):
            yield from self._iter_atoms_from_logical(formula.expression)
            return
        if isinstance(formula, CNFFormulaIR2):
            for clause in formula.clauses:
                yield from clause.literals
            return
        if isinstance(formula, DNFFormulaIR2):
            for term in formula.terms:
                yield from term.literals
            return
        raise TypeError(f"Unsupported IR2 formula type: {type(formula).__name__}")

    def _iter_atoms_from_logical(self, node: object) -> Iterable[object]:
        from dsl.ir.ir1.nodes import AndIR, AtomicIR, NotIR, OrIR

        if isinstance(node, AtomicIR):
            yield node
            return
        if isinstance(node, NotIR):
            yield from self._iter_atoms_from_logical(node.operand)
            return
        if isinstance(node, (AndIR, OrIR)):
            for operand in node.operands:
                yield from self._iter_atoms_from_logical(operand)
            return
        raise TypeError(
            "Unsupported logical IR node while collecting evaluations: "
            f"{type(node).__name__}"
        )

    @staticmethod
    def _unique_points(
        points: tuple[PointBindingIR, ...],
    ) -> tuple[PointBindingIR, ...]:
        unique: list[PointBindingIR] = []
        seen: set[PointBindingIR] = set()
        for point in points:
            if point not in seen:
                seen.add(point)
                unique.append(point)
        return tuple(unique)

    @staticmethod
    def _normalize_quantifier(quantifier: str) -> str:
        normalized = {"∀": "forall", "∃": "exists"}.get(
            quantifier.strip(), quantifier.strip().lower()
        )
        if normalized not in {"forall", "exists"}:
            raise ValueError(f"Unsupported IR1 quantifier: {quantifier!r}")
        return normalized

    @staticmethod
    def _alternation_depth(sequence: tuple[str, ...]) -> int:
        return sum(a != b for a, b in zip(sequence, sequence[1:]))
