# Ce script reproduit le calcul utilisé par l'exemple micro_speech
# FFT 256 points, 40 filtres Mel

import librosa # gestion des données musicales
import numpy as np

# Constantes
SAMPLE_RATE = 16000
WINDOW_SIZE_MS = 30 # durée d'une trame
WINDOW_STRIDE_MS = 20 # décalage entre trames
# Pour une seconde d'audio, le nombre de trames = (1000 - 30)/20 + 1 = 49
# Dans l'exemple officiel, on génère 49 trames de 40 coefficients Mel.
FFT_SIZE = 256 # Doit être une puissance de 2 >= WINDOW_SIZE échantillons.
WINDOW_SIZE_SAMPLES = int(SAMPLE_RATE * WINDOW_SIZE_MS / 1000)
N_MELS = 40
N_FFT = 512
HOP_LENGTH = int(SAMPLE_RATE * 0.020)
WIN_LENGTH = int(SAMPLE_RATE * 0.030)
MAX_FRAMES = 49

def extraction(chemin_fichier, max_frame=MAX_FRAMES):
    y, sr = librosa.load(chemin_fichier, sr=SAMPLE_RATE, mono=True)
    if len(y) == 0:
        raise ValueError(f"Fichier audio vide : {chemin_fichier}")

    # Tronquer ou pad à 1 seconde
    target_len = SAMPLE_RATE
    if len(y) > target_len:
        y = y[:target_len]
    else:
        y = librosa.util.fix_length(y, size=target_len)

    # Calcul du spectrogramme Mel
    mel_spec = librosa.feature.melspectrogram(
        y=y,
        sr=SAMPLE_RATE,
        n_fft=N_FFT,
        hop_length=HOP_LENGTH,
        win_length=WIN_LENGTH,
        window="hamming",
        n_mels=N_MELS,
        fmin=20.0, # fréquences basses
        fmax=SAMPLE_RATE/2
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
