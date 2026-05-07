# Ce module transforme charge les sons de chaque étiquette,
# pour chaque son (au format wav), on extrait les MFCCs
# grâce à la fonction extraction du module extraction_mfcc.
# Ensuite l'on découpe les données en trois groupes :
# les données d'entrainement, de test et de validation.
# Grâce à Scikit-learn, on transforme les noms des classes
# en nombre entier pour l'entrainement du modèle.

import os
import numpy as np
from sklearn.model_selection import train_test_split # Découpage des données
from sklearn.preprocessing import LabelEncoder # Transformation des mots en numéro pour les NN
from tensorflow.keras.utils import to_categorical # créer un codage one-hot
from extraction_mfcc import extraction

REPERTOIRE_DES_CLASSES = 'sons/'
CLASSES = ['marche', 'inverse', 'stop', 'plus',  'moins', 'bruit', 'inconnu']
RATIO_TEST = 0.2 # La part du jeu des données de test (15%)
RATIO_VALIDATION = 0.2 # La part des données de validation (15%)
SEED = 42 # Ce découpage est reproductible.

sons, mots = [], []
print('CHARGEMENT DU DATASET...')

for label in CLASSES:
    dossier = os.path.join(REPERTOIRE_DES_CLASSES, label)
    if not os.path.isdir(dossier):
        print(f"[ATTENTION] Ce dossier n'existe pas : {dossier}")
        continue
    compteur=0
    for fichier in os.listdir(dossier):
        if not fichier.lower().endswith('.wav'):
            continue

        chemin = os.path.join(dossier, fichier)
        try:
            features = extraction(chemin_fichier=chemin)
            sons.append(features)
            mots.append(label)
            compteur += 1
        except Exception as e:
            print(f"[ERREUR] {fichier} : {e}")

    print(f"{label:<10} : {compteur} fichiers chargés")

X = np.array(sons, dtype=np.float32) # passe d'une list en un tableau numpy
print(f"\nDATASET chargé : {X.shape}, dtype={X.dtype}")

# Encoder les étiquettes en entiers
label_encoder = LabelEncoder()
y_int = label_encoder.fit_transform(mots) # Transformation des labels texte en nombres entiers
y = to_categorical(y_int, num_classes=len(label_encoder.classes_))

print(f"Classes (ordre) : {list(label_encoder.classes_)}")

# Division
X_temp, X_test, y_temp, y_test, y_int_temp, y_int_test = train_test_split(
    X, y, y_int,
    test_size=RATIO_TEST,
    random_state=SEED,
    stratify=y_int # Pour conserver la distribution des classes
)

ratio_val_sur_restant = RATIO_VALIDATION / (1 - RATIO_TEST)
X_train, X_val, y_train, y_val, y_int_train, y_int_val = train_test_split(
    X_temp, y_temp, y_int_temp,
    test_size=ratio_val_sur_restant,
    random_state=SEED,
    stratify=y_int_temp
)

NUM_CLASSES = len(label_encoder.classes_)
CLASSES_ORDRE = list(label_encoder.classes_)

taille_X_train = X_train.shape
taille_X_val = X_val.shape
taille_X_test = X_test.shape
print(f"Entrainement : {taille_X_train}")
print(f"Validation   : {X_val.shape}")
print(f"Test         : {X_test.shape}")