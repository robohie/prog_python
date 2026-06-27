# prog_python

Description
-----------
prog_python est un "repository" conçu pour contenir tous les programmes informatiques codés en python liés à mon travail de fin de cycle(TFC). Ce travail est projet IoT de contrôle vocal d'un moteur DC(à aimant permanent et à balais, type EG- de Mabucchi Motor) que j'ai trouvé dans un vieux poste radio de mon père.

Dans ce projet, nous avons considérer trois grands systèmes qui se communiquent : le microcontrôleur et le modèle TinyML, le circuit de commande qui rélie le microcontrôleur au motor, le moteur et son alimentation. Le microcontrôleur est un arduino nano 33 ble sense rev2 qui comprend neuf capteurs intégrés dont un microphone numérique.

Table des matières
------------------
- [Description](#description)
- [Contenu du dépôt](#contenu-du-dépôt)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Tests](#tests)
- [Contribuer](#contribuer)
- [Licence](#licence)
- [Contact](#contact)
- [Remerciements](#remerciements)

Contenu du dépôt
----------------
Les fichiers principaux identifiés à la racine du dépôt sont :


Prérequis
---------
- Python 3.8+
- pip
- Recommandé : utiliser un environnement virtuel (`venv` ou `virtualenv`)

Installation
------------
1. Cloner le dépôt :
   git clone https://github.com/robohie/prog_python.git
2. Se placer dans le répertoire :
   cd prog_python
3. Créer et activer un environnement virtuel :
   python -m venv .venv
   - Linux / macOS : `source .venv/bin/activate`
   - Windows : `.venv\Scripts\activate`
4. Installer les dépendances

Utilisation
-----------
Les commandes suivantes sont des points d'entrée typiques ; adaptez-les selon la logique interne des scripts.

- Pour exécuter l'acquisition ADC :
  `python adc.py`

- Pour lancer le traitement de signaux (ex. pipelines, analyses) :
  `python human_signal.py`

- Pour exécuter le module de contrôle vocal :
  `python voice_controle.py`

Tests
-----
- Localisation des tests : `test_micro_ampli_filtre_adc.py` (à la racine)
- Objectifs :
  - Couvrir l'acquisition ADC, le filtrage et l'amplification critiques.
  - Fournir des fixtures pour simuler les entrées matérielles si nécessaire.

Contribuer
----------
Merci pour votre intérêt ! Processus recommandé :

1. Forkez le dépôt.
2. Créez une branche descriptive : `git checkout -b feat/ma-fonctionnalite`
3. Implémentez et testez votre changement.
4. Formatez le code et lancez les tests.
5. Ouvrez une Pull Request avec une description claire des changements et des instructions de reproduction.

Bonnes pratiques :
- Respectez PEP8 / les conventions établies.
- Ajoutez/maintiens des tests pour les nouvelles fonctionnalités ou corrections.
- Documentez les options des scripts via `--help` ou un fichier `docs/`.

Contact
-------
- Mainteneur principal : robohie — https://github.com/robohie  
- Pour les questions et contributions : ouvrez une issue sur ce dépôt.
- Mail : rogerbosolinndo34@gmail.com
- Téléphone : +243 82 24 60 896

Remerciements
-------------
- Ce README a été rédigé et adapté avec l'aide de GitHub Copilot (@copilot).
- Merci aux contributeurs passés et futurs.
