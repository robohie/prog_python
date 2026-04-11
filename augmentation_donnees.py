import librosa
import soundfile as sf
import numpy as np
import os

def agrandir_audio(chemin_fichier, dossier, nombre=10):
    """
    Crée "nombre" versions d'un fichier audio, grâce aux opérations
    comme l'ajout de bruit, le décalage temporel, le changement de
    hauteur.
    :param chemin_fichier:
    :param dossier:
    :param nombre:
    :return:
    """
    y, sr = librosa.load(chemin_fichier, sr=16000)
    base = os.path.splitext(os.path.basename(chemin_fichier))[0]
    saved = []

    for i in range(nombre):
        agrandi = y.copy()

        facteur_bruit = np.random.uniform(0.001, 0.01)
        agrandi = agrandi + facteur_bruit * np.random.normal(0, 1, len(y))

        decalage = np.random.randint(-3200, 3200)
        agrandi = np.roll(agrandi, decalage)

        if np.random.rand() > 0.5:
            steps = np.random.uniform(-2, 2)
            agrandi = librosa.effects.pitch_shift(agrandi, sr=sr, n_steps=steps)

        agrandi = agrandi / (np.max(np.abs(agrandi)) + 1e-8)
        sortie = os.path.join(dossier, f'{base}{i}.wav')
        sf.write(sortie, agrandi, sr, subtype='PCM_16')
        saved.append(sortie)

    return saved

DATASET_PATH = "sons"
for mot in ("marche",):
    src_dir = os.path.join(DATASET_PATH, mot)
    for fname in os.listdir(src_dir):
        if fname.endswith('.wav'):
            agrandir_audio(os.path.join(src_dir, fname), src_dir, 400)
    print(f"mot {mot} terminé!")