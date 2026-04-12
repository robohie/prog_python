import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
import os, time

FREQUENCE_ECHANTILLON = 16000
DUREE = 1 # Chaque enregistrement dure 1 seconde
NOMBRE_CLIPS = 400
NOM_CLASSE = "bruit"
DOSSIER = f"sons/{NOM_CLASSE}"

os.makedirs(DOSSIER, exist_ok=True)
print(f"Enregistrement de {NOMBRE_CLIPS} clips pour la classe '{NOM_CLASSE}'")
print(f"format : {FREQUENCE_ECHANTILLON} Hz, 16 bits, mono, {DUREE}s")
print("Prononcez le mot (appuyez sur ENTREE)")
time.sleep(1)

for i in range(NOMBRE_CLIPS):
    input(f"[{i + 1:03d}/{NOMBRE_CLIPS}] Appuyez sur ENTREE puis prononcez '{NOM_CLASSE}'...")
    audio = sd.rec(int(DUREE * FREQUENCE_ECHANTILLON),
                   samplerate=FREQUENCE_ECHANTILLON,
                   channels=1,
                   dtype='int16')
    sd.wait()

    # Vérification du volume
    volume = np.abs(audio).mean()
    if volume < 50:
        print(" [ATTENTION] Volume très faible. Recommencez ce clip!")
        i-=1
        continue

    fichier = os.path.join(DOSSIER, f"{NOM_CLASSE}_{i:03d}.wav")
    wav.write(fichier, FREQUENCE_ECHANTILLON, audio)
    print(f"Sauvegardé : {fichier} (volume moyen: {volume:.0f})")
    time.sleep(0.3)

print(f"\nTerminé! {NOMBRE_CLIPS} clips sauvegardés dans {DOSSIER}")
