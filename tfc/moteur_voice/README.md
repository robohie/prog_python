# Moteur à commande vocale

Ce dossier contient le programme Arduino de reconnaissance vocale et de commande du moteur.

- `moteur_voice.ino` capture le son, calcule les caractéristiques Mel, lance l’inférence et applique les commandes reconnues.
- `model.h` contient le modèle embarqué.
- `mel_filterbank.h` contient les filtres Mel utilisés pour le prétraitement.

Le sketch cible une Arduino Nano 33 BLE Sense et s’appuie notamment sur PDM, CMSIS-DSP et MicroTFLite. Les paramètres audio, seuils et broches sont configurés dans le fichier `.ino`. Vérifiez le câblage et les bibliothèques nécessaires avant le téléversement.