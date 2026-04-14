# HYPOTHESIS

## Architecture

```text
tests/
│
├── unit/                      # déjà fait
│
├── hypothesis/
│   ├── test_parser.py        # tests principaux
│   ├── test_roundtrip.py     # parse → serialize → parse
│
│   ├── strategies/
│   │   ├── __init__.py
│   │   ├── primitives.py     # tokens simples
│   │   ├── identifiers.py    # noms valides FORML
│   │   ├── model.py          # model declaration
│   │   ├── target.py         # target
│   │   ├── properties.py     # propriétés
│   │   ├── program.py        # programme complet
│   │
│   ├── utils/
│   │   ├── serialize.py
│   │   ├── compare_ast.py
│   │
│   └── settings.py           # config hypothesis
```