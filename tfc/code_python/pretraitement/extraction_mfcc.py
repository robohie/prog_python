# Auteur : BOSOLINDO EDHIENGENE Roger
# mail : rogerbosolinndo34@gmail.com
# =================================================================
# Ce script reproduit le calcul utilisé par l'exemple micro_speech
# FFT (transformée de Fourier Rapide) 256 points, 40 filtres Mel
# =================================================================
# Le module librosa est un module python d'analyse audio et
# musicale. Du chargement des fichiers à l'extraction des caractéristiques
# et l'analyse spéctrale.

import numpy as np
import librosa # gestion des données sonores

DUREE_CLIP_ms: int = 1000 # durée d'un enregistrement audio en milliseconde
FREQUENCE: int = 16000 # fréquence d'échantillonnage.
DUREE_TRAME_ms: int = 30 # durée d'une trame (ou fenêtre) en milliseconde
DECALAGE_TRAME_ms: int = 20 # décalage entre trames en milliseconde

# Pour une seconde d'audio, le nombre de trames (n) est tel que
# (ech_a – ech_b)*n – ech_b = 16000, avec ech_a le nombre d'échantillons par trame
# et ech_b le nombre d'échantillons dans la zone de chevauchement.
# On compte donc 49 trames (de 40 coefficients Mel).

NOMBRE_ECHANTILLONS = int(FREQUENCE * DUREE_CLIP_ms / 1000) # Nombre total d'échantillons
ECHANTILLONS_PAR_TRAME = int(FREQUENCE * DUREE_TRAME_ms / 1000) # Échantillons dans une fenêtre.
WINDOW_STRIDE_SAMPLES = int(FREQUENCE * DECALAGE_TRAME_ms / 1000)
LENGTH_minus_WINDOW = NOMBRE_ECHANTILLONS - ECHANTILLONS_PAR_TRAME # ech_b

NOMBRE_TRAMES: int = int(LENGTH_minus_WINDOW/WINDOW_STRIDE_SAMPLES + 1)

FFT_SIZE = 256 # Doit être une puissance de deux.

N_MELS = 40 # Nombre des coefficients Mel par trame
N_FFT = 512
HOP_LENGTH = int(FREQUENCE * DECALAGE_TRAME_ms / 1000)
WIN_LENGTH = int(FREQUENCE * DUREE_TRAME_ms / 1000)


def extraction(chemin_fichier: str,
               max_frame:int=NOMBRE_TRAMES,
               frequence:int=FREQUENCE,
               decalage:int=HOP_LENGTH,
               ech_par_trame:int=WIN_LENGTH,
               n_fft:int=N_FFT,
               n_mels:int=N_MELS):
    """
    Cette fonction extrait les caractéristiques Mel d'un enregistrement audio.
    Elle retourne ces caractéristiques en échelle logarithmique.

    :param frequence: La fréquence d'échantillonnage
    :param decalage: nombre d'échantillons par décalage de trame
    :param ech_par_trame: nombre d'échantillons par trame
    :param n_fft:
    :param n_mels: nombre de coefficients mels par trame
    :param chemin_fichier: le chemin vers les enregistrements
    :param max_frame: le nombre des trames.
    :return:
    """
    y, sr = librosa.load(chemin_fichier, sr=frequence, mono=True)
    if len(y) == 0:
        raise ValueError(f"Fichier audio vide : {chemin_fichier}")

    # Tronquer ou pad à 1 seconde
    # Nous limitons le nombre d'échantillons à FREQUENCE
    if len(y) > frequence:
        y = y[:frequence]
    else:
        # On complète les vides par des zéros
        y = librosa.util.fix_length(y, size=frequence)

    # Calcul du spectrogramme Mel
    mel_spec = librosa.feature.melspectrogram(
        y=y,
        sr=frequence,
        n_fft=n_fft,
        hop_length=decalage,
        win_length=ech_par_trame,
        window="hamming",
        n_mels=n_mels,
        fmin=20.0, # fréquences basses
        fmax=frequence / 2
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
