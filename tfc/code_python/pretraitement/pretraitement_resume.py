# Auteur : BOSOLINDO EDHIENGENE Roger
# =================================================
# Les fichiers considérés sont des fichiers audios
# de type .wav.
# =================================================

import os
import numpy as np

from extraction_mfcc import extraction
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from typing import Tuple

# CHEMIN VERS LE DATASET
DATASET = "data/"

# LISTE DES ETIQUETTES CONSTITUANT LE DATASET
# Ce sont des dossiers contenant plusieurs enregistrements d'un mot
MOTS_CLES = ("go",
             "yes",
             "up",
             "down",
             "bed",
             "left",
             "backward",
             "stop",
             "bird",
             "dog",
             "eight",
             "no",
             "forward",
             "nine",
             "off",
             "house")

# LA LISTE DES ETIQUETTES À RECONNAITRE
# Ce sont les données d'entrainement à part la classe INCONNU
CLASSES = ("go",
           "up",
           "down",
           "left",
           "stop")

EXEMPLES_PAR_LABELS = 3500

def resume_and_data(dataset_folder:str=DATASET,
                   extension:str=".wav",
                   all_labels:Tuple[str]=MOTS_CLES,
                   labels:Tuple[str]=CLASSES,
                   ech_par_label:int=EXEMPLES_PAR_LABELS) -> Tuple[np.ndarray, list]:
    """

    :param dataset_folder: emplacement des sous-dossiers des enregistrements
    :param extension: l'extension des fichiers audios traités
    :param all_labels: la liste des sous-dossiers (liste des labels possibles)
    :param labels: la liste des labels exploités, les autres sont inconnus
    :param ech_par_label: nombre maximal d'échantillons par étiquette

    :return:
    """
    enregistrements, classes = [], []
    compteur_inconnus = 0

    # LA LISTE DES ETIQUETTES INCONNUES
    mots_inconnus = [m for m in MOTS_CLES if m not in labels]
    np.random.shuffle(mots_inconnus)  # pour les mélanger de façon aléatoire

    limite_inconnus = int(ech_par_label * 1.2)

    # =========================================================================
    print("CHARGEMENT DU DATASET...")

    for classe in all_labels:
        dossier = os.path.join(dataset_folder, classe)

        fichiers = os.listdir(dossier)  # liste des enrégistrements de la classe
        for fichier in fichiers:
            # On vérifie si l'enregistrement a l'extension souhaitée
            if not fichier.lower().endswith(extension):
                continue

            chemin = os.path.join(dossier, fichier)  # chemin vers le fichier .wav
            try:
                features = extraction(chemin_fichier=chemin)
            except Exception as e:
                print(f"Erreur lors de l'extraction de {chemin} : {e}")
                continue

            if classe in labels:
                enregistrements.append(features)
                classes.append(classe)
            else:
                # On limite le nombre d'enregistrements des étiquettes
                # de classe "inconnu" pour avoir un ensemble de données
                # cohérent.
                if compteur_inconnus <= limite_inconnus:
                    enregistrements.append(features)
                    classes.append("inconnu")
                    compteur_inconnus += 1
    # ====================================================================================
    msg = f"Données chargées : {len(enregistrements)}"
    data = np.array(enregistrements, dtype=np.float32)  # Nous passons à un tableau numpy
    # LabelEncoder permet de créer une bijection entre les noms des étiquettes
    # et des nombres entiers naturels 0, 1, 2, ...
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(classes)

    print(msg)
    print("=" * len(msg))

    # affichage du nombre d'échantillons par étiquette
    for c in labels + ("inconnu",):
        print(f"{c} : {classes.count(c)} échantillons")

    print(f"\nDATASET chargé avec succès: shape={data.shape}, dtype={data.dtype}")

    # affichage de l'ordre des classes, très importants pour comprendre quel chiffre
    # est lié à quel label.
    print(f"Ordre des classes : {list(label_encoder.classes_)}")

    return data, y

def repartition(data:np.ndarray,
                e_labels:list,
                ratio_test:int=0.15,
                ratio_validation=0.15,
                seed:int=42):
    """"""
    # Répartition des données dans le jeu d'entrainement, de validation et de test
    print(f"Dimension d'une entrée du modèle : {data[0].shape}")

    x_temp, x_test, y_temp, y_test = train_test_split(
        data, e_labels,
        test_size=ratio_test,
        stratify=e_labels,
        random_state=seed
    )

    # pourcentage du jeu de données de validation récalculé
    ratio_val = ratio_validation / (1 - ratio_test)

    x_train, x_val, y_train, y_val = train_test_split(
        x_temp, y_temp,
        test_size=ratio_val,
        stratify=y_temp,
        random_state=seed
    )

    print("REPARTITION DES DONNEES(entre le test, la validation et l'entrainement")
    print("======================================================================")
    print(f"Entraînement : {x_train.shape}")
    print(f"Validation   : {x_val.shape}")
    print(f"Test         : {x_test.shape}")

    return {
        "x_train": x_train,
        "x_val": x_val,
        "x_test": x_test,
        "y_train":y_train,
        "y_val": y_val,
        "y_test": y_test
    }