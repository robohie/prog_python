"""
Ce script, Généré par Claude AI, sert à créer le fichier mel_filterbank.h
utilisé par l'Arduino. Il faut le relancer SEULEMENT si on change
la frequence d'échantillonnage, N_FFT, N_MELS, les fréquences min ou max
dans extraction_mfcc.py. Sinon le fichier.h ne correspondra plus à ce qui a
servi à l'entrainement du modèle
"""

import librosa
import numpy as np

# ces valeurs doivent être EXACTEMENT les memes que dans extraction_mfcc.py
FREQUENCE = 16000
N_FFT = 512
N_MELS = 40
FMIN = 20.0
FMAX = FREQUENCE / 2

NOM_FICHIER_SORTIE = "mel_filterbank.h"


def generer_fichier_header():
    """
    Cette fonction génère le fichier d'en-tête qui sera
    utilisé côté arduino.

    :return:
    """

    # on demande à librosa de calculer les 40 filtres mel
    # le résultat est un tableau de 40 lignes (un filtre par ligne).
    matrice_mel = librosa.filters.mel(
        sr=FREQUENCE, n_fft=N_FFT, n_mels=N_MELS, fmin=FMIN, fmax=FMAX
    )

    nb_filtres = matrice_mel.shape[0]
    nb_colonnes = matrice_mel.shape[1]

    # on prépare les lignes du fichier(h) petit a petit dans une liste
    lignes = ["// Généré avec librosa.filters.mel()", "// sr=" + str(FREQUENCE) + " n_fft=" + str(N_FFT) +
              " n_mels=" + str(N_MELS) + " fmin=" + str(FMIN) + " fmax=" + str(FMAX),
              "// Ne pas modifier a la main, relancer le script si besoin", "#ifndef MEL_FILTERBANK_H",
              "#define MEL_FILTERBANK_H", "", "#define MEL_NUM_FILTERS " + str(nb_filtres),
              "#define MEL_NUM_FFT_BINS " + str(nb_colonnes) + "  // n_fft/2 + 1", "", "typedef struct {",
              "  uint16_t start_bin;", "  uint16_t num_bins;", "  const float* weights;", "} MelFilter;", ""]

    lignes_structs = []

    # Chaque filtre mel a beaucoup de zeros, il ne "voit" qu'une petite
    # plage de frequences comme indiqué dans le rapport de ce projet.
    # Donc, on ne garde que la partie utile pour economiser de la memoire sur l'Arduino
    for i in range(nb_filtres):

        ligne_filtre = matrice_mel[i]

        # on cherche où commencent et où finissent les valeurs non nulles
        indices_non_zero = np.nonzero(ligne_filtre)[0]

        if len(indices_non_zero) == 0:
            # ça ne devrait pas arriver avec des paramètres normaux
            raise ValueError("Le filtre mel numero " + str(i) + " est vide, "
                              "verifie tes paramètres (N_FFT, N_MELS, fmin, fmax)")

        indice_debut = int(indices_non_zero[0])
        indice_fin = int(indices_non_zero[-1])
        nb_valeurs = indice_fin - indice_debut + 1

        poids = ligne_filtre[indice_debut: indice_debut + nb_valeurs]

        nom_tableau = "mel_weights_" + str(i)

        # on écrit chaque poids en notation scientifique avec 8 chiffres
        valeurs_texte = []
        for w in poids:
            valeurs_texte.append("{:.8e}f".format(w))
        texte_valeurs = ", ".join(valeurs_texte)

        lignes.append("static const float " + nom_tableau + "[" + str(nb_valeurs) + "] = { " + texte_valeurs + " };")

        lignes_structs.append("  { " + str(indice_debut) + ", " + str(nb_valeurs) + ", " + nom_tableau + " }")

    lignes.append("")
    lignes.append("static const MelFilter mel_filterbank[MEL_NUM_FILTERS] = {")
    lignes.append(",\n".join(lignes_structs))
    lignes.append("};")
    lignes.append("")
    lignes.append("#endif // MEL_FILTERBANK_H")

    # on écrit tout dans le fichier(h) d'un coup
    fichier = open(NOM_FICHIER_SORTIE, "w")
    fichier.write("\n".join(lignes))
    fichier.close()

    print(NOM_FICHIER_SORTIE + " génère (" + str(nb_filtres) + " filtres).")


if __name__ == "__main__":
    generer_fichier_header()
