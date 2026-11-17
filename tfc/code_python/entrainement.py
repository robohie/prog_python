# Auteur : BOSOLINDO EDHIENGENE Roger
# mail : rogerbosolinndo34@gmail.com
# ========================================================
# Ce module contient les fonctions nécessaires pour entraîner
# un modèle TinyML pour ce projet de fin de cycle, tracer les
# courbes d'apprentissage et le sauvegarder.

import matplotlib.pyplot as plt
import tensorflow as tf
import os
import numpy as np

from tensorflow import keras
from typing import List


def resume_and_training(model:keras.Model,
             loss:str,
             metrics:List[str],
             optimiseur,
             epoques:int,
             dict_data:dict,
             rappels:list):
    """

    :param model: le modèle à entraîner
    :param loss: la fonction de coût
    :param metrics: les mesures à réaliser durant l'entrainement
    :param optimiseur: la méthode d'optimisation
    :param epoques: le nombre d'époques
    :param dict_data: les données de validation, d'entraînement et de test
    :param rappels: les rappels
    :return:
    """
    model.compile(
        loss=loss,
        metrics=metrics,
        optimizer=optimiseur
    )
    model.summary()

    question = input("Taper sur un caractère pour commencer l'entrainement: ")
    if not question:
        return model
    deroulement = model.fit(
        x=dict_data['x_train'],
        y=dict_data['y_train'],
        epochs=epoques,
        validation_data=(
            dict_data['x_val'],
            dict_data['y_val']
        ),
        callbacks=rappels
    )
    return model, deroulement

def plot_courbes_learning(deroulement):
    """
    Cette fonction permet de tracer les courbes d'apprentissage
    à partir de l'objet History renvoyé par la méthode fit
    de la classe Model.

    :param deroulement: la valeur de retour de la méthode fit
    :return:
    """
    perte = deroulement.history["loss"]
    val_perte = deroulement.history["val_loss"]

    precision = deroulement.history["accuracy"]
    val_precision = deroulement.history["val_accuracy"]

    epochs = range(1, 1 + len(perte))

    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
    plt.title("Courbes d'apprentissage")

    ax1.plot(epochs, perte, label="loss")
    ax1.plot(epochs, val_perte, label="val_loss")
    ax1.legend()
    ax1.grid()

    ax2.plot(epochs, precision, label="Accuracy")
    ax2.plot(epochs, val_precision, label="Val_Accuracy")
    ax2.legend()
    ax2.grid()

def save_non_quantized(model:keras.Model, folder, filename):
    """
    Cette méthode permet de sauvegarder un modèle TinyML non
    quantifié.

    :param model:
    :param folder:
    :param filename:
    :return:
    """
    chemin = os.path.join(folder, filename)
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    tflite_model = converter.convert()

    with open(chemin, "wb") as file:
        file.write(tflite_model)

def save_quantized(model:keras.Model, folder, filename, x_test):
    """
    Cette méthode similaire à save_non_quantized permet
    de sauvegarder un modèle quantifié, très important pour
    un fonctionnement sur microcontrôleur.

    :param model:
    :param folder:
    :param filename:
    :param x_test: Le jeu de données de test.
    :return:
    """
    chemin = os.path.join(folder, filename)
    # fonction génératrice
    def generator():
        for value in x_test:
            new_value = np.expand_dims(value, axis=0)
            yield [new_value.astype(np.float32)]

    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT] # model quantifié

    converter.representative_dataset = generator
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
    converter.inference_input_type = tf.int8
    converter.inference_output_type = tf.int8

    tflite_model = converter.convert()
    with open(chemin, "wb") as file:
        file.write(tflite_model)
