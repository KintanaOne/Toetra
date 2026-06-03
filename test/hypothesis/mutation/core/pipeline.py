from __future__ import annotations

from typing import List

from core.artifact import Artifact
from core.mutation import Mutation
from core.executor import MutationExecutor


class MutationPipeline:
    """
    Sequential composition of mutations applied to a DSL artifact.
    """

    def __init__(self, mutations: List[Mutation]):
        self.mutations = mutations
        self.executor = MutationExecutor()

    def run(self, artifact: Artifact) -> Artifact:
        """
        Apply all mutations sequentially.

        Args:
            artifact: Input DSL artifact.

        Returns:
            Mutated artifact after full pipeline execution.
        """

        for mutation in self.mutations:
            artifact = self.executor.apply(mutation, artifact)

        return artifact