# Program
## Info
- \* : répété zéro ou plusieurs fois
- ? : optionnel
- Chaque bloc est détaillé pour montrer comment header, body et footer s’emboîtent
- property_expr est détaillé pour chaque type d’expression (quantifier_expr, anchor_expr, check_expr, pairwise_expr)

## Structure
Arbre syntaxique complet d’un fichier .forml :

```forml
program
│
├── header
│   │
│   ├── comment*                       # Commentaires optionnels
│   │   └── "#" suivi de texte
│   │
│   ├── target_declaration?             # Déclaration optionnelle de la colonne cible
│   │   ├── "target"
│   │   ├── ":="
│   │   └── identifier                 # Nom de la colonne cible
│   │
│   └── model_declaration?              # Déclaration optionnelle du modèle
│       ├── "model"
│       ├── ":="
│       └── quoted_identifier          # Chemin vers le modèle (ex: "/path/to/model.onnx")
│
├── body
│   │
│   ├── section+                        # Une ou plusieurs sections
│   │   │
│   │   ├── comment?                    # Commentaire optionnel avant la section
│   │   │
│   │   ├── declaration_section?        # Exemple : variable := value
│   │   │   ├── identifier
│   │   │   ├── ":="
│   │   │   └── value
│   │   │
│   │   └── property_section?           # Section de propriété
│   │       ├── property
│   │       │   ├── [ property_type ]
│   │       │   ├── ":"
│   │       │   ├── property_expr
│   │       │   │   ├── quantifier_expr (optionnel)
│   │       │   │   │   ├── "forall"
│   │       │   │   │   ├── identifier
│   │       │   │   │   └── quantifier_set
│   │       │   │   │       ├── hyperball | ball | noise
│   │       │   │   │       └── args
│   │       │   │   │           ├── arg_identifier_only | arg_identifier_eq | arg_number | arg_boolean
│   │       │   │   │           └── ...
│   │       │   │   ├── anchor_expr (optionnel)
│   │       │   │   │   ├── "at"
│   │       │   │   │   ├── identifier
│   │       │   │   │   ├── "in"
│   │       │   │   │   └── domain | quantifier_set
│   │       │   │   ├── check_expr (optionnel)
│   │       │   │   └── pairwise_expr (optionnel)
│   │       │   ├── "->"
│   │       │   ├── assertion
│   │       │   │   ├── logic_expr
│   │       │   │   │   ├── CLASSIFICATION | PREDICTION | ...
│   │       │   │   │   └── function_expr
│   │       │   │   │       ├── function (EQUAL, EQUITY, BETWEEN, INCREASING)
│   │       │   │   │       └── args (optionnels)
│   │       │   │   └── logic_assertion (alternative)
│   │       │   │       ├── "(" condition "->" consequence ")"
│   │       │   │       └── logic_term (AND/OR)
│   │       │   └── abstractor?          # using ERAN("zonotope")
│   │       └── SEPARATORS
│
└── footer
    └── comment*                        # Commentaires optionnels, notes ou métadonnées

```