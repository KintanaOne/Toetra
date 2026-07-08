from __future__ import annotations

from core.mutation import Mutation
from metadata.contract import MutationContract
from metadata.enums import Layer, Nature, Strategy, Domain
from test.hypothesis.mutation.core.registry import GLOBAL_MUTATION_REGISTRY
from test.hypothesis.mutation.metadata.descriptor import MutationDescriptor


def mutation(
    *,
    name: str,
    layer: Layer,
    nature: Nature,
    strategy: Strategy,
    domain: Domain,
    contract: MutationContract,
    severity: float | None = None,
):

    def wrapper(fn):

        descriptor = MutationDescriptor(
            mutation=Mutation(name=name, fn=fn),
            layer=layer,
            nature=nature,
            strategy=strategy,
            domain=domain,
            contract=contract,
            severity=severity,
        )

        # =====================================================
        # 🔥 REGISTRY IMPLICITE
        # =====================================================
        GLOBAL_MUTATION_REGISTRY.register(descriptor)

        # Optionnel : attacher le descriptor à la fonction
        fn._mutation_descriptor = descriptor

        return descriptor

    return wrapper
