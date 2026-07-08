from __future__ import annotations

from dsl.ir.ir1.nodes import AtomicIR


class ModelConstraintIR2(AtomicIR):
    """Base class for backend-neutral model constraints.

    Model constraints are logical atoms from the point of view of NNF/CNF/DNF
    normalization.
    """

    pass
