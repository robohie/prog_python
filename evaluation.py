import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, classification_report, ConfusionMatrixDisplay
import tensorflow as tf
from train_model import x_val, y_val, le

# 1.Charger le meilleur modèle
model = tf.keras.models.load_model('best_model.h5')
print("Modèle chargé")

# 2.Prédictions sur l'ensemble de validation
y_pred_proba = model.predict(x_val, verbose=0)
y_pred = np.argmax(y_pred_proba, axis=1)
y_true=np.argmax(y_val, axis=1)

# 3. Matrice de confusion
cm = confusion_matrix(y_true, y_pred)
print("\nMATRICE DE CONFUSION")
print("(Lignes = vraies classes, Colonnes = prédictions)")
print(cm)

# Affichage graphique de la matrice de confusion
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=le.classes_)
disp.plot(cmap="Blues", xticks_rotation=45)
plt.title('Matrice de confusion')
plt.tight_layout()
plt.savefig("matrice_confusion.png", dpi=150, bbox_inches="tight")
plt.show()

# 4. Rapport de classification détaillé
print("\nRAPPORT DE CLASSIFICATION")
print(classification_report(y_true, y_pred, target_names=le.classes_))

# 5. Courbes d'apprentissage
try:
    history = model.history
except:
    print("Historique non disponible dans le modèle chargé")
    history = None

if history is not None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

    ax1.plot(history.history['accuracy'], label="Entrainement")
    ax1.plot(history.history['val_accuracy'], label="Validation")
    ax1.set_title('Précision au fil des époques')
    ax1.set_xlabel("Epoque")
    ax1.set_ylabel("Précision")
    ax1.legend()
    ax1.grid(True, linestyle="--", alpha=0.5)

    ax2.plot(history.history['loss'], label="Entrainement")
    ax2.plot(history.history['val_loss'], label="Validation")
    ax2.set_title('Perte au fil des époques')
    ax2.set_xlabel("Epoque")
    ax2.set_ylabel("Perte")
    ax2.legend()
    ax2.grid(True, linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.savefig("courbes_apprentissage.png", dpi=150, bbox_inches="tight")
    plt.show()

# Ananlyse des erreurs
print("\nEXEMPLES D'ERREURS")
errors = np.where(y_pred != y_true)[0]
print(f"Nombre total d'erreurs : {len(errors)}")
for i in errors[:5]:
    vraie_classe = le.classes_[y_true[i]]
    pred_classe = le.classes_[y_pred[i]]
    confiance = y_pred_proba[i][y_pred[i]]
    print(f" Vrai: {vraie_classe:8}| Prédit: {pred_classe:8}| Confiance: {confiance:.2f}")