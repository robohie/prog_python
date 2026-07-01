<p align="center">
  <img src="rapports/figures/unikin_logo.PNG" alt="Logo de l'Université" width="220" />
</p>

# prog_python

Prog_Python — Système IoT de contrôle vocal pour moteur (Travail de Fin de Cycle)

> README rédigé par GitHub Copilot (@copilot)

Résumé (Abstract)
-----------------
Ce dépôt contient l'ensemble des codes, notebooks et documents associés au projet de fin de cycle portant sur la conception d'un système IoT de contrôle vocal d'un moteur. Le projet intègre trois sous-systèmes principaux :

1) un microcontrôleur embarqué exécutant un modèle TinyML pour la détection de commandes vocales,
2) un circuit de commande reliant le microcontrôleur au moteur (driver / commande de puissance),
3) le moteur pilote et ses interfaces.

Ce document décrit l'architecture, l'installation, l'utilisation, les protocoles d'évaluation et les bonnes pratiques de contribution, afin d'assurer la reproductibilité et la vérifiabilité scientifique du travail.

Contexte et objectifs
---------------------
Objectifs scientifiques et techniques :

- Concevoir et implémenter un pipeline de traitement audio embarqué capable de reconnaître des commandes vocales simples via TinyML.
- Développer l'interface matérielle (circuit de commande) pour piloter un moteur DC ou pas-à-pas en toute sécurité.
- Évaluer la robustesse du système en conditions réelles (bruit, variations d'alimentation, latence).
- Documenter les méthodes expérimentales, les résultats et les procédures de reproduction permettant une évaluation académique rigoureuse.

Contributions principales
-------------------------
- Code embarqué et hôte pour acquisition ADC, filtrage et amplification du signal analogique.
- Pipelines de traitement du signal audio et notebooks d'analyse (prétraitement, extraction de caractéristiques, tests).
- Intégration d'un modèle TinyML pour classification de commandes vocales et exemples d'export/quantification.
- Scripts d'évaluation et tests unitaires / fixtures pour simuler l'entrée matérielle.
- Documentation et artefacts de recherche (notebooks, rapports LaTeX).

Architecture du projet
----------------------
- Acquisition et prétraitement : lecture ADC, filtrage, amplification — scripts Python (`src/adc.py`, `src/human_signal.py`).
- Modélisation : notebooks Jupyter pour exploration et entraînement (réduction de dimension, extraction MFCC, etc.).
- TinyML : conversion du modèle entraîné en format compatible microcontrôleur (TFLite, quantification).
- Interface matérielle : code C++ pour microcontrôleur (contrôle PWM, GPIO, protocole de communication série/I2C/SPI) dans `firmware/`.
- Tests et validation : tests unitaires et scripts de simulation (ex. `tests/test_micro_ampli_filtre_adc.py`).

Contenu du dépôt (aperçu)
-------------------------
- notebooks/           — Notebooks Jupyter d'analyse et d'entraînement
- firmware/            — Code C++ pour microcontrôleur (drivers, main)
- src/                 — Scripts Python (acquisition, traitement, inférence)
- tests/               — Tests unitaires et fixtures
- docs/                — Documentation additionnelle et procédés expérimentaux
- thesis/              — Sources LaTeX du rapport (TFC)
- rapports/            — Figures et rapports (logo universitaire : `rapports/figures/unikin_logo.PNG`)
- README.md            — Ce fichier
- requirements.txt     — Liste des dépendances Python (si présente)

Prérequis
---------
- Matériel :
  - Microcontrôleur compatible (ex : STM32, ESP32, ou équivalent) avec ADC et capacités d'exécution TinyML.
  - Module d'acquisition audio / préamplificateur et moteur (DC / stepper) avec driver de puissance.
- Logiciel :
  - Python 3.8+
  - pip
  - Outils pour TinyML (TensorFlow, TFLite Converter) installés selon besoins
  - Outils de compilation pour firmware (toolchain ARM ou ESP-IDF selon la cible)
- Recommandé : utilisation d'un environnement virtuel (venv, virtualenv, conda)

Installation
------------
1. Cloner le dépôt :
   git clone https://github.com/robohie/prog_python.git
2. Se placer dans le répertoire :
   cd prog_python
3. Créer et activer un environnement virtuel :
   python -m venv .venv
   - Linux / macOS : source .venv/bin/activate
   - Windows : .venv\Scripts\activate
4. Installer les dépendances Python (si `requirements.txt` est présent) :
   pip install -r requirements.txt
5. Pour le firmware, configurer la toolchain et flasher la cible selon les instructions dans `firmware/README.md` (si disponible).

Utilisation (exemples)
----------------------
- Acquisition ADC :
  python src/adc.py --config config/adc_config.yaml

- Traitement du signal / pipelines d'analyse :
  python src/human_signal.py --input data/raw --output data/processed

- Module de contrôle vocal / inférence (hôte) :
  python src/voice_controle.py --model models/tflite/command_model.tflite

- Exemples & notebooks :
  Ouvrir les notebooks dans `notebooks/` pour reproduire les expériences (Jupyter / JupyterLab)

Reproductibilité des expériences
-------------------------------
Pour reproduire les protocoles expérimentaux décrits dans le TFC :

1. Prétraiter les données en suivant `notebooks/01_preprocessing.ipynb`.
2. Exécuter l'entraînement avec `notebooks/02_training.ipynb` ou via le script dédié (`src/train.py` si présent).
3. Exporter et quantifier le modèle en TFLite (notebook ou script d'export dans `src/`).
4. Flasher le firmware et transférer le modèle quantifié sur la cible.
5. Lancer les protocoles d'évaluation décrits dans `docs/experiments.md` (séquences de tests, métriques, conditions).

Évaluation et métriques
----------------------
Les métriques recommandées :
- Précision, rappel, F1-score par classe de commande (sur jeu de test).
- Matrice de confusion pour analyser erreurs inter-classes.
- Latence d'inférence (ms) mesurée sur cible.
- Consommation énergétique (mA) en mode veille vs inférence.
- Robustesse au bruit : tests SNR décroissant.

Tests
-----
- Emplacement des tests : `tests/` (ex. `tests/test_micro_ampli_filtre_adc.py`)
- Exécuter les tests unitaires :
  python -m pytest tests/ -q
- Les tests incluent des fixtures pour simuler entrées matérielles (ADC) et valider les algorithmes de filtrage/amplification.

Bonnes pratiques de développement
--------------------------------
- Respecter les conventions PEP8 pour les fichiers Python.
- Documenter les APIs et options de scripts avec argparse (`--help`).
- Ajouter des tests pour toute nouvelle fonctionnalité ou correction.
- Versionner les modèles (ex. `models/v1`, `models/v2`) et conserver les notebooks d'entraînement.

Guide de contribution
---------------------
1. Forkez le dépôt.
2. Créez une branche descriptive : git checkout -b feat/ma-fonctionnalite
3. Implémentez et testez vos modifications.
4. Assurez-vous que les tests passent et que la documentation est à jour.
5. Ouvrez une Pull Request en décrivant clairement :
   - L'objectif des changements
   - Les étapes pour reproduire
   - L'impact sur l'architecture et les performances

Licence
-------
Indiquer la licence appropriée (ex. MIT, CC-BY, ou autre). Si aucune licence n'est fournie, le dépôt reste propriétaire. Voir le fichier `LICENSE` pour les détails.

Contact
-------
- Mainteneur principal : robohie — https://github.com/robohie  
- Courriel : rogerbosolinndo34@gmail.com
- Pour toute question, ouvrir une issue sur ce dépôt.

Remerciements et références
---------------------------
- Ce projet a été réalisé dans le cadre d'un travail de fin de cycle (TFC). Si vous utilisez ou citez ce travail, merci d'indiquer la référence suivante (exemple BibTeX à adapter) :

```bibtex
@techreport{robohie2026_tfc,
  title = {Système IoT de contrôle vocal d'un moteur},
  author = {Roger Bosolo Ndo},
  year = {2026},
  institution = {Université / École},
  note = {Travail de fin de cycle}
}
```

Notes finales
-------------
- Ce README est conçu pour être un document vivant : mettez-le à jour au fur et à mesure de l'évolution du projet (résultats, modèles, scripts).
- J'ai inséré le logo universitaire disponible dans `rapports/figures/unikin_logo.PNG` et ajouté la mention de rédaction par GitHub Copilot (@copilot).

