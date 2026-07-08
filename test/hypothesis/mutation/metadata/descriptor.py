from dataclasses import dataclass

from test.hypothesis.mutation.core.mutation import Mutation
from test.hypothesis.mutation.metadata.contract import MutationContract
from test.hypothesis.mutation.metadata.enums import Domain, Layer, Nature, Strategy


@dataclass(frozen=True, slots=True)
class MutationDescriptor:
    mutation: Mutation
    layer: Layer
    nature: Nature
    strategy: Strategy
    domain: Domain
    contract: MutationContract
    severity: float | None = None
