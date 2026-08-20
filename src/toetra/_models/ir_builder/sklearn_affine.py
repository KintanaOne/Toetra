from sklearn.linear_model import LinearRegression, LogisticRegression

from toetra._models.ir.affine import AffineModelIR

class SklearnAffineModelIRBuilder:
    def build(
        self,
        model,
        schema) -> AffineModelIR:
        # Implement the logic to build the intermediate representation (IR) for the Sklearn Affine model
        if not type(model) not in (LinearRegression, LogisticRegression):
            raise TypeError("Input model must be a Sklearn Affine model")

        coefficients = model.coef_
        bias = model.intercept_
        features = schema.features

        