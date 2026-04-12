import os, librosa
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

SR = 16000
N_MFCC=13
MAX_FRAMES = 100
DONNEES_CHEMIN = "sons"
BATCH_SIZE = 32
EPOCHS = 30

# 1. Charger tous les fichiers et leurs labels
def extract_mfcc(chemin):
    y, sr = librosa.load(chemin, sr=SR, mono=True)
    if len(y) > SR:
        y = y[:SR]
    else:
        y = np.pad(y, (0, SR - len(y)))

    mfcc = librosa.feature.mfcc(y=y, sr=SR, n_mfcc=N_MFCC, n_fft=512, hop_length=160)
    mfcc = mfcc.T

    if mfcc.shape[0] < MAX_FRAMES:
        pad = np.zeros((MAX_FRAMES - mfcc.shape[0], N_MFCC))
        mfcc = np.vstack([mfcc, pad])
    else:
        mfcc = mfcc[:MAX_FRAMES]
    mfcc = (mfcc - mfcc.mean()) / (mfcc.std() + 1e-8)
    return mfcc[..., np.newaxis].astype(np.float32)

x = []
y = []
print("Chargement des données...")

for mot in os.listdir(DONNEES_CHEMIN):
    dossier = os.path.join(DONNEES_CHEMIN, mot)
    if not os.path.isdir(dossier):
        continue
    for fichier in os.listdir(dossier):
        if fichier.endswith(".wav"):
            chemin_fichier = os.path.join(dossier, fichier)
            try:
                features = extract_mfcc(chemin_fichier)
                x.append(features)
                y.append(mot)
            except Exception as e:
                print(f"Erreur sur {chemin_fichier} : {e}")

x, y = np.array(x), np.array(y)
print(f"Données chargées : {x.shape} exemples")

# 2. Encoder les labels
le = LabelEncoder()
y_int = le.fit_transform(y)
y_cat = tf.keras.utils.to_categorical(y_int, num_classes=len(le.classes_))
print("Classes : ", le.classes_)

# 3. Split train / validation
x_train, x_val, y_train, y_val = train_test_split(x, y_cat, test_size=0.2, random_state=42, stratify=y_int)

# 4. Construction du modèle
model = models.Sequential([
        # Couche d'entrée
        layers.Input(shape=(MAX_FRAMES, N_MFCC, 1)),

        # Première convolution : detecte les motifs simples
        layers.Conv2D(8, (5, 3), activation="relu", padding="same"),
        layers.MaxPooling2D((2, 2)),

        # Deuxième convolution
        layers.Conv2D(16, (3, 3), activation="relu", padding="same"),
        layers.MaxPooling2D((2, 2)),

        # Transition vers les couches denses
        layers.Flatten(),

        layers.Dropout(0.25),

        # Couche dense cachée
        layers.Dense(64, activation="relu"),
        # Couche de sortie
        layers.Dense(len(le.classes_), activation="softmax")
    ])
model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
model.summary()

# 5. Callbacks
callbacks = [
    tf.keras.callbacks.EarlyStopping(monitor="val_accuracy", patience=8, restore_best_weights=True),
    tf.keras.callbacks.ModelCheckpoint('best_model.h5', monitor='val_accuracy', save_best_only=True),
    tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=4, min_lr=1e-6)
]

# 6. Entraînement
history = model.fit(
    x_train, y_train,
    validation_data=(x_val, y_val),
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    callbacks=callbacks,
    verbose=1
)

# 7. Evaluation et sauvegarde
val_loss, val_acc = model.evaluate(x_val, y_val, verbose=0)
print(f"\nPrécision validation : {val_acc*100:.2f}%")

# sauvegarde du modèle final
model.save("modèle_vocal_final.h5")

# sauvegarde des classes pour arduino
with open("labels.txt", "w") as f:
    for label in le.classes_:
        f.write(label + "\n")
print("Labels sauvegardés dans labels.txt (à copier dans le code Arduino)")