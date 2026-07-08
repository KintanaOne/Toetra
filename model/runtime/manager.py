from pathlib import Path

from model.detector.detector import ModelDetector

from model.detector.model_framework import EnumModelFramework
from model.introspector.introspector_factory import (
    IntrospectorFactory,
)

from model.loader.loader_factory import LoaderFactory

from model.schema.model_schema import ModelSchema


class ModelManager:
    """
    Central orchestration layer for model handling.

    Responsibilities
    ----------------
    - load serialized models
    - detect ML framework
    - introspect model metadata
    - expose normalized ModelSchema
    """

    def __init__(
        self,
        model_path: str | Path,
        dataset_path: str | Path | None = None,
        schema=None,
        target_name: str | None = None,
    ):

        # --------------------------------------------------
        # Input artifacts
        # --------------------------------------------------

        self.model_path = Path(model_path)

        self.dataset_path = Path(dataset_path) if dataset_path is not None else None

        self.schema = schema

        self.target_name = target_name

        # --------------------------------------------------
        # Runtime artifacts
        # --------------------------------------------------

        self.model = None
        self.framework: EnumModelFramework | None = None
        self.model_schema: ModelSchema | None = None

    # ======================================================
    # Public API
    # ======================================================

    def build_schema(self) -> ModelSchema:
        """
        Main orchestration pipeline.
        """

        # --------------------------------------------------
        # 1. Select loader
        # --------------------------------------------------

        loader = LoaderFactory.get_loader(self.model_path)

        # --------------------------------------------------
        # 2. Load serialized model
        # --------------------------------------------------

        self.model = loader.load()

        # --------------------------------------------------
        # 3. Detect ML framework
        # --------------------------------------------------

        self.framework = ModelDetector().detect(self.model)

        # --------------------------------------------------
        # 4. Select introspector
        # --------------------------------------------------

        introspector = IntrospectorFactory.create(
            framework=self.framework,
            model=self.model,
            dataset_path=self.dataset_path,
            schema=self.schema,
            serialization_format=self.model_path.suffix,
            target_name=self.target_name,
        )

        # --------------------------------------------------
        # 5. Produce normalized schema
        # --------------------------------------------------

        self.model_schema = introspector.introspect()
        assert self.model_schema is not None
        return self.model_schema
