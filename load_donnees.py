import os
import numpy as np
from jupyterlab.semver import satisfies
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.utils import to_categorical

CHEMIN_DONNEES = "sons\\"
MOTS = ("marche", "inverse", "stop", "plus", "moins")
MAX_FRAMES = 100 # nombre de frames temporelles

X_list, Y_list = [], []
print("Chargement des données...")

for label in MOTS:
    folder = os.path.join(CHEMIN_DONNEES, label)
    if not os.path.isdir(folder):
        print(f" [ATTENTION] Dossier absent : {folder}")
        continue
    count = 0
    for fname in os.listdir(folder):
        if not fname.lower().endswith(".wav"):
            continue
        try:
            features = extract_mfcc(os.path.join(folder, fname),
                                    max_frames=MAX_FRAMES)
            X_list.append(features)
            Y_list.append(label)
            count += 1
        except Exception as e:
            print(f"[ERREUR] {fname} : {e}")
    print(f" {label : <10} : {count} fichiers chargés")

X = np.array(X_list)
print(f"\nDATASET chargé : {X.shape}, dtype={X.dtype}")
# Encoder les etiquettes en entiers
le = LabelEncoder()
y_int = le.fit_transform(Y_list)
y_onehot = to_categorical(y_int)
print(f"Classes (ordre): {list(le.classes_)}")

# Division 80% entrainement / 20% validattion
X_train, X_val, y_train, y_val = train_test_split(X, y_onehot,
                                                  test_size=0.2, random_state=42,
                                                  stratify=y_int)

print(f"Entrainement : {X_train.shape}")
print(f"Validation : {X_val.shape}")
NUM_CLASSES = len(le.classes_)