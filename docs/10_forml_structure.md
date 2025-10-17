# .forml file structure
Un fichier .forml décrit un ensemble de propriétés formelles à vérifier sur un modèle de Machine Learning ou Deep Learning.
Il est structuré en trois sections principales :
- header
- body
- footer

Chaque section a un rôle bien défini.

## 1. header
Le header constitue le point d’entrée du fichier .forml.
Il peut contenir plusieurs déclarations optionnelles permettant de contextualiser le script.
### Contenu
#### Déclaration de la cible (target)
```forml
target := MyTargetColumn
```
#### Déclaration du modèle (optionnelle)
Spécifie le chemin vers le modèle ML/DL au format ONNX à vérifier.
```forml
model := "/path/to/model.onnx"
```
#### Commentaires
Des commentaires peuvent être placés n’importe où dans le fichier.
```forml
# Script de vérification de robustesse
# Auteur : KintanaOne.
```
## 2. body
- Le body contient les propriétés à vérifier.
- Chaque propriété est définie dans une section introduite par un tag entre crochets ([PROPERTY_TYPE]).
### Structure d’une section
```forml
# (commentaire facultatif)
[PROPERTY_TYPE]:
PROPERTY_EXPRESSION -> ASSERTION;
```
#### Exemple minimal
```forml
# Vérification de robustesse locale
[ROBUTNESS]:
forall x in hyperball("L2", 0.01) -> CLASSIFICATION.EQUAL();
```
### Composants
#### Type de propriété :
Le mot entre crochets détermine la nature de la propriété :
- ROBUTNESS
- STABILITY
- FAIRNESS
- MONOTONICITY
- BOUND
- LOGIC
- ou tout type défini en majuscules ([CUSTOM_PROPERTY])

#### Expression de propriété :
Elle définit le contexte d’évaluation.
Plusieurs formes sont possibles selon la nature du test :
| Expression                     | Description                                 | Exemple                             |
| ------------------------------ | ------------------------------------------- | ----------------------------------- |
| `forall x in <set>`            | Quantificateur universel                    | `forall x in hyperball("L2", 0.01)` |
| `at <anchor> in <domain>`      | Vérifie une propriété à un point donné      | `at pointA in ball("L2", 0.5)`      |
| `check_at <anchor>`            | Vérifie une condition à un point spécifique | `check_at x0`                       |
| `<a> ~ <b> with distance(...)` | Vérifie une propriété pairwise              | `x1 ~ x2 with distance(x1,x2,0.5)`  |

#### Assertion
Elle définit ce que la propriété doit vérifier sur le modèle.
Il s’agit d’une expression logique ou fonctionnelle.

##### example
- CLASSIFICATION.EQUAL();
- CLASSIFICATION.EQUITY("group");
- REGRESSION.INCREASING("feature_x");

ou sous forme logique :
```forml
(temp < 0.1) -> (predicted_class == "safe")
```

#### Abstractor
Permet de spécifier le backend de vérification (ex. ERAN, Z3, Zonotope…).
```forml
using ERAN("zonotope", "timeout"=60)
```
## 3. footer
Le footer est facultatif.
Il peut contenir des commentaires généraux, des notes d’expérimentation ou des métadonnées.
```forml 
# Fin du script
'''
Très
long
commentaire
'''
# Vérifié le 15/10/2025 avec backend Z3
```

## Example :
```forml
# Test de robustesse simple
target := MyTargetColumn

[ROBUTNESS]:
forall x in hyperball("L2", 0.01) -> CLASSIFICATION.EQUAL();
using ERAN("zonotope")

# Fin du fichier
```