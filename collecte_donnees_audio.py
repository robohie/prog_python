# Importation des modules :
# 1. sounddevice pour l'enregistrement des sons issus du microphone de l'ordinateur
# 2. scipy.io.wavfile pour la lecture et l'écriture des fichiers enregistrement au format wav
# 3. numpy pour le calcul matriciel
# 4. os pour la gestion du système des fichiers
# 5. time pour la gestion du temps

import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
import os, time

FREQUENCE_ECHANTILLON = 16000    # Le signal sonore est échantillonné à 16 kHz
DUREE = 1                        # Chaque enregistrement dure 1 seconde, utile pour la conversion Mel
NOMBRE_CLIPS = 400               # Le nombre d'individus par échantillon ou classe
NOM_CLASSE = "bruit"             # La classe ou l'étiquette concernée
DOSSIER = f"sons/{NOM_CLASSE}"   # Le sous dossier du dossier "sons" contenant les enregistrements

os.makedirs(DOSSIER, exist_ok=True)
print(f"Enregistrement de {NOMBRE_CLIPS} clips pour la classe '{NOM_CLASSE}'")
print(f"({FREQUENCE_ECHANTILLON} Hz, 16 bits, mono, {DUREE}s)")
print('______________________________________________________________________\n')

time.sleep(1)

i = 0
while i < NOMBRE_CLIPS:
    if NOM_CLASSE.lower() != "bruit":
        input(f"[{i + 1:03d}/{NOMBRE_CLIPS}] Appuyez sur ENTREE puis prononcez '{NOM_CLASSE}'...")
    enregistrement = sd.rec(int(DUREE * FREQUENCE_ECHANTILLON),
                            samplerate=FREQUENCE_ECHANTILLON,
                            channels=1,
                            dtype='int16')
    sd.wait()

    # Vérification du volume
    volume = np.abs(enregistrement).mean() # la moyenne des valeurs absolues des intensités
    if volume < 50:
        print(" [ATTENTION] Volume très faible. Recommencez ce clip!")
        i-=1
        continue

    fichier = os.path.join(DOSSIER, f"{NOM_CLASSE}_{i+1:03d}.wav")
    wav.write(fichier, FREQUENCE_ECHANTILLON, enregistrement)
    print(f"{fichier} sauvegardé (volume moyen: {volume:.0f})")

    i+=1
    time.sleep(0.3)

print(f"\nEnregistrement terminé! {NOMBRE_CLIPS} clips sauvegardés dans {DOSSIER}")
