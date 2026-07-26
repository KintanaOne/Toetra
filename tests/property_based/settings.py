from hypothesis import settings

DEFAULT_SETTINGS = settings(
    max_examples=200,
    deadline=None,  # important pour parser
    suppress_health_check=[],
)
