import random
from copy import deepcopy
from typing import List

from test.hypothesis.mutation.functions.semantic.helper.constraint import SemanticConstraint
from test.hypothesis.mutation.functions.semantic.helper.constraint import SemanticConstraintSet



class SemanticConstraintEngine:
    """
    Core engine for semantic constraint manipulation.

    Responsibilities:
        - extract constraints from AST (future integration)
        - inject contradictions
        - corrupt constraints
        - generate impossible states
    """

    # =========================================================
    # CONTRADICTION GENERATION
    # =========================================================

    def inject_contradiction(
        self,
        constraints: SemanticConstraintSet,
    ) -> SemanticConstraintSet:
        """
        Create semantic contradiction:
            age > 18 AND age < 0
        """

        mutated = deepcopy(constraints)

        if not mutated.constraints:
            return mutated

        c = random.choice(mutated.constraints)

        contradiction = SemanticConstraint(
            field=c.field,
            operator=self._invert_operator(c.operator),
            value=self._generate_invalid_value(c.value),
            context=c.context,
        )

        mutated.add(contradiction)

        return mutated

    # =========================================================
    # OPERATOR INVERSION
    # =========================================================

    def _invert_operator(self, op: str) -> str:
        """
        Invert semantic meaning of operator.
        """

        mapping = {
            ">": "<",
            "<": ">",
            ">=": "<=",
            "<=": ">=",
            "==": "!=",
            "!=": "==",
        }

        return mapping.get(op, op)

    # =========================================================
    # VALUE CORRUPTION
    # =========================================================

    def _generate_invalid_value(self, value):
        """
        Generate semantically invalid value.
        """

        # numeric case
        if isinstance(value, (int, float)):
            return -abs(value) - 1

        # boolean case
        if isinstance(value, bool):
            return not value

        # fallback corruption
        return None
    
    def _mutate_constraint(self, c, *, operator=None, value=None):
        """
        Create a new SemanticConstraint instead of modifying in-place.
        """

        return SemanticConstraint(
            field=c.field,
            operator=operator if operator is not None else c.operator,
            value=value if value is not None else c.value,
            context=c.context,
        )

    # =========================================================
    # RANDOM CORRUPTION
    # =========================================================

    def corrupt_random_constraint(
        self,
        constraints: SemanticConstraintSet,
    ) -> SemanticConstraintSet:
        """
        Randomly corrupt one constraint.
        """

        mutated = deepcopy(constraints)

        if not mutated.constraints:
            return mutated

        idx = random.randrange(len(mutated.constraints))
        c = mutated.constraints[idx]

        mutated.constraints[idx] = self._mutate_constraint(
            c,
            operator=self._invert_operator(c.operator),
            value=self._generate_invalid_value(c.value),
        )

        return mutated