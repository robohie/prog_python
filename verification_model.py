# Test du modèle tflite sur les données de validation
import numpy as np
import tensorflow as tf

X_val = np.load("data_validation.npy")
y_val = np.load("label_validation.npy")

interpreteur = tf.lite.Interpreter(model_path="model_quantified.tflite")
interpreteur.allocate_tensors()

input_details = interpreteur.get_input_details()
output_details = interpreteur.get_output_details()

input_scale = input_details[0]["quantization"][0]
input_zp = input_details[0]["quantization"][1]
output_scale = output_details[0]["quantization"][0]
output_zp = output_details[0]["quantization"][1]

print(f"Entrée : dtype={input_details[0]["dtype"]}, "
      f"scale={input_scale:.6f}, zero_pt={input_zp}")
print(f"Sortie : dtype={output_details[0]["dtype"]}, "
      f"scale={output_scale:.6f}, zero_pt={input_zp}")

# Evaluer la précision du modèle quantifié
correct = 0
for i in range(len(X_val)):
    # Quantifier l'entrée: float32 -> int8
    inp = X_val[i:i+1].astype(np.float32)
    inp_q = np.clip(inp/input_scale + input_zp, -128, 127).astype(np.int8)
    interpreteur.set_tensor(input_details[0]["index"], inp_q)
    interpreteur.invoke()
    out_q = interpreteur.get_tensor(output_details[0]["index"])
    # Dequantifier la sortie pour avoir les probabilités
    out_f = (out_q.astype(np.float32) - output_zp) * output_scale
    if np.argmax(out_f) == np.argmax(y_val[i]):
        correct += 1

print(f"Précision modèle quantifié : {correct/len(X_val)*100:.2f}%")