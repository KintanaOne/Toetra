# dsl/language/tools/registry.py

from dsl.language.vocabulary.protected_words import protected_words
from dsl.language.tools.constants import OFFICIAL_MAPS


SPECIAL_SEQ = {
    "official_properties": " | ".join(OFFICIAL_MAPS["properties"].keys()),
    "official_problems": " | ".join(OFFICIAL_MAPS["problems"].keys()),
    "official_quantifier": " | ".join(OFFICIAL_MAPS["quantifiers"].keys()),
    "official_functions": " | ".join(OFFICIAL_MAPS["functions"].keys()),
    "official_backends": " | ".join(OFFICIAL_MAPS["backends"].keys()),
    "official_metrics": " | ".join(OFFICIAL_MAPS["metrics"].keys()),
    "official_logic_operators": " | ".join(OFFICIAL_MAPS["logic_operations"].keys()),
    "comparison_operators": " | ".join(OFFICIAL_MAPS["comparison_operators"].keys()),
}


PRIMITIVE_SEQ = {
    "lowercase_string": r"/[a-z]+/",
    "uppercase_string": r"/[A-Z]+/",
    "number": "NUMBER",
    "CHAR": r"/[a-zA-Z]/",
    "digit": "DIGIT",
    "identifier_name": "IDENTIFIER",
    "escaped_string": "ESCAPED_STRING",
}


MISC_SEQ = {
    "any_character_except_triple_quotes": r"/'''(.|\n)*?'''/",
    "any_character_except_newline": r"/[^\n]+/",
    "pairwise_token": r"/[A-Za-z][A-Za-z0-9_]*\s*~\s*[A-Za-z][A-Za-z0-9_]*'/",
}


GRAMMAR_REGISTRY = {
    "SPECIAL_SEQ": SPECIAL_SEQ,
    "PRIMITIVE_SEQ": PRIMITIVE_SEQ,
    "MISC_SEQ": MISC_SEQ,
    "PROTECTED_WORDS": protected_words,
}