from typing import Protocol

from toetra._models.ir.base import ModelIR
from toetra._models.schema.model_schema import ModelSchema


class ModelIRBuilder(Protocol):
    def build(
        self,
        model: object,
        schema: ModelSchema,
    ) -> ModelIR:
        """Build a normalized Model IR from a source model and schema.

        Args:
            model: The source framework model.
            schema: The normalized model interface.

        Returns:
            The normalized Toetra model computation.
        """
        ...
