<p align="center">
  <img src="rapports/figures/unikin_logo.PNG" alt="Logo de l'Université" width="220" />
</p>

# prog_python

Prog_Python — Système IoT de contrôle vocal pour moteur (Travail de Fin de Cycle)

Résumé
------
Ce dépôt contient le code, les notebooks et les documents associés au projet de fin de cycle portant sur la conception et l'évaluation d'un système IoT de contrôle vocal pour moteur. Le contenu présent dans le dépôt a été vérifié et la structure suivante reflète l'état actuel des fichiers.

Principaux composants présents dans ce dépôt
-------------------------------------------
- Prétraitement et extraction de caractéristiques : `pretraitement/extraction_mfcc.py`
- Notebooks d'entraînement / exploration : `tfc_train_model_Bosolindo.ipynb` (notebook principal d'entraînement)
- Vérification / scripts utilitaires : `verification_model.py`
- Modèles : `models/models_non_quantifies/` et `models/models_quantifies/` (répertoires pour stocker modèles)
- Code C/C++ généré pour TinyML : `c_model/CNN1_quantifie.cc`
- Schémas et documents de simulation circuit : `lt_spice/` (fichiers .asc, .asy, PDF)
- Rapports et figures (incluant le logo) : `rapports/figures/` (ex. `unikin_logo.PNG`, images d'analyse)
- Fichier de dépendances Python : `requirements.txt`
- Divers dossiers projet liés au matériel et simulations : `Schéma_Kicad/`, `simul_ide/`, `test_circuit_commande/`

Remarques importantes sur la cohérence du dépôt
-----------------------------------------------
- J'ai enlevé les références à des chemins qui n'existent plus dans ce dépôt (par exemple `src/`, `firmware/`, `tests/`, ou certains scripts cités dans la version précédente du README). Le README précédent mentionnait des fichiers/scripts (`src/adc.py`, `src/human_signal.py`, `src/voice_controle.py`, `tests/test_micro_ampli_filtre_adc.py`) qui ne sont pas présents actuellement ; ils ont été retirés pour éviter toute confusion.
- Si vous souhaitez réintroduire ces modules (par exemple déplacement depuis un autre emplacement ou réécriture), indiquez où se trouvent les sources et je mettrai le README à jour pour pointer vers les bons fichiers.

Architecture et rôle des répertoires (aperçu)
---------------------------------------------
```
pretraitement/                 extraction MFCC et utilitaires Python
c_model/                       code C/C++ du modèle quantifié (ex: CNN1_quantifie.cc)
models/                        dossiers pour modèles non quantifiés et quantifiés
lt_spice/                      simulations LTspice et documentation associée (PDF, .asc)
rapports/figures/              figures et images (logo, schémas)
Schéma_Kicad/                  fichiers de schéma KiCad (s'il y en a)
simul_ide/                     scripts/simulations pour IDEs ou simulateurs
test_circuit_commande/         fichiers et notes pour tests du circuit de commande
tfc_train_model_Bosolindo.ipynb notebook principal d'entraînement/expérimentation
verification_model.py          script utilitaire pour vérification de modèle
requirements.txt               dépendances Python listées ici
```

Comment exécuter / reproduire les parties actives
-------------------------------------------------
1. Cloner le dépôt :
   git clone https://github.com/robohie/prog_python.git
   cd prog_python

2. Installer les dépendances Python (recommandé dans un environnement virtuel) :
   python -m venv .venv
   # Linux / macOS
   source .venv/bin/activate
   # Windows
   .venv\Scripts\activate
   pip install -r requirements.txt

3. Notebooks :
   - Ouvrir `tfc_train_model_Bosolindo.ipynb` dans Jupyter / JupyterLab pour reproduire l'entraînement et l'analyse.

4. Scripts :
   - Vérifier le modèle (exemple) :
     python verification_model.py

5. Modèles C/C++ (TinyML) :
   - Le fichier `c_model/CNN1_quantifie.cc` contient la version C++/C du modèle quantifié ; intégrer/adapter selon la cible embarquée.

Points à compléter / suggestions
--------------------------------
- Si vous utilisez une cible microcontrôleur (STM32, ESP32, etc.), ajoutez ici un dossier `firmware/` contenant le code embarqué et des instructions de flash. Actuellement le dépôt ne contient pas de dossier `firmware/`.
- Si des tests unitaires existent ailleurs, ajoutez un dossier `tests/` et mettez un exemple d'exécution `pytest`.
- Documenter l'emplacement exact des modèles TFLite quantifiés si vous souhaitez conserver des chemins d'exécution automatiques (ex. `models/models_quantifies/your_model.tflite`).

Licence et contact
------------------
- Licence : ajouter/indiquer la licence choisie dans le fichier `LICENSE` (si absent, préciser la licence désirée).
- Mainteneur : robohie — https://github.com/robohie  
- Courriel : rogerbosolinndo34@gmail.com

Historique des ajustements
--------------------------
- Ce README met à jour les chemins et la description pour refléter les fichiers réellement présents dans le dépôt au moment de la vérification.
- Références supprimées : `src/` (scripts cités), `firmware/` et `tests/` — ces éléments n'ont pas été trouvés et ont été retirés de la documentation pour éviter des erreurs.

Merci — si vous souhaitez, je peux :
- appliquer ce README directement sur la branche (préparer le commit),
- ou bien l'adapter davantage (ajouter exemples détaillés d'usage pour `verification_model.py`, ou checklist pour déployer sur cible embarquée).
