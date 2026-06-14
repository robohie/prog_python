# Ce script reproduit le calcul utilisé par l'exemple micro_speech
# FFT (transformée de Fourier Rapide) 256 points, 40 filtres Mel

import librosa # gestion des données sonores
import numpy as np

# Constantes
DUREE_CLIP_ms: int = 1000 # durée d'un enregistrement audio en milliseconde
FREQUENCE: int = 16000 # fréquence d'échantillonnage.
DUREE_TRAME_ms: int = 30 # durée d'une trame (ou fenêtre) en milliseconde
DECALAGE_TRAME_ms: int = 20 # décalage entre trames en milliseconde

# Pour une seconde d'audio, le nombre de trames = (1000 - 30)/20 + 1 = 49
# On compte donc 49 trames (de 40 coefficients Mel, exemple micro-speech).
NOMBRE_ECHANTILLONS = int(FREQUENCE * DUREE_CLIP_ms / 1000) # Nombre total d'échantillons
ECHANTILLONS_PAR_TRAME = int(FREQUENCE * DUREE_TRAME_ms / 1000) # Échantillons dans une fenêtre.
WINDOW_STRIDE_SAMPLES = int(FREQUENCE * DECALAGE_TRAME_ms / 1000)
LENGTH_minus_WINDOW = NOMBRE_ECHANTILLONS - ECHANTILLONS_PAR_TRAME

NOMBRE_TRAMES: int = int(LENGTH_minus_WINDOW/WINDOW_STRIDE_SAMPLES + 1)

FFT_SIZE = 256 # Doit être une puissance de deux.

N_MELS = 40 # Nombre des coefficients Mel par trame
N_FFT = 512
HOP_LENGTH = int(FREQUENCE * 0.020)
WIN_LENGTH = int(FREQUENCE * 0.030)


def extraction(chemin_fichier, max_frame=NOMBRE_TRAMES):
    y, sr = librosa.load(chemin_fichier, sr=FREQUENCE, mono=True)
    if len(y) == 0:
        raise ValueError(f"Fichier audio vide : {chemin_fichier}")

    # Tronquer ou pad à 1 seconde
    target_len = FREQUENCE
    if len(y) > target_len:
        y = y[:target_len]
    else:
        y = librosa.util.fix_length(y, size=target_len)

    # Calcul du spectrogramme Mel
    mel_spec = librosa.feature.melspectrogram(
        y=y,
        sr=FREQUENCE,
        n_fft=N_FFT,
        hop_length=HOP_LENGTH,
        win_length=WIN_LENGTH,
        window="hamming",
        n_mels=N_MELS,
        fmin=20.0, # fréquences basses
        fmax=FREQUENCE / 2
    )

    # Passage en échelle logarithmique (log Mel)
    log_mel = np.log(mel_spec + 1e-6)

    if log_mel.shape[1] < max_frame:
        pad_width = max_frame - log_mel.shape[1]
        log_mel = np.pad(log_mel, ((0,0), (0, pad_width)), mode="constant")
    else:
        log_mel = log_mel[:, :max_frame]

    # Normalisation par trame (moyenne=0, variance=1)
    mean = np.mean(log_mel, axis=0, keepdims=True)
    std = np.std(log_mel, axis=0, keepdims=True) + 1e-8
    log_mel = (log_mel - mean) / std

    # Transposition pour obtenir (frames, mel_bins)
    log_mel = log_mel.T

    # Ajout de la dimension canal pour CNN
    return log_mel[..., np.newaxis].astype(np.float32)
