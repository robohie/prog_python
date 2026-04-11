import librosa
import numpy as np

# Constantes d'extraction MFCC
SR = 16000 # Fréquence d'échantillonnage
N_MFCC = 13 # Nombre de coefficients
N_FFT = 512 # Taille de la fênetres
HOP_LENGTH = 160 # Pas entre fênetres

def extraire_mfcc(chemin, max_frames=100):
    """Extraire et normaliser les MFCCs d'un fichier audio WAV.
    Returne un tableau numpy de forme (max_frames, N_MFCC, 1)
    La dimension 1 est le canal"""

    y, sr = librosa.load(chemin, sr=SR, mono=True)

    #Tronquer pour avoir exactement 1 seconde
    if len(y) > SR:
        y = y[:SR]
    else:
        y = np.pad(y, (0, SR - len(y)))

    # Calculer les MFCCs : resultat de forme (N_MFCC, n_frames)
    mfcc = librosa.feature.mfcc(y=y, sr=SR, n_mfcc=N_MFCC,
                                n_fft=N_FFT, hop_length=HOP_LENGTH)
    # Transposer -> (n_frames, N_MFCC)
    mfcc=mfcc.T

    # Uniformiser à max_frames
    if mfcc.shape[0] < max_frames:
        pad = np.zeros((max_frames - mfcc.shape[0], N_MFCC))
        mfcc = np.vstack([mfcc, pad])
    else:
        mfcc = mfcc[:max_frames]

    # Normalisation Z-score : moyenne=0, ecart-type=1
    mfcc = (mfcc - mfcc.mean()) / (mfcc.std() + 1e-8)

    # Ajouter la dimension canal
    return mfcc[..., np.newaxis].astype(np.float32)