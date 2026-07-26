from hypothesis import strategies as st
from .primitives import numbers, booleans, escaped_strings

values = st.one_of(numbers, booleans, escaped_strings)
