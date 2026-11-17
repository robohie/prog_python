# Auteur : BOSOLINDO EDHIENGENE Roger
# email : rogerbosolinndo34@gmail.com
# =========================================================================
# Le modèle à convolution a été inspiré du code speech_commands/models.py
# du dépot https://github.com/tensorflow/tensorflow.git

from tensorflow import keras

def model_convolution(input_shape=(49, 40, 1), nbre_classes: int = 6):
    """

    :param input_shape: la forme d'une entrée du réseau
    :param nbre_classes: le nombre de régions de décisions
    :return:
    """
    inputs = keras.Input(shape=input_shape)

    conv1 = keras.layers.Conv2D(
        filters=16,
        kernel_size=(10, 8),
        strides=(2, 2),
        padding="same",
        use_bias=False,
        activation="relu",
        name="conv_1"
    ) # Première couche de convolution

    bn1 = keras.layers.BatchNormalization(name="BNormalisation1")
    pooling1 = keras.layers.MaxPooling2D()

    conv2 = keras.layers.Conv2D(
        filters=32,
        kernel_size=(10, 8),
        strides=(2, 2),
        padding="same",
        use_bias=False,
        activation="relu",
        name="conv_2"
    ) # Deuxième couche de convolution

    bn2 = keras.layers.BatchNormalization(name="BNormalisation2")
    pooling2 = keras.layers.MaxPooling2D()
    dropout1 = keras.layers.Dropout(0.3, name="dropout_1") # Couche de régularisation

    global_pool = keras.layers.GlobalAveragePooling2D()

    dense_hidden = keras.layers.Dense(
        32,
        activation="relu",
        kernel_regularizer=keras.regularizers.l2(1e-4),
        name="couche_cachee"
    )

    dropout2 = keras.layers.Dropout(0.3, name="dropout_2")

    couche_sortie = keras.layers.Dense(
        nbre_classes,
        activation="softmax",
        kernel_regularizer=keras.regularizers.l2(1e-4),
        name="output_dense"
    )

    x = conv1(inputs)
    x = bn1(x)
    x = pooling1(x)

    x = conv2(x)
    x = bn2(x)
    x = pooling2(x)

    x = dropout1(x)
    x = global_pool(x)
    x = dense_hidden(x)
    x = dropout2(x)
    outputs = couche_sortie(x)

    model = keras.Model(
        inputs=inputs,
        outputs=outputs,
        name="Tiny_Embedding_Conv_Audio"
    )

    return model
