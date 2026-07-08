from model.detector.model_framework import EnumModelFramework

from model.introspector.base_introspector import BaseIntrospector

from model.introspector.sklearn_introspector import (
    SklearnIntrospector,
)

from model.introspector.xgboost_introspector import (
    XGBoostIntrospector,
)

from model.errors.introspection import (
    UnsupportedIntrospectorError,
)


class IntrospectorFactory:
    """
    Factory responsible for selecting the correct
    introspector implementation depending on the
    detected ML framework.
    """

    INTROSPECTORS: dict[EnumModelFramework, type[BaseIntrospector]] = {
        EnumModelFramework.SKLEARN: SklearnIntrospector,
        EnumModelFramework.XGBOOST: XGBoostIntrospector,
    }

    @classmethod
    def create(
        cls,
        framework,
        model,
        dataset_path,
        schema=None,
        serialization_format=None,
        target_name: str | None = None,
    ) -> BaseIntrospector:
        """
        Create the appropriate introspector instance.
        """

        introspector_class = cls.INTROSPECTORS.get(framework)

        if introspector_class is None:

            raise UnsupportedIntrospectorError(
                f"No introspector available for framework '{framework}'"
            )

        return introspector_class(
            model=model,
            source_path=dataset_path,
            schema=schema,
            serialization_format=serialization_format,
            target_name=target_name,
        )
