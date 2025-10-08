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
    "lowercase_string": r"/[a-z]+/",
    "uppercase_string": r"/[A-Z]+/",
    "NUMBER": "common.NUMBER",
    "CHAR": r"/[a-zA-Z]/",
    "digit": r"/[0-9]/",
    "any_character_except_quotes": "ESCAPED_STRING",
    "any_character_except_triple_quotes": r"/'''(.|\n)*?'''/",
    "any_character_except_newline": r'/[^\n]+/',
}

def transform_ebnf_brackets(line: str) -> str:
    """
    Transforme les notations EBNF {} et [] en syntaxe Lark.
    
    {} → répétition 0 ou plusieurs fois : (élément)*
    [] → optionnel (0 ou 1 fois) : (élément)?
    
    ⚠ Les regex Lark encadrées par /.../ sont protégées et ne sont pas modifiées.
    """

    # 🔹 Transformation des accolades { ... } pour répétition
    def repl_curly(match):
        inner = match.group(1)
        if inner.startswith('/') and inner.endswith('/'):
            return match.group(0)  # regex protégée
        return f"({inner})*"

    line = re.sub(r"\{([^}]+)\}", repl_curly, line)

    # 🔹 Transformation des crochets [ ... ] pour optionnel
    # On protège aussi les regex déjà
    def repl_brackets(match):
        inner = match.group(1)
        if inner.startswith('/') and inner.endswith('/'):
            return match.group(0)
        return f"({inner})?"

    line = re.sub(r"\[([^\]]+)\]", repl_brackets, line)

    return line

def replace_special_sequences(line: str) -> str:
    """
    Remplace les séquences spéciales ?nom? par leur regex ou valeur définie
    dans SPECIAL_SEQ. Les regex sont déjà protégées pour ne pas subir de ?+.
    """
    def repl(match):
        key = match.group(1).strip()
        value = SPECIAL_SEQ.get(key, "/.*/")
        return value
    return re.sub(r'\?\s*(.*?)\s*\?', repl, line)


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
    ]
    
    header += problem_list + [""] # Ajout des types de problème officiels
    header += property_list + [""]  # Ajout des propriétés officielles

    for raw_line in lines:
        if not raw_line.strip():
            lark_lines.append("")
            continue

        # commentaire
        if raw_line.strip().startswith("(*") and raw_line.strip().endswith("*)"):
            lark_lines.append("# " + raw_line.strip()[2:-2].strip())
            continue
        line = re.sub(r"\(\*(.*?)\*\)", lambda m: "# " + m.group(1).strip(), raw_line.strip())

        # regex spéciaux
        line = replace_special_sequences(line)

        # accolades/brackets
        line = transform_ebnf_brackets(line)

        # nettoyage des )?=
        line = re.sub(r"\?\+", "?", line)

        line = line.rstrip(";")
        line = re.sub(r"\s*,\s*", " ", line)
        line = re.sub(r"\s+", " ", line)

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
    input_path = Path("src/grammar/forml_grammar copy.ebnf")
    output_path = Path("src/grammar/forml_grammar copy.lark")

    ebnf_text = input_path.read_text(encoding="utf-8")
    lark_text = ebnf_to_lark(ebnf_text)
    output_path.write_text(lark_text, encoding="utf-8")
    print(f"✅ Converted `{input_path.name}` → `{output_path.name}`")

if __name__ == "__main__":
    main()
