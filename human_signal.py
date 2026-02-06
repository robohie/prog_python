# TRAVAIL DE FIN DE CYCLE (TFC) / Simulation avec Python
# Sujet de TFC : système de contrôle d'un moteur DC par la voix
# Bosolindo Edhiengene Roger L3 Génie électrique
# email : rogerbosolinndo34@gmail.com
# Téléphone : +243 822 460 896
# ===================================================================
# Ce module contient deux classes qui implémentent le fonctionnement
# respectivement de deux microphones idéaux i.e. sans bruit à savoir
# le microphone dynamique et le microphone statique,
# que nous avons analysés.
# ===================================================================

import numpy as np

ERREUR1 = "La fondamentale d'un son humain doit être entre 20 Hz et 2 kHz"

class TensionVoice:
    """
    Cette classe implémente le fonctionnement d'un microphone
    dynamique idéal. Pour ce faire, nous l'avons considéré
    comme une source tension générant un signal composé en
    considérant plusieurs harmoniques et une fondamentale
    donnée qui serait la fondamentale de la voix humaine
    """
    def __init__(self, f:float, *enveloppes):
        """

        :param f: fréquence fondamentale (Hz)
        :param enveloppes: les amplitudes variables (des fonctions)
        """
        if not 20<=f<=2000:
            # On lève une exception si la fondamentale ne correspond
            # pas à celle d'un son audible et humain
            raise ValueError(f"{ERREUR1}\nMais {f} a été donnée!")
        self.f = f
        self.enveloppes = enveloppes
    def get_signal(self, x):
        """Renvoie le signal de sortie de fréquence
        fondamentale self.f et d'amplitudes self.enveloppes

        :param x: temps (s)
        """
        x = np.asarray(x)                  # conversion de x en array
        s = np.zeros_like(x, dtype=float)  # la sortie
        for k, env in enumerate(self.enveloppes, start=1):
            s+=env(x) * np.sin(2*np.pi*self.f*k*x)
        return s

class CapacityVariable(TensionVoice):
    """
    Cette classe implémente le fonctionnement d'un microphone
    statique idéal. Pour ce faire, nous l'avons considéré
    comme formé d'une capacité qui varie de la même façon
    que l'excitation de la membrane du microphone. Sa vraie
    implémentation sera faite dans le module voice_contrôle.py
    """
    def __init__(self, f:float, capas:tuple, phases:tuple):
        """

        :param f: fréquence fondamentale (Hz)
        :param capas: valeurs des capacités pour chaque harmonique
        :param phases: les déphasages de chaque harmonique
        """
        super().__init__(f, *capas)
        self.phases = np.asarray(phases)
    def get_signal(self, x):
        """Renvoie la capacité variable de fréquence fondamentale
        self.f, ayant des amplitudes et de déphasages donnés

        :param x: temps (s)
        """
        x = np.asarray(x)
        s = np.zeros_like(x, dtype=float)
        for k, (capa, phase) in enumerate(zip(self.enveloppes, self.phases), start=1):
            s+=capa * np.sin(2 * np.pi * self.f * x * k + phase)
        return s

if __name__ == "__main__":
    # Tests du module
    import matplotlib.pyplot as plt

    t = np.linspace(0, 1, 1000)
    # ================================================================================
    amplitudes = (
        lambda x : 5 * np.exp(-x) * np.sin(x),
        lambda x : 10 * np.cos(x),
        lambda x : 4 * np.cos(x) * np.sin(x)
                  )
    capacities = (1e-6, 10e-6, 0.1e-6, 1e-7, 20e-6, 1e-9)
    les_phases = (np.pi, 0, np.pi / 2, 0, 0, 0)
    # ================================================================================
    tension = TensionVoice(20, *amplitudes)
    capa_variable = CapacityVariable(20, capacities, les_phases)

    signal1 = tension.get_signal(t)
    signal2 = capa_variable.get_signal(t)
    # ================================================================================
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
    ax1.plot(t, signal1) ; ax1.set_title("Tension")
    ax2.plot(t, signal2) ; ax2.set_title("Capacité variable")

    plt.show()
