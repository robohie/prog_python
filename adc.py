# TRAVAIL DE FIN DE CYCLE (TFC) / Simulation avec Python
# Sujet de TFC : système de contrôle d'un moteur DC par la voix
# Bosolindo Edhiengene Roger L3 Génie électrique
# email : rogerbosolinndo34@gmail.com
# Téléphone : +243 822 460 896
# ===================================================================

# ===================================================================

import numpy as np
import matplotlib.pyplot as plt

class ADC:
    def __init__(self, resolution:int, v_ref1:float, v_ref2:float):
        """

        :param resolution: nombre des bits
        :param v_ref1: tension d'alimentation V_ref+
        :param v_ref2: tension d'alimentation V_ref-
        """
        self.bits = resolution
        self.pe = v_ref1 - v_ref2        # la pleine échelle
        self.q = self.pe / 2 ** resolution # le quantum

    def get_numeric(self, input_signal):
        entree = np.asarray(input_signal)
        sortie = []
        for value in entree:
            if value > self.pe:
                sortie.append(2 ** self.bits- 1)
                continue
            n = round(value / self.q)
            sortie.append(n)
        return sortie

    def entree_max(self):
        return self.q * (2 ** self.bits - 1)

if __name__ == "__main__":
    t = np.linspace(0, 7, 100)
    adc1 = ADC(8, 2.5, -2.5)

    sortie_analog = np.sin(t) ** 2
    sortie_adc = adc1.get_numeric(sortie_analog)

    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
    ax1.plot(t, sortie_analog)
    ax2.scatter(t, sortie_adc, c="red")

    plt.show()
