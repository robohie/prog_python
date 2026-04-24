import librosa
import numpy as np


# Constantes d'extraction
FREQUENCE_ECHANTILLON = 16000
N_MFCC = 20 # Nombre de caractéristiques extraites par fenêtre (la résolution)
N_FFT = 512 # Taille de la fenêtre FFT (analyse fréquentielle)
HOP_LENGTH = 160 # Pas entre fenêtres successives
DUREE = 1 # durée d'un son en seconde

def extraction(chemin_fichier, max_frame=100):
    """
    Extrait et normalise les MFCCs d'un fichier audio WAV.
    Retourne un tenseur (numpy) de forme (max_frames, N_MFCC, 1)
    La dimension 1 étant label_encoder canal
    """
    # 1. Chargement du fichier
    y, sr = librosa.load(chemin_fichier, sr=FREQUENCE_ECHANTILLON, mono=True)
    # Vérification : label_encoder fichier est-il vide ?
    if not len(y):
        raise ValueError(f"Fichier audio vide : {chemin_fichier}")

    # 2. Tronquer pour avoir exactement 1 seconde
    longueur = int(FREQUENCE_ECHANTILLON*DUREE) # nombre d'échantillons correspondant à DUREE
    if len(y) > longueur:
        y = y[:longueur]
    else:
        y = librosa.util.fix_length(y, size=longueur) # complète avec des zéros

    # 3. Normalisation de l'amplitude du signal
    y = librosa.util.normalize(y)

    # 4. Calcul des MFCCs
    mfcc = librosa.feature.mfcc(
        y=y,
        sr=FREQUENCE_ECHANTILLON,
        n_mfcc=N_MFCC,
        n_fft=N_FFT,
        hop_length=HOP_LENGTH
    )
    # 5. Permutation des axes pour obtenir (temps, coefficients)
    mfcc = mfcc.T

    # 6. Uniformiser à max_frames
    if mfcc.shape[0] < max_frame:
        padding = np.zeros((max_frame - mfcc.shape[0], N_MFCC), dtype=mfcc.dtype)
        mfcc = np.vstack([mfcc, padding])
    else:
        mfcc = mfcc[:max_frame]

    # Normalisation par coefficient ( moyenne=0, variance=1)
    mfcc = (mfcc - mfcc.mean(axis=0, keepdims=True)) / (mfcc.std(axis=0, keepdims=True) + 1e-8)

    # Ajout de la dimension canal (nécessaire pour un CNN)
    return mfcc[..., np.newaxis].astype(np.float32)