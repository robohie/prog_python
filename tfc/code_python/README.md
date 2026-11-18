# Code Python

Ce dossier rassemble les scripts Python du projet : définition du réseau de neurones, entraînement, vérification et export de caractéristiques audio.

- `models.py` définit le modèle convolutif.
- `entrainement.py` fournit les fonctions d’entraînement, de visualisation des courbes et de conversion TensorFlow Lite.
- `verification_model.py` sert à vérifier un modèle.
- `pretraitement/` contient les traitements audio.
- `export_mel_filterbank.py` prépare l’export des filtres Mel pour le code embarqué.

Les dépendances sont listées dans [`../requirements.txt`](../requirements.txt).