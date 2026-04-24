from tensorflow import keras
from tensorflow.keras import layers, models
from load_dataset import NUM_CLASSES

INPUT_SHAPE=(100, 20, 1) # (max_frames, n_mfcc, canaux)

def def_model():
    model = models.Sequential([
        # Couche d'entrée
        layers.Input(shape=INPUT_SHAPE),

        # Première convolution (motif simple)
        layers.Conv2D(8, (3, 3), padding="same", use_bias=False),
        layers.BatchNormalization(),
        layers.ReLU(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.10),

        # Deuxième convolution (motif plus complexe)
        layers.Conv2D(16, (3, 3), padding="same", use_bias=False),
        layers.BatchNormalization(),
        layers.ReLU(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.15),

        # Transition vers les couches denses
        layers.GlobalAveragePooling2D(),
        layers.Dense(32, activation="relu"),
        layers.Dropout(0.20),
        layers.Dense(NUM_CLASSES, activation="softmax")
    ])

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-3),
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )
    return model

if __name__ == "__main__":
    built_model = def_model()
    built_model.summary()