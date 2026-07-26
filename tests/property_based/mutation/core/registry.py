from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from metadata.descriptor import MutationDescriptor
from tests.property_based.mutation.core.filtering import MutationFilterEngine


@dataclass
class MutationRegistry:
    """
    Central registry of MutationDescriptors.

    This is the source of truth for all mutation strategies.
    """

    _items: List[MutationDescriptor] = field(default_factory=list)

    # ---------------------------------------------------------
    # registration
    # ---------------------------------------------------------

    def register(self, descriptor: MutationDescriptor) -> None:
        """
        Register a new mutation descriptor.
        """
        self._items.append(descriptor)

    # ---------------------------------------------------------
    # access
    # ---------------------------------------------------------

    def all(self) -> List[MutationDescriptor]:
        """
        Return all registered mutations.
        """
        return list(self._items)

    # ---------------------------------------------------------
    # filtering entrypoint
    # (delegates to filtering engine)
    # ---------------------------------------------------------

    def filter(
        self, engine: MutationFilterEngine, **kwargs
    ) -> List[MutationDescriptor]:
        """
        Filter mutations using a filtering engine.
        """
        return engine.filter(self._items, **kwargs)


# =========================================================
# GLOBAL SINGLETON (IMPORTANT)
# =========================================================

GLOBAL_MUTATION_REGISTRY = MutationRegistry()
