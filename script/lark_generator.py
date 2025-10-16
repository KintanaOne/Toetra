import re
import sys; print(sys.path)

from pathlib import Path
from forml.grammar.official_contents.official_problems import official_problems
from forml.grammar.official_contents.official_properties import official_properties
from forml.grammar.official_contents.official_quantifier_sets import official_quantifier_sets
from forml.grammar.official_contents.official_functions import official_functions
from forml.grammar.official_contents.official_backends import official_backends

# Dictionnaires et listes des types officiels
official_problem_dict = official_problems
official_property_dict = official_properties
official_quantifier_sets_dict = official_quantifier_sets
official_function_dict = official_functions
official_backends_dict = official_backends

problem_list = [f"{k} : {v}" for k, v in official_problem_dict.items()]
property_list = [f"{k} : {v}" for k, v in official_property_dict.items()]
quantifier_set_list = [f"{k} : {v}" for k, v in official_quantifier_sets_dict.items()]
function_list = [f"{k} : {v}" for k, v in official_function_dict.items()]
backend_list = [f"{k} : {v}" for k, v in official_backends_dict.items()]

official_properties = " | ".join(official_property_dict.keys())
official_problems = " | ".join(official_problem_dict.keys())
official_quantifier_sets = " | ".join(official_quantifier_sets_dict.keys())
official_functions = " | ".join(official_function_dict.keys())
official_backends = " | ".join(official_backends_dict.keys())

SPECIAL_SEQ = {
    "official_properties": official_properties,
    "official_problems": official_problems,
    "official_quantifier_sets" : official_quantifier_sets,
    "official_functions": official_functions,
    "official_backends": official_backends,
    "lowercase_string": r"/[a-z]+/",
    "uppercase_string": r"/[A-Z]+/",
    "number": "NUMBER",
    "CHAR": r"/[a-zA-Z]/",
    "digit": "DIGIT",
    "identifier_name": r"/[A-Za-z_][A-Za-z0-9_.]*/",
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
        "%ignore WS",
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
    ] + backend_list + [""]



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
