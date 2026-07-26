from enum import Enum

from toetra._language.vocabulary.utils import EnumMixin


class EnumOutputSelector(EnumMixin, Enum):
    """User-facing selectors available after a declared output reference."""

    LABEL = "label"
    PROBABILITY = "probability"
