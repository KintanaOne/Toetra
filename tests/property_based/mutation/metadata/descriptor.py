from dataclasses import dataclass

from tests.property_based.mutation.core.mutation import Mutation
from tests.property_based.mutation.metadata.contract import MutationContract
from tests.property_based.mutation.metadata.enums import Domain, Layer, Nature, Strategy


@dataclass(frozen=True, slots=True)
class MutationDescriptor:
    mutation: Mutation
    layer: Layer
    nature: Nature
    strategy: Strategy
    domain: Domain
    contract: MutationContract
    severity: float | None = None
