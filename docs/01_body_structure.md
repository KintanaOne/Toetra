# Body
Le body est composé de plusieurs **property**, toutes composé comme ceci :

```
├── property
│   │
│   ├── [ property_type ]                # Ex: [ROBUTNESS]
│   │
│   ├── ":"                             # Début du bloc de propriété
│   │
│   ├── property_expr                    # Expression de la propriété
│   │
│   │   ├── quantifier_expr (optionnel)        # Exemple : forall x in hyperball("L2", 0.01)
│   │   │   ├── "forall"
│   │   │   ├── identifier                     # x
│   │   │   └── quantifier_set
│   │   │       ├── hyperball | ball | noise
│   │   │       └── args
│   │   │           ├── arg_identifier_only | arg_identifier_eq | arg_number | arg_boolean
│   │   │           └── ... (liste d'arguments séparés par des virgules)
│   │   │
│   │   ├── anchor_expr (optionnel)            # Exemple : at pointA in ball("L2", 0.5)
│   │   │   ├── "at"
│   │   │   ├── identifier                     # pointA
│   │   │   ├── "in"
│   │   │   └── domain | quantifier_set
│   │   │       ├── domain
│   │   │       │   ├── "with"
│   │   │       │   ├── identifier             # variable
│   │   │       │   └── value_list
│   │   │       │       ├── value
│   │   │       │       └── ... (liste de valeurs)
│   │   │       └── quantifier_set
│   │   │           ├── hyperball | ball | noise
│   │   │           └── args
│   │   │               ├── arg_identifier_only | arg_identifier_eq | arg_number | arg_boolean
│   │   │               └── ... (liste d'arguments)
│   │   │
│   │   ├── check_expr (optionnel)             # Exemple : check_at x0
│   │   │   ├── "check_at"
│   │   │   └── identifier                     # x0
│   │   │
│   │   └── pairwise_expr (optionnel)          # Exemple : x1 ~ x2 with distance(x1,x2,0.5)
│   │       ├── identifier                     # x1
│   │       ├── "~"
│   │       ├── identifier                     # x2
│   │       ├── "with"
│   │       └── symbolic_distance
│   │           ├── "distance("
│   │           ├── identifier                 # x1
│   │           ├── ","
│   │           ├── identifier                 # x2
│   │           ├── ","
│   │           └── value                      # 0.5
│   │
│   ├── "->"                                # Séparateur entre propriété et assertion
│   │
│   ├── assertion
│   │   ├── logic_expr                        # Exemple : CLASSIFICATION.EQUAL()
│   │   │   ├── CLASSIFICATION | PREDICTION | ...
│   │   │   └── function_expr
│   │   │       ├── function                 # EQUAL, EQUITY, BETWEEN, INCREASING
│   │   │       └── args (optionnels)
│   │   │
│   │   └── logic_assertion (forme alternative)
│   │       ├── "(" condition "->" consequence ")"
│   │       └── logic_term (AND/OR)
│   │
│   └── abstractor (optionnel)                # Exemple : using ERAN("zonotope")
│       ├── "using"
│       ├── backend                          # ERAN, Z3, Zonotope, etc.
│       └── args (optionnels)
```