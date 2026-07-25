# test/hypothesis/utils/serialize.py

"""
Simple DSL serializer.

IMPORTANT:
This is an MVP serializer.

It should later become:
    AST -> canonical Toetra Specification Language serializer

The goal for now is:
    - support AST mutation testing
    - allow parser roundtrip
    - generate coherent DSL strings
"""


def serialize(obj):
    """
    Serialize a parsed AST/CST object back into DSL text.
    """

    # -----------------------------------------------------
    # Raw strings
    # -----------------------------------------------------

    if isinstance(obj, str):
        return obj

    # -----------------------------------------------------
    # Lists
    # -----------------------------------------------------

    if isinstance(obj, list):
        return "\n".join(serialize(x) for x in obj)

    # -----------------------------------------------------
    # Dictionaries
    # -----------------------------------------------------

    if isinstance(obj, dict):

        parts = []

        for key, value in obj.items():
            parts.append(f"{key}: {serialize(value)}")

        return "\n".join(parts)

    # -----------------------------------------------------
    # Generic objects with __dict__
    # -----------------------------------------------------

    if hasattr(obj, "__dict__"):

        parts = []

        for key, value in vars(obj).items():

            # Skip empty values
            if value is None:
                continue

            serialized = serialize(value)

            parts.append(f"{key}={serialized}")

        return "\n".join(parts)

    # -----------------------------------------------------
    # Fallback
    # -----------------------------------------------------

    return str(obj)
