# Module d'entrainement du modèle définit dans definition_model.py
# Il s'agit d'un entrainement avec callbacks : l'entrainement
# s'arrête si la précision de validation ne s'améliore plus.
# Il y a sauvegarde automatique du meilleur modèle à chaque époque.

import load_dataset as ld
import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np
from definition_modele import def_model
from sklearn.metrics import confusion_matrix, classification_report


LIMITE_EPOQUES = 10
EPOQUES = 50

# Callbacks
callbacks = [
    # Arrêter si val_accuracy ne s'améliore pas pendant N époques
    tf.keras.callbacks.EarlyStopping(
        monitor="val_accuracy",
        patience=LIMITE_EPOQUES,
        restore_best_weights=True, # Récharger le meilleur modèle
        verbose=1
    ),
    # Sauvegarder le meilleur modèle automatiquement
    tf.keras.callbacks.ModelCheckpoint(
        filepath="meilleur_model.keras",
        monitor="val_accuracy",
        save_best_only=True,
        verbose=1
    ),
    # Réduire le learning rate si la progression stagne
    tf.keras.callbacks.ReduceLROnPlateau(
        monitor="val_loss",
        factor=0.5,
        patience=LIMITE_EPOQUES/2,
        min_lr=1e-6,
        verbose=1
    )
]

# Entrainement
model = def_model()
history = model.fit(
    ld.X_train, ld.y_train,
    validation_data=(ld.X_val, ld.y_val),
    epochs=EPOQUES,
    batch_size=32,
    callbacks=callbacks,
    verbose=1
)

# Evaluation finale
val_loss, val_acc = model.evaluate(ld.X_val, ld.y_val, verbose=0)
print(f"\nPrécision finale sur validation : {val_acc*100:.2f}%")
print(f"Perte finale : {val_loss:.4f}")

# Obtenir les prédictions sur le dataset de validation
y_prediction_proba = model.predict(ld.X_val, verbose=0)
y_prediction = np.argmax(y_prediction_proba, axis=1) # classe prédite
y_vraie = np.argmax(ld.y_val, axis=1)  # vraie classe

# Matrice de confusion
# Un coefficient Cij d'une matrice de confusion indique combien d'exemple
# de la classe i ont été prédits comme appartenant à la classe j.
matrice = confusion_matrix(y_vraie, y_prediction)
print("Matrice de confusion :")
print(matrice)

# Rapport détaillé : précision, recall, F1 par classe
print("\nRapport de classification :")
print(classification_report(y_vraie, y_prediction, target_names=ld.label_encoder.classes_))

# Visualisation des courbes d'entraînement
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
ax1.plot(history.history["accuracy"], label="Entraînement")
ax1.plot(history.history["val_accuracy"], label="Validation")
ax1.set_title("Précision par époque")
ax1.set_xlabel("Epoque")
ax1.legend()

ax2.plot(history.history["loss"], label="Entraînement")
ax2.plot(history.history["val_loss"], label="Validation")
ax2.set_title("Perte par époque")
ax2.set_xlabel("Epoque")
ax2.legend()

plt.tight_layout()
plt.savefig("Courbes_entraînement.png", dpi=150, bbox_inches="tight")
plt.show()
# ==========================================================================
# Charger le meilleur modèle enregistré
model = tf.keras.models.load_model("meilleur_model.keras")

# Initialiser le convertisseur
converter = tf.lite.TFLiteConverter.from_keras_model(model)

# Activer les optimisations
converter.optimizations = [tf.lite.Optimize.DEFAULT]

# Générateur de données de calibration
def calibration_data_gen(nombre:int=100):
    """Utilise nombre exemples de l'ensemble de validation"""
    for i in range(min(nombre, len(ld.X_val))):
        sample = np.expand_dims(ld.X_val[i], axis=0).astype(np.float32)
        yield [sample]

converter.representative_dataset = calibration_data_gen

# Forcer toutes les opérations en int8
converter.target_spec.supported_ops = [
    tf.lite.OpsSet.TFLITE_BUILTINS_INT8
]

# Forcer les entrées et sorties en int8
converter.inference_input_type = tf.int8
converter.inference_output_type = tf.int8

# Convertir le modèle
model_tflite = converter.convert()
# Sauvegarder le fichier .tflite
with open("model_quantified.tflite", "wb") as f:
    f.write(model_tflite)

np.save("data_validation", ld.X_val)
np.save("label_validation", ld.y_val)
