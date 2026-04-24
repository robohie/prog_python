# Importation des modules :
# 1. sounddevice pour l'enregistrement des sons issus du microphone de l'ordinateur
# 2. scipy.io.wavfile pour la lecture et l'écriture des fichiers enregistrement au format wav
# 3. numpy pour label_encoder calcul matriciel
# 4. os pour la gestion du système des fichiers
# 5. time pour la gestion du temps

import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
import os, time

FREQUENCE_ECHANTILLON = 16000    # Le signal sonore est échantillonné à 16 kHz
DUREE = 1                        # Chaque enregistrement dure 1 seconde, utile pour la conversion Mel
NOMBRE_CLIPS = 200               # Le nombre d'individus par échantillon ou classe
NOM_CLASSE = "bruit"             # La classe ou l'étiquette concernée
DOSSIER = f"sons/{NOM_CLASSE}"   # Le sous dossier du dossier "sons" contenant les enregistrements

os.makedirs(DOSSIER, exist_ok=True)
print(f"Enregistrement de {NOMBRE_CLIPS} clips pour la classe '{NOM_CLASSE}'")
print(f"({FREQUENCE_ECHANTILLON} Hz, 16 bits, mono, {DUREE}s)")
print('______________________________________________________________________\n')

time.sleep(1)

i = 0
while i < NOMBRE_CLIPS:
    print(f"Préparation pour l'échantillon [{i+1:03d}/{NOMBRE_CLIPS}]")
    # Compte à rebours
    for second in range(2, 0, -1):
        print(f"{second}...", end=" ", flush=True)
        time.sleep(0.6)
    print(f"PRONONCEZ LE MOT {NOM_CLASSE.upper()}!")
    enregistrement = sd.rec(
        int(DUREE*FREQUENCE_ECHANTILLON),
        samplerate=FREQUENCE_ECHANTILLON,
        channels=1
    )
    sd.wait() # Attend la fin de la second d'enregistrement

    # Vérification du volume
    volume = np.sqrt(np.mean(enregistrement**2)) * 1000
    if volume > 50 or NOM_CLASSE=="bruit":
        fichier = f"{DOSSIER}/{NOM_CLASSE}_{i+1:03d}.wav"
        wav.write(fichier, FREQUENCE_ECHANTILLON, enregistrement)
        print(f"{fichier} enregistré (volume moyen: {volume})")
        i+=1
    else:
        print(f"[ATTENTION] SON TROP FAIBLE (volume : {volume})! Recommence...")

print(f"\nEnregistrement terminé! {NOMBRE_CLIPS} clips sauvegardés dans {DOSSIER}")
