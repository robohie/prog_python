# Vérification de la précision des modèles
import numpy as np
import tensorflow as tf

def verification1(model_path, x_test, y_test):
    """Cette fonction évalue la précision du modèle non quantifié

    * model_path est un chemin qui conduit vers un modèle tflite
    * x_test est le jeu des données de test
    * y_test est le jeu d'étiquettes correspondantes.
    """
    # On instancie les interpréteurs pour nos modèles
    interpreteur = tf.lite.Interpreter(model_path=model_path)

    # Allocation de la memoire pour le modèle
    interpreteur.allocate_tensors()

    # Obtention des index pour les entrées et les sorties
    index_sortie_model = interpreteur.get_output_details()[0]["index"]

    index_input_model = interpreteur.get_input_details()[0]["index"]

    # Prédiction correcte
    correct = 0

    # Exécuter chaque interpréteur pour chaque valeur
    for value in x_test:
        value.astype(np.float32)
        # Ecrire dans les tenseurs d'entrée
        interpreteur.set_tensor(index_input_model, value)
        # Inférence
        interpreteur.invoke()
        prediction = interpreteur.get_tensor(index_sortie_model)[0]

        if np.argmax(prediction) == np.argmax(y_test[x_test.index(value)]):
            correct += 1

    return correct / len(y_test)

def verification2(model_q_path, x_test, y_test):
    """Cette fonction évalue la précision du modèle quantifié

    * model_q_path est le chemin vers le modèle quantifié
    * x_test est le jeu de données de test
    * y_test est le jeu d'étiquettes correspondantes.
    """
    interpreteur = tf.lite.Interpreter(model_path=model_q_path) # Interpréteur
    interpreteur.allocate_tensors() # Allocation de la memoire pour le modèle

    input_details = interpreteur.get_input_details()
    output_details = interpreteur.get_output_details()

    input_scale = input_details[0]["quantization"][0]
    input_zp = input_details[0]["quantization"][1]

    output_scale = output_details[0]["quantization"][0]
    output_zp = output_details[0]["quantization"][1]

    print(f"Type de l'entrée : dtype={input_details[0]["dtype"]}, "
          f"scale={input_scale:.6f}, zero_pt={input_zp}")
    print(f"Type de sortie   : dtype={output_details[0]["dtype"]}, "
          f"scale={output_scale:.6f}, zero_pt={input_zp}")

    correct = 0
    for value in x_test:
        value.astype(np.float32)
        value_q = np.clip(value/input_scale + input_zp, -128, 127).astype(np.int8)

        interpreteur.set_tensor(input_details[0]["index"], value_q)
        interpreteur.invoke()
        sortie_q = interpreteur.get_tensor(output_details[0]["index"])

        # Dequantization
        sortie = (sortie_q.astype(np.float32) - output_zp) * output_scale
        if np.argmax(sortie) == np.argmax(y_test[x_test.index(value)]):
            correct += 1

    return correct / len(y_test)
