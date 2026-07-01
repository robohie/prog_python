<p align="center">
  <img src="rapports/figures/unikin_logo.PNG" alt="Logo de l'Université" width="220" />
</p>

# prog_python

Prog_Python — Système IoT de contrôle vocal pour moteur (Travail de Fin de Cycle)

Résumé
------
Ce dépôt contient le code, les notebooks et les documents associés au projet de fin de cycle portant sur la conception et l'évaluation d'un système IoT de contrôle vocal pour moteur. Le README a été aligné sur l'état réel du dépôt : il liste les fichiers et dossiers présents, indique comment reproduire les parties actives, et donne des exemples d'utilisation pratiques.

Contenu et architecture (état actuel)
------------------------------------
- pretraitement/
  - `extraction_mfcc.py` — outils d'extraction de MFCC et prétraitement audio
- c_model/
  - `CNN1_quantifie.cc` — code C/C++ généré du modèle quantifié (TinyML)
- models/
  - `models_non_quantifies/` et `models_quantifies/` — emplacements destinés aux modèles
- lt_spice/
  - simulations et documentation pour le circuit (fichiers `.asc`, `.asy`, PDF)
- rapports/figures/
  - images et figures utilisées dans le rapport (`unikin_logo.PNG`, etc.)
- Schéma_Kicad/, simul_ide/, test_circuit_commande/ — dossiers liés au matériel et aux simulations
- `tfc_train_model_Bosolindo.ipynb` — notebook principal d'entraînement / expérimentation
- `verification_model.py` — script utilitaire pour évaluer des modèles TFLite
- `requirements.txt` — dépendances Python

Remarque importante :
- Les références à des chemins/fichiers inexistants (ex. `src/`, `firmware/`, `tests/`, et certains scripts cités dans l'ancienne version du README) ont été retirées pour éviter toute confusion. Si vous avez une copie de ces fichiers à réintégrer, dites‑le et je mettrai le README à jour.

Comment reproduire (rapide)
---------------------------
1. Cloner le dépôt :

```bash
git clone https://github.com/robohie/prog_python.git
cd prog_python
```

2. Créer un environnement virtuel et installer les dépendances :

```bash
python -m venv .venv
# Linux / macOS
source .venv/bin/activate
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
```

3. Ouvrir et exécuter les notebooks :
- Lancer Jupyter / JupyterLab et ouvrir `tfc_train_model_Bosolindo.ipynb` pour reproduire l'entraînement et l'analyse.

4. Script d'évaluation / vérification :
- `verification_model.py` fournit deux fonctions (pour modèles non quantifiés et quantifiés). Voir la section suivante pour un exemple d'utilisation et les attentes sur le format des données.

Utilisation détaillée de verification_model.py
---------------------------------------------
Le script `verification_model.py` expose actuellement deux fonctions : `verification1(model_path, x_test, y_test)` pour modèles non quantifiés et `verification2(model_q_path, x_test, y_test)` pour modèles quantifiés.

Formats attendus
- x_test : numpy array de formes `(N, ...)` correspondant à la forme d'entrée du modèle. Les valeurs doivent être float32 pour les modèles non quantifiés.
- y_test : labels correspondants. Le code actuel compare `argmax` des sorties et des étiquettes — cela signifie que `y_test` doit être au format one-hot (vecteurs de probabilités/0-1) ou transformable en argmax. Si vous avez des indices de classes entières (0..C-1), convertissez avec `tf.keras.utils.to_categorical(y_indices, num_classes)`.

Exemple d'usage (depuis un notebook ou script) :

```python
import numpy as np
from verification_model import verification1, verification2

# charger/définir vos données de test
x_test = np.load('data/x_test.npy')            # shape (N, ...) dtype float32
y_test = np.load('data/y_test_onehot.npy')    # shape (N, num_classes)

# évaluer un modèle tflite non quantifié
model_path = 'models/models_non_quantifies/my_model.tflite'
acc = verification1(model_path, x_test, y_test)
print(f'Accuracy (float model): {acc:.2%}')

# évaluer un modèle tflite quantifié
model_q_path = 'models/models_quantifies/my_model_quant.tflite'
acc_q = verification2(model_q_path, x_test, y_test)
print(f'Accuracy (quantized model): {acc_q:.2%}')
```

Notes et recommandations sur verification_model.py
-------------------------------------------------
Pendant la relecture du script, j'ai relevé quelques points d'amélioration (non appliqués automatiquement ici) qui rendent l'utilisation plus robuste :

1) Boucle d'itération
- Le code actuel itère `for value in x_test:` puis utilise `x_test.index(value)` pour récupérer l'étiquette correspondante. Si `x_test` est un numpy array, `list.index` n'existe et la correspondance échouera. Recommandation : itérer avec un index `for i, value in enumerate(x_test):` et utiliser `y_test[i]`.

2) Conversion dtype
- `value.astype(np.float32)` ne modifie pas `value` en place. Utiliser `value = value.astype(np.float32)` ou caster lors du `set_tensor`.

3) Affichages & f-strings
- Quelques f-strings utilisent des guillemets doubles imbriqués et des variables mal référencées (ex. réutilisation de `input_zp` pour l'affichage de la sortie). Il faudra corriger ces lignes pour éviter des erreurs de syntaxe et afficher les bons paramètres.

4) Gestion des formes d'entrée
- Assurez-vous que la forme de chaque entrée correspond à `input_details[0]['shape']`. Il est fréquent de devoir appliquer `np.expand_dims(value, 0)` ou reshaper à `(1, ...)` avant `set_tensor`.

Si vous le souhaitez, je peux proposer et appliquer un correctif (patch) pour `verification_model.py` qui implémente ces améliorations et fournit des logs plus clairs. Voulez‑vous que je :
- (A) applique uniquement les améliorations au README (comme ici),
- (B) applique en plus un patch correctif automatique au fichier `verification_model.py`, ou
- (C) crée une branche avec le patch et une PR pour revue avant fusion ?

Bonnes pratiques et contribution
--------------------------------
- Documentez, à l'avenir, l'emplacement exact des modèles TFLite finaux (par ex. `models/models_quantifies/your_model.tflite`) afin que les scripts puissent référencer des chemins stables.
- Ajouter des tests unitaires (ex. dossier `tests/`) qui valident le pipeline de prétraitement et l'inférence sur un petit jeu de données de raison.
- Si vous ciblez une MCU spécifique, créez une arborescence `firmware/` avec un README (toolchain, flash steps) pour faciliter la reprise par d'autres.

Licence et contact
------------------
- Licence : ajoutez le fichier `LICENSE` si vous souhaitez une licence explicite (ex. MIT).
- Mainteneur : robohie — https://github.com/robohie
- Courriel : rogerbosolinndo34@gmail.com

---

Si vous validez, j'appliquerai maintenant :
- soit (A) aucune modification supplémentaire, ou
- soit (B) le patch automatique recommandé pour `verification_model.py`, ou
- soit (C) créer une branche et ouvrir une PR contenant le README affiné + le patch proposé pour `verification_model.py`.
