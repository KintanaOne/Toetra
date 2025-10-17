# Header
Le head est l'en-tête du .forml dont voici la structure :

```
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
```
