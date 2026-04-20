```text
forml/
│
├── language/              # DSL pur (définition du langage)
│   ├── grammar/
│   │   ├── forml.ebnf
│   │   └── forml.lark
│   └── vocabulary/
│       ├── functions.py
│       ├── properties.py
│       ├── quantifiers.py
│       └── ...
│
├── parser/                # parsing brut (Lark → parse tree)
│   ├── parser.py
│   └── errors.py
│
├── ast/                   # structures AST (pur, sans logique métier)
│   ├── nodes/
│   │   ├── program.py
│   │   ├── property.py
│   │   ├── expressions.py
│   │   └── ...
│   └── utils.py
│
├── builder/               # parse tree → AST (ex-transformer)
│   ├── transformer.py
│   └── helpers.py
│
semantic/
│
├── validator.py          # entry point
├── property.py           # validation des propriétés
├── implication.py        # LHS/RHS split + règles FORML
├── logic.py              # AND/OR/NOT/Comparison
├── problem.py            # ProblemExpr validation
├── binding.py            # variables & scope (x0, etc.)
├── types.py              # compatibilité + typing léger
└── errors.py             # exceptions sémantiques
│
├── ir/                    # Intermediate Representations
│   ├── logical/           # IR niveau 1 (déclaratif)
│   │   ├── nodes.py
│   │   ├── predicates.py
│   │   └── quantifiers.py
│   │
│   ├── executable/        # IR niveau 2 (exécutable)
│   │   ├── program.py
│   │   ├── evaluator.py
│   │   └── operators.py
│   │
│   └── transforms/        # IR1 → IR2
│       └── lowering.py
│
├── backends/              # vérification formelle (TES vrais backends)
│   ├── base.py            # interface commune
│   ├── router.py          # sélection backend
│   │
│   ├── z3/                # ex: :contentReference[oaicite:0]{index=0}
│   │   ├── translator.py  # IR → contraintes
│   │   └── executor.py
│   │
│   ├── eran/
│   │   ├── translator.py
│   │   └── executor.py
│   │
│   └── ...
│
├── exploration/           # (OPTIONNEL / FUTUR)
│   ├── base.py
│   ├── router.py
│   │
│   ├── hypothesis_engine/ # ex: :contentReference[oaicite:1]{index=1}
│   │   ├── translator.py
│   │   └── executor.py
│   │
│   └── fuzzing_engine/
│
├── runtime/               # orchestration globale
│   ├── orchestrator.py
│   ├── pipeline.py
│   └── result.py
│
├── api/                   # interface utilisateur
│   ├── run.py
│   └── serializer/
│       └── to_forml.py
│
├── core/                  # utilitaires transverses (MINIMAL)
│   ├── types.py
│   ├── constants.py
│   └── utils.py

```