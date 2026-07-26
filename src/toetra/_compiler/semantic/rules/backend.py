from toetra._language.vocabulary.backends import EnumBackend
from toetra._language.vocabulary.properties import EnumProperty
from toetra._compiler.semantic.errors.errors import InvalidPropertyError

V1_SUPPORTED_BACKENDS = {
    EnumBackend.Z3,
}


PROPERTY_BACKEND_COMPATIBILITY = {
    EnumProperty.ROBUSTNESS: {EnumBackend.Z3},
    EnumProperty.BOUND: {EnumBackend.Z3},
    EnumProperty.LOGIC: {EnumBackend.Z3},
    EnumProperty.MONOTONICITY: {EnumBackend.Z3},
    EnumProperty.STABILITY: {EnumBackend.Z3},
    EnumProperty.FAIRNESS: {EnumBackend.Z3},
}


def validate_backend_for_property(property_type, backend):
    """
    Validate backend compatibility for the current V1.

    V1 policy:
        - Z3 is the only active verification backend.
        - Other backends may remain in grammar as reserved/future values,
          but should not be accepted as executable backends yet.
    """

    if backend is None:
        return True

    if backend not in V1_SUPPORTED_BACKENDS:
        raise InvalidPropertyError(
            f"Backend '{backend.value}' is declared but not supported in V1. "
            "Only Z3 is currently supported."
        )

    allowed = PROPERTY_BACKEND_COMPATIBILITY.get(property_type)

    if allowed is None:
        raise InvalidPropertyError(
            f"No backend compatibility rule defined for property '{property_type.value}'"
        )

    if backend not in allowed:
        allowed_names = ", ".join(b.value for b in allowed)

        raise InvalidPropertyError(
            f"Backend '{backend.value}' is not compatible with property "
            f"'{property_type.value}'. Allowed backends: {allowed_names}"
        )

    return True
