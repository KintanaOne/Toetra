import re
import sys; print(sys.path)

from pathlib import Path
from forml.grammar.official_contents.problems import official_problems
from forml.grammar.official_contents.properties import official_properties
from forml.grammar.official_contents.quantifiers import official_quantifiers
from forml.grammar.official_contents.functions import official_functions
from forml.grammar.official_contents.backends import official_backends
from forml.grammar.official_contents.sets import official_sets
from forml.grammar.official_contents.protected_words import protected_words

# Dictionnaires et listes des types officiels
official_problems_dict          = official_problems
official_properties_dict        = official_properties
official_quantifiers_dict       = official_quantifiers
official_functions_dict         = official_functions
official_backends_dict          = official_backends
official_sets_dict              = official_sets
official_protected_words_dict   = protected_words

problem_list            = [f"{k} : {v}" for k, v in official_problems_dict.items()]
property_list           = [f"{k} : {v}" for k, v in official_properties_dict.items()]
quantifier_set_list     = [f"{k} : {v}" for k, v in official_quantifiers_dict.items()]
function_list           = [f"{k} : {v}" for k, v in official_functions_dict.items()]
backend_list            = [f"{k} : {v}" for k, v in official_backends_dict.items()]
set_list                = [f"{k} : {v}" for k, v in official_sets_dict.items()]
protected_words_list    = [f"{k} : {v}" for k, v in official_protected_words_dict.items()]

official_properties =       " | ".join(official_properties_dict.keys())
official_problems =         " | ".join(official_problems_dict.keys())
official_quantifiers =      " | ".join(official_quantifiers_dict.keys())
official_functions =        " | ".join(official_functions_dict.keys())
official_backends =         " | ".join(official_backends_dict.keys())
official_sets =             " | ".join(official_sets_dict.keys())
official_protected_words =  " | ".join(official_protected_words_dict.keys())

SPECIAL_SEQ = {
    "official_properties":  official_properties,
    "official_problems":    official_problems,
    "official_quantifier" : official_quantifiers,
    "official_functions":   official_functions,
    "official_backends":    official_backends,
    "official_sets" :       official_sets,
    "lowercase_string": r"/[a-z]+/",
    "uppercase_string": r"/[A-Z]+/",
    "number": "NUMBER",
    "CHAR": r"/[a-zA-Z]/",
    "digit": "DIGIT",
    "identifier_name": r"/[A-Za-z][A-Za-z0-9_.]*/",
    "escaped_string": "ESCAPED_STRING",
    "any_character_except_triple_quotes": r"/'''(.|\n)*?'''/",
    "any_character_except_newline": r'/[^\n]+/',
}

def transform_ebnf_brackets(line: str) -> str:
    """
    Transforme les notations EBNF {} et [] en syntaxe Lark.
    {} → répétition 0 ou plusieurs fois : (élément)*
    [] → optionnel (0 ou 1 fois) : (élément)?
    ⚠ Les regex /…/ et les séquences spéciales ?…? sont protégées.
    """
    def is_protected(inner: str) -> bool:
        inner = inner.strip()
        return (inner.startswith('/') and inner.endswith('/')) or \
               (inner.startswith('?') and inner.endswith('?'))

    def repl_curly(match):
        inner = match.group(1)
        if is_protected(inner):
            return match.group(0)
        return f"({inner})*"

    def repl_brackets(match):
        inner = match.group(1)
        if is_protected(inner):
            return match.group(0)
        return f"({inner})?"

    line = re.sub(r"\{([^}]+)\}", repl_curly, line)
    line = re.sub(r"\[([^\]]+)\]", repl_brackets, line)
    return line

def protect_brackets(line: str) -> str:
    """
    Protège les crochets, parenthèses et accolades entre guillemets ("[", "]", "(", ")", "{", "}")
    pour éviter qu'elles soient interprétées comme des structures EBNF par transform_ebnf_brackets().
    """
    def repl(match):
        content = match.group(0)
        # on protège uniquement les symboles entre guillemets
        replacements = {
            '"["': "___BRACKET_OPEN___",
            '"]"': "___BRACKET_CLOSE___",
            '"("': "___PAREN_OPEN___",
            '")"': "___PAREN_CLOSE___",
            '"{"': "___CURLY_OPEN___",
            '"}"': "___CURLY_CLOSE___",
            '","': '___COMMA___',
        }
        for k, v in replacements.items():
            content = content.replace(k, v)
        return content

    # cette regex capture toutes les chaînes entre guillemets doubles
    return re.sub(r'"[^"]*"', repl, line)


def unprotect_brackets(line: str) -> str:
    """
    Restaure les crochets, parenthèses et accolades protégées.
    """
    replacements = {
        "___BRACKET_OPEN___": '"["',
        "___BRACKET_CLOSE___": '"]"',
        "___PAREN_OPEN___": '"("',
        "___PAREN_CLOSE___": '")"',
        "___CURLY_OPEN___": '"{"',
        "___CURLY_CLOSE___": '"}"',
        "___COMMA___": '","',
    }
    for k, v in replacements.items():
        line = line.replace(k, v)
    return line

# Crée un motif regex qui détecte les mots exacts à remplacer
PROTECTED_PATTERN = re.compile(rf"\b({'|'.join(map(re.escape, protected_words.keys()))})\b")

def replace_protected_words(line: str) -> str:
    """Remplace les tokens protégés (style _IN) par leurs équivalents lisibles."""
    for k, v in protected_words.items():
        line = line.replace(k, v)
    return line


def replace_special_sequences(line: str) -> str:
    """
    Remplace les séquences spéciales ?nom? par leur valeur depuis SPECIAL_SEQ.
    - Si la valeur est une regex (/.../), elle est insérée telle quelle.
    - Si c'est une séquence multiple (avec "|"), elle est mise entre parenthèses.
    - Si le placeholder est inconnu, lève une KeyError.
    """
    def repl(match):
        key = match.group(1).strip()
        if key not in SPECIAL_SEQ:
            raise KeyError(f"Placeholder inconnu dans la grammaire: ?{key}?")
        value = SPECIAL_SEQ[key]

        # Si c'est une regex (commence et finit par /), on garde tel quel
        if isinstance(value, str) and value.startswith("/") and value.endswith("/"):
            return value

        # Pour les séquences multiples (backends, fonctions, etc.), on met entre parenthèses
        if "|" in str(value):
            return f"( {value} )"

        # Sinon on renvoie la valeur brute
        return str(value)

    return re.sub(r'\?\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\?', repl, line)


def ebnf_to_lark(ebnf_text: str) -> str:
    lines = ebnf_text.splitlines()
    lark_lines = []

    header = [
        "%import common.WS",
        "%import common.WS_INLINE",
        "%import common.NEWLINE",
        "%import common.ESCAPED_STRING",
        "%import common.NUMBER",
        "%import common.DIGIT",
        "%ignore WS_INLINE",
        # Définition des commentaires
        'COMMENT_LINE: /#[^\\n]*/',
        'COMMENT_BLOCK: /\'\'\'(.|\\n)*?\'\'\'/',
        "%ignore COMMENT_LINE",
        "%ignore COMMENT_BLOCK",
        "%ignore NEWLINE",
        "",
        "# === OFFICIAL PROBLEMS ===",
    ] + problem_list + [
        "",
        "# === OFFICIAL PROPERTIES ===",
    ] + property_list + [
        "",
        "# === OFFICIAL QUANTIFIER SETS ===",
    ] + quantifier_set_list + [
        "",
        "# === OFFICIAL FUNCTIONS ===",
    ] + function_list + [
        "",
        "# === OFFICIAL BACKENDS ===",
    ] + backend_list + [
        "",
        "# === OFFICIAL SETS ===",
    ] + set_list + [
        "",
    ]


    for raw_line in lines:
        if not raw_line.strip():
            lark_lines.append("")
            continue

        # commentaire
        if raw_line.strip().startswith("(*") and raw_line.strip().endswith("*)"):
            lark_lines.append("# " + raw_line.strip()[2:-2].strip())
            continue

        if raw_line.startswith("identifier ="):
            print("Debug: Found identifier line:", raw_line)

        line = re.sub(r"\(\*(.*?)\*\)", lambda m: "# " + m.group(1).strip(), raw_line.strip())
        
        # protéger les accolades/brackets/parenthèses entre guillemets
        line = protect_brackets(line)

        # accolades/brackets
        line = transform_ebnf_brackets(line)

        # restaurer les accolades/brackets/parenthèses protégées
        line = unprotect_brackets(line)
        
        # nettoyage des )?=
        line = re.sub(r"\?\+", "?", line)

        line = line.rstrip(";")
        line = re.sub(r"\s+,\s+", " ", line)
        # line = line
        line = re.sub(r"\s+", " ", line)

        # regex spéciaux
        line = replace_special_sequences(line)

        # mots protégés
        line = replace_protected_words(line)

        # string déjà géré par ESCAPED_STRING
        if re.match(r'^string\s*=', line):
            lark_lines.append("string : ESCAPED_STRING")
            continue

        # conversion EBNF assignment => Lark
        if re.match(r"^\w+\s*=", line):
            line = re.sub(r"^(\w+)\s*=", r"\1 : ", line)

        lark_lines.append(line)

    return "\n".join(header + lark_lines)

def main():
    input_path = Path("forml/grammar/forml_grammar.ebnf")
    output_path = Path("forml/grammar/forml_grammar.lark")

    ebnf_text = input_path.read_text(encoding="utf-8")
    try:
        lark_text = ebnf_to_lark(ebnf_text)
        output_path.write_text(lark_text, encoding="utf-8")
        print(f"✅ Converted `{input_path.name}` → `{output_path.name}`")
    except KeyError as e:
        print(f"❌ EBNF to Lark Error: {e}")

if __name__ == "__main__":
    main()
