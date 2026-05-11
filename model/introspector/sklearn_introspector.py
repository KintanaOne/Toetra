
from model.introspector.base_introspector import BaseIntrospector
from model.schema.modesl_schema import ModelSchema


class SklearnIntrospector(BaseIntrospector):

    def introspect(self):

        # Check if the model has the attribute 'feature_names_in_' which is common in sklearn models
        if hasattr(self.model, "feature_names_in_"):
            features = {feature: str(type(getattr(self.model, feature))) for feature in self.model.feature_names_in_}


        return ModelSchema(
            name=self.model.__class__.__name__,
            features={feature: str(type(getattr(self.model, feature))) for feature in dir(self.model) if not feature.startswith('_')}
        )