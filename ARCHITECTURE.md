# 🧱 FORML Project Architecture

This document provides an overview of the internal structure of the FORML DSL project.

FORML is built to be **modular**, **maintainable**, and **extensible** — separating the parsing logic, the abstract syntax tree (AST), and integration with external formal verification libraries.

---

## 📁 Directory Structure
```
forml/
├── forml/
│   ├── __init__.py
│   ├── grammar/
│   │   ├── forml_grammar.ebnf           # Grammaire EBNF du DSL (version source)
│   │   ├── forml_grammar.lark           # Fichier pour Lark (parser prêt à l’emploi)
│   │   └── lark_generator.py            # generator de fichier .lark
│   ├── parser/
│   │   ├── __init__.py
│   │   ├── parser.py            # Lark parser (chargement de la grammaire)
│   │   └── transformer.py       # Transformer → AST → objets Python
│   ├── ast/
│   │   ├── __init__.py
│   │   ├── base.py              # Classe de base pour les nœuds d’AST
│   │   ├── properties.py        # Représentation Python des propriétés FORML
│   │   ├── expressions.py       # Éléments logiques, expressions conditionnelles
│   │   └── utils.py             # Fonctions utilitaires de parsing/validation
│   └── examples/
│       ├── bound_example.forml        # Exemple de fichier FORML
│       ├── fairness_example.forml        # Exemple de fichier FORML
│       ├── logic_example.forml        # Exemple de fichier FORML
│       ├── monotonicity_example.forml        # Exemple de fichier FORML
│       ├── stability_example.forml        # Exemple de fichier FORML
│       └── ROBUSTNESS_example.forml        # Exemple de fichier FORML
├── tests/
│   ├── test_parser.py           # Tests unitaires du parser
│   ├── test_transformer.py      # Tests des objets générés
│   └── test_properties.py       # Validation logique des propriétés
├── README.md                    # Documentation complète
├── LICENSE                      # MIT ou autre
├── pyproject.toml               # Déclaration du projet Python
└── setup.cfg / setup.py         # Setup d’installation
```

## 🧩 Component Descriptions

| Path / File                         | Description |
|------------------------------------|-------------|
| `forml/`                           | Main Python package for the DSL |
| `forml/grammar/forml.ebnf`         | Clean, human-readable version of the grammar in EBNF |
| `forml/grammar/forml.lark`         | Lark-compatible grammar used by the parser |
| `forml/parser/parser.py`           | Loads and runs the Lark parser over `.forml` input |
| `forml/parser/transformer.py`      | Transforms parse trees into structured Python objects |
| `forml/ast/base.py`                | Base classes for AST node structure |
| `forml/ast/properties.py`          | Classes representing formal properties (Robustness, Fairness, etc.) |
| `forml/ast/expressions.py`         | Encodes logical and numerical expressions within properties |
| `forml/ast/utils.py`               | Utility functions (e.g., validation, normalization) |
| `forml/examples/example.forml`     | Example file showing DSL syntax |
| `tests/`                           | Tests to ensure parsing and transformation are correct |
| `README.md`                        | Overview of the DSL and how to use it |
| `ARCHITECTURE.md`                  | Explanation of the file structure and responsibilities |
| `pyproject.toml`                   | Declares project dependencies and metadata |
| `setup.cfg`, `setup.py`            | Standard setup configuration for Python packaging |

---

## 🔧 Extension Ideas (Future Work)

- `forml/backend/` → Optional subpackage to interface directly with tools like ERAN, Z3, Marabou
- `forml/vscode/` → Codegen and assets for a VS Code syntax plugin
- `forml/cli.py` → Command-line interface for parsing `.forml` files and verifying properties

---

## 📌 Notes

- This project is structured to **separate concerns**: grammar, parsing, transformation, logic.
- DSL properties are transformed into **clean Python objects**, enabling further analysis and connection to verification backends.
- The `formal_ml` library will handle the verification phase — this repo focuses on defining, parsing, and validating properties.

---

FORML is designed to make formal methods accessible to ML practitioners without sacrificing rigor.

