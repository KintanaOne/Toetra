from __future__ import annotations

from core.artifact import Artifact
from core.mutation import Mutation


class MutationExecutor:
    """
    Executes a mutation on a DSL artifact.

    This class contains no domain logic.
    """

    def apply(self, mutation: Mutation, artifact: Artifact) -> Artifact:
        """
        Apply a mutation function to an artifact.

        Args:
            mutation: The mutation operator to apply.
            artifact: The input DSL artifact.

        Returns:
            A new mutated artifact.
        """

        new_value = mutation.fn(artifact.value)

        return Artifact(
            value=new_value,
            layer=artifact.layer,
        )