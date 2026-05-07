# Ce module sert à acquérir des échantillons des sons.
# Nécessaire pour résoudre notre type de problème (détection des mots clés).

import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
import os, time

FREQUENCE_ECHANTILLON = 16000    # Le signal sonore est échantillonné à 16 kHz (comme sur Arduino)
DUREE = 1                        # Chaque enregistrement dure une seconde (utile pour la conversion Mel).
NOMBRE_CLIPS = 200               # Le nombre d'individus par échantillon ou classe (on a sept classes).
NOM_CLASSE = "essai"             # La classe ou l'étiquette concernée
DOSSIER = f"sons/{NOM_CLASSE}"   # Le sous dossier du dossier "sons" contenant les enregistrements

os.makedirs(DOSSIER, exist_ok=True)
titre = f"***  Enregistrement de {NOMBRE_CLIPS} clips pour la classe '{NOM_CLASSE}'  ***".upper()

print(f"{"*" * len(titre)}")
print(titre)
print(f"{"*" * len(titre)}")

print(f'{FREQUENCE_ECHANTILLON} Hz, 16 bits, mono, {DUREE}s')

time.sleep(1)

compteur = 0
while compteur < NOMBRE_CLIPS:
    print(f"Préparation pour l'échantillon [{compteur + 1:03d}/{NOMBRE_CLIPS}]")
    # Compte à rebours
    for second in range(2, 0, -1):
        print(f"{second}...", end=" ", flush=True)
        time.sleep(0.8)

    print(f"Prononcez le mot {NOM_CLASSE.upper()}!")
    enregistrement = sd.rec(
        int(DUREE*FREQUENCE_ECHANTILLON),
        samplerate=FREQUENCE_ECHANTILLON,
        channels=1
    )
    sd.wait() # Attend la fin de la seconde d'enregistrement

    # Vérification du volume
    volume = np.sqrt(np.mean(enregistrement**2)) * 1000
    if volume > 50 or NOM_CLASSE=="bruit":
        fichier = f"{DOSSIER}/{NOM_CLASSE}_{compteur + 1:03d}.wav"
        wav.write(fichier, FREQUENCE_ECHANTILLON, enregistrement)
        print(f"{fichier} enregistré (volume moyen: {volume})\n")
        compteur+=1
    else:
        print(f"[ATTENTION] SON TROP FAIBLE (volume : {volume})! Recommencez...\n")

print(f"\nEnregistrement terminé! {NOMBRE_CLIPS} clips sauvegardés dans {DOSSIER}")
