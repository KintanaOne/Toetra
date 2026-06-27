```text
test/
│
├── parsing/                  # 🔤 Parser Lark (syntaxe → AST)
│   ├── test_header.py
│   ├── test_body.py
│   ├── test_pairwise.py
│   ├── test_check_at.py
│   ├── test_forall.py
│   ├── test_logic.py        # 🔥 important maintenant
│   └── test_errors.py       # ❌ inputs invalides
│
├── transformer/             # 🔁 AST → objets Python
│   ├── test_property.py
│   ├── test_assertion.py
│   ├── test_logic_tree.py
│   └── test_pairwise.py
│
├── ir/                      # 🧠 IR logique
│   ├── test_logic_normalization.py   # CNF / DNF plus tard
│   ├── test_semantics.py            # A -> B == NOT A OR B
│   └── test_constraints.py
│
├── integration/             # 🔗 end-to-end
│   ├── test_full_pipeline.py
│   └── test_real_examples.py
│
├── property_based/          # 🔥 génération automatique
│   ├── test_fuzz_parser.py
│   ├── test_fuzz_transformer.py
│   └── strategies.py        # générateurs Hypothesis
│
├── fixtures/                # 📁 fichiers FORML exemples
│   ├── valid/
│   │   ├── robustness_pairwise.forml
│   │   ├── check_at.forml
│   │   └── logic.forml
│   │
│   └── invalid/
│       ├── missing_arrow.forml
│       ├── bad_token.forml
│       └── invalid_logic.forml
│
└── utils/
    ├── parser_utils.py
    └── assert_utils.py

```