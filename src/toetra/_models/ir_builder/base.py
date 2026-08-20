

from typing import Protocol

from toetra._models.ir.base import ModelIR
from toetra._models.schema.model_schema import ModelSchema


class ModelIRBuilder(Protocol):
    def build(
        self,
        model: object,
        schema: ModelSchema,
    ) -> ModelIR:
        """Build a normalized Toetra Model IR from a source model and normalized schema.

        Args:
            model (object): The input model representation.
            schema (ModelSchema): The normalized schema describing the model interface.

        Returns:
            ModelIR: The normalized Toetra model representation.
        """
        ...