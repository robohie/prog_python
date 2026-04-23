# Importation des modules :
# 1. os : gestion du système de fichiers, communication avec le S.E
# 2. librosa : traitement des signaux musicaux ou de l'audio
# 3. tensorflow : conception du modèle deep-learning par des réseaux des neurones
# 4. scikit-learn(sklearn) : data analysis

import tensorflow as tf
import os


def audio_vers_mfcc(chemin_audio):
    """Cette fonction convertie les fichiers audio wav
    en spectrogramme de Mel afin d'utiliser le réseau
    des neurones convolutifs
    """
    # 1.CHARGEMENT DU FICHIER AUDIO
    audio_binary = tf.io.read_file(chemin_audio)
        # conversion des bytes vers un tableau de flottants
    audio, _ = tf.audio.decode_wav(audio_binary,
                                   desired_channels=1,
                                   desired_samples=16000)
    audio = tf.squeeze(audio, axis=-1) # supprime la dimension "canaux"([16000,1]->[16000])

    # 2.CALCUL DE LA TRANSFORMEE DE FOURIER A COURT TERME (STFT)
    stft = tf.signal.stft(
        audio,
        frame_length=640, # longueur de chaque fenêtre d'analyse
        frame_step=320, # décalage entre fenêtres
        fft_unique_bins=257 # nombre des fréquences analysées 257 = frame_length/2 + 1
    )

    # 3.CALCUL DU SPECTROGRAMME
    spectrogramme = tf.abs(stft)
    spectrogramme = tf.math.pow(spectrogramme, 0.5)

    # 4. APPLICATION DES FILTRES MEL
    num_mel_bins = 40 # nbre de bandes de fréquences Mel
    linear_to_mel = tf.signal.linear_to_mel_weight_matrix(
        num_mel_bins=num_mel_bins,
        num_spectrogram_bins=257,
        sample_rate=16000,
        lower_edge_hertz=20.0, # fréquence minimale
        upper_edge_hertz=4000 # fréquence maximale
    )
    mel_spectrogramme = tf.matmul(spectrogramme, linear_to_mel)
    log_mel = tf.math.log(mel_spectrogramme + 1e-6)

    return log_mel # forme : (49, 40)