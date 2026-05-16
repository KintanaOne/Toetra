from hypothesis import strategies as st

IDENTIFIER_REGEX = r"[a-zA-Z_][a-zA-Z0-9_]*"

identifiers = st.from_regex(IDENTIFIER_REGEX, fullmatch=True)

escaped_strings = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_./-",
    min_size=1,
    max_size=30
).map(lambda s: f'"{s}"')

numbers = st.floats(
    min_value=0,
    max_value=100,
    allow_nan=False,
    allow_infinity=False
).map(lambda x: str(round(x, 3)))

booleans = st.sampled_from(["true", "false", "True", "False"])