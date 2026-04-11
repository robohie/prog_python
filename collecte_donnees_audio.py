import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
import os, time

FREQUENCE_ECHANTILLONNAGE = 16000
DUREE = 1                         # Une seconde
NOMS_des_CLASSE = ("marche", "stop", "inverse", "plus", "moins")       # mot à enregistrer

print(f"Enregistrement de {len(NOMS_des_CLASSE)} fichiers wav correspondant aux mots {NOMS_des_CLASSE}")
print("===============================================================================================")

for mot in NOMS_des_CLASSE:
    dossier = f"sons\\{mot}"
    os.makedirs(dossier, exist_ok=True)
    print(f"format : {FREQUENCE_ECHANTILLONNAGE} Hz, 16 bits, {DUREE}s")
    print("Prononcez le mot\n")
    time.sleep(1)

    input(f"Appuyez sur Entrée puis prononcez le mot '{mot}'")

    while True:
        audio = sd.rec(int(DUREE * FREQUENCE_ECHANTILLONNAGE),
                   samplerate=FREQUENCE_ECHANTILLONNAGE,
                   channels=1, dtype='int16')
        sd.wait()

        # Vérification du volume
        volume = np.abs(audio).mean()
        if volume < 50:
            print('[ATTENTION] Volume très faible. Recommencez!')
        else:
            break

    nom_fichier = os.path.join(dossier, f'{mot}.wav')
    wav.write(nom_fichier, FREQUENCE_ECHANTILLONNAGE, audio)
    print(f"Sauvegarde : {nom_fichier}")
    print("===================================================================")
    time.sleep(0.3)

print(f"Terminé!")