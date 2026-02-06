import voice_controle as voice
import adc
import numpy as np
import matplotlib.pyplot as plt

f_echantillon = 5000
t = np.linspace(0, 1, f_echantillon)
BRUIT = voice.bruit(t)
# ==============================================================================
amps = (
        lambda x : np.sin(x),
        lambda x : np.cos(x),
        lambda x : np.cos(x) * np.sin(x)
    )

micro = voice.MicroDynamique(50, 5, amps)
ampli = voice.Amplificateur(10, 9)
filtre = voice.FiltrePasseBas(400e-6)
can = adc.ADC(16, 5, -5)

signal_micro = micro.get_output(t, BRUIT)
signal_ampli = ampli.get_output(signal_micro)
signal_filtre = filtre.get_output(signal_ampli, f_echantillon)
signal_adc = can.get_numeric(signal_filtre)

fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
ax1.scatter(t, signal_adc, c="red")
ax2.plot(t, signal_filtre)

plt.tight_layout()
plt.show()