# Auteur : BOSOLINDO EDHIENGENE Roger
# email : rogerbosolinndo34@gmail.com
# =========================================================================
# Vérification de la précision des modèles

import numpy as np
import tensorflow as tf

def verification1(model_path, x_test, y_test):
    """Cette fonction évalue la précision du modèle non quantifié
    Inspirée du code proposé dans le livre "TinyML, Machine
    Learning with Tensorflow Lite on Arduino and Ultra-Low-Power
    Microcontroller"

    :param model_path: un chemin qui conduit vers un modèle tflite
    :param x_test: le jeu des données de test
    :param y_test: le jeu d'étiquettes correspondantes.
    """
    # On instancie l'interpréteur de notre modèle
    interpreteur = tf.lite.Interpreter(model_path=model_path)

    # Allocation de la memoire pour le modèle
    interpreteur.allocate_tensors()

    # Obtention des index pour les entrées et les sorties
    index_sortie_model = interpreteur.get_output_details()[0]["index"]

    index_input_model = interpreteur.get_input_details()[0]["index"]

    # nombre de prédictions correctes
    correct = 0

    # Exécution de l'interpréteur pour chaque valeur (x_test_i, y_test_i)
    for i, value in enumerate(x_test):
        tenseur = np.expand_dims(value, axis=0)
        tenseur.astype(np.float32)
        # Écrire dans les tenseurs d'entrée
        interpreteur.set_tensor(index_input_model, tenseur)
        # Inférence
        interpreteur.invoke()
        prediction = interpreteur.get_tensor(index_sortie_model)[0]

        if np.argmax(prediction) == y_test[i]: # Car la prédiction est une liste des scores
            correct += 1

    return correct / len(y_test)

def verification2(model_q_path, x_test, y_test):
    """Cette fonction évalue la précision du modèle quantifié
    Inspirée du code proposé dans le livre "TinyML, Machine
    Learning with Tensorflow Lite on Arduino and Ultra-Low-Power
    Microcontroller"

    :param model_q_path: le chemin vers le modèle quantifié
    :param x_test: le jeu de données de test
    :param y_test: le jeu d'étiquettes correspondantes.
    """
    interpreteur = tf.lite.Interpreter(model_path=model_q_path) # Interpréteur
    interpreteur.allocate_tensors() # Allocation de la memoire pour le modèle

    input_info = interpreteur.get_input_details()
    output_info = interpreteur.get_output_details()

    input_scale = input_info[0]["quantization"][0]
    input_zp = input_info[0]["quantization"][1]

    output_scale = output_info[0]["quantization"][0]
    output_zp = output_info[0]["quantization"][1]

    correct = 0
    for i, value in enumerate(x_test):
        tenseur = np.expand_dims(value, axis=0)
        tenseur.astype(np.float32)
        value_q = np.clip(tenseur/input_scale + input_zp, -128, 127).astype(np.int8)

        interpreteur.set_tensor(input_info[0]["index"], value_q)
        interpreteur.invoke()
        sortie_q = interpreteur.get_tensor(output_info[0]["index"])

        # Dequantization
        sortie = (sortie_q.astype(np.float32) - output_zp) * output_scale
        if np.argmax(sortie) == y_test[i]:
            correct += 1

    print(f"Type de l'entrée : dtype={input_info[0]["dtype"]}, "
          f"scale={input_scale:.6f}, zero_pt={input_zp}")
    print(f"Type de sortie   : dtype={output_info[0]["dtype"]}, "
          f"scale={output_scale:.6f}, zero_pt={input_zp}")

    return correct / len(y_test)
