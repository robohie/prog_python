# TRAVAIL DE FIN DE CYCLE (TFC) / Simulation avec Python
# Sujet de TFC : système de contrôle d'un moteur DC par la voix
# Bosolindo Edhiengene Roger L3 Génie électrique
# email : rogerbosolinndo34@gmail.com
# Téléphone : +243 822 460 896
# ===================================================================
# Ce module contient les classes MicroDynamique, MicroStatique,
# Amplificateur, FiltrePasseBas et probablement FiltrePasseBande qui
# sont respectivement les implémentations quasi réelles des micro-
# phones dynamique et statique, de l'amplificateur en configuration
# non inverseuse, du filtre1 passe-bas d'ordre 1 et du filtre2 passe-
# bande.
# ===================================================================

import human_signal as h
from scipy.integrate import odeint
from scipy.interpolate import interp1d
import numpy as np

def bruit(x, amp_min=0.01, amp_max=0.1, nbre_harmonique=10):
    """Retourne un bruit au(x) temps x fourni

    :param nbre_harmonique: nombre d'harmoniques
    :param amp_min: amplitude minimale du bruit
    :param amp_max: amplitude maximale du bruit
    :param x: temps (s)
    """
    x = np.asarray(x)
    # Nous prénons une fréquence fondamentale aléatoire
    # ainsi que des amplitudes aléatoires entre amp_min
    # et amp_max
    f = np.random.uniform(2000, 5000)
    amplitudes = np.random.uniform(amp_min, amp_max, size=(nbre_harmonique, ))
    b = 0
    for k, a in enumerate(amplitudes, start=1):
        b += a * np.sin(2 * np.pi * k * f * x)
    return b

class MicroDynamique(h.TensionVoice):
    def __init__(self, r:float, f:float, amplitudes):
        """

        :param r: résistance du microphone dynamique
        :param f: fréquence du signal de sortie
        :param amplitudes: les amplitudes du signal de sorties
                           ce sont des fonctions.
        """
        super().__init__(f, *amplitudes)
        self.r = r

    def get_output(self, x, noise):
        """Renvoie le signal de sortie du
        microphone dynamique

        :param noise: bruit
        :param x: temps (s)
        """
        return self.get_signal(x) + noise

class MicroStatique(h.CapacityVariable):
    def __init__(self, r:float, vf:float, f:float, capas:tuple, phases:tuple):
        """

        :param r: résistance du microphone (ohm)
        :param vf: tension de d'alimentation du microphone (V)
        :param f: fréquence fondamentale (Hz)
        :param capas: les capacités pour chaque harmonique (F)
        :param phases: déphasage de chaque harmonique (rad)
        """
        super().__init__(f, capas, phases)
        self.r = r
        self.vf = vf
    # ============= A REVOIR ======================
    def get_output(self, x, noise):
        return self.r * self.vf * np.gradient(self.get_signal(x), x) + noise
    # =============================================

class Amplificateur:
    def __init__(self, r1:float, r2:float):
        self.gain = 1 + r2 / r1
    def get_output(self, input_signal):
        return self.gain * input_signal
    def get_vamp(self, input_signal):
        """Renvoie la tension moyenne de sortie"""
        output = self.get_output(input_signal)
        return sum(output) / len(output)
    @staticmethod
    def v_moy_given(input_signal):
        """Renvoie la tension moyenne d'entrée
        Nous la déclarons comme méthode statique
        étant donné que c'est une méthode qui
        ne dépend pas de l'instance de la classe"""
        return sum(input_signal) / len(input_signal)
    @staticmethod
    def design_r2(v_in, v_amp, r1):
        """Renvoie la résistance R2 connaissant
        les éléments suivant (c'est aussi une
        méthode statique)

        :param v_in: tension moyenne en entrée
        :param v_amp: tension moyenne de sortie
        :param r1: la résistance R1
        """
        return ((v_amp / v_in) * np.sqrt(2) - 1) * r1

class FiltrePasseBas:
    def __init__(self, c:float, fc:float):
        """

        :param c: la capacité du filtre1 passe-bas (F)
        :param fc: la fréquence de coupure (Hz)
        """
        self.r = 1 / (2 * fc * np.pi * c)    # la résistance du filtre1
        self.tau = self.r * c                # tau = R.C
        self.fc = fc

    def get_output(self, input_signal, temps):
        """
        Nous utilisons la méthode de Euler pour
        approximer la sortie
        """
        x = np.asarray(input_signal)
        x_t = interp1d(temps, x, kind="linear", fill_value="extrapolate")

        def second_membre(v, ngonga):
            return (x_t(ngonga) - v) / self.tau

        y0 = 0
        y = odeint(second_membre, y0, t)
        return y.flatten()

class IdealFiltrePB:
    """Implémentation d'un filtre passe-bas idéal"""
    def __init__(self, fc:float):
        """

        :param fc: fréquence de coupure
        """
        self.fc = fc
    def get_output(self, input_signal):
        pass

class FiltrePasseBande:
    def __init__(self):
        pass
    def get_output(self):
        pass

class IdealFiltrePBande:
    """Implémentation d'un filtre passe-bande
    idéal
    """
    def __init__(self, f1:float, f2:float):
        """

        :param f1: fréquence de coupure minimale
        :param f2: fréquence de coupure maximale
        """
        self.f1, self.f2 = f1, f2
    def get_output(self, input_signal):
        pass

if __name__ == "__main__":
    import matplotlib.pyplot as plt

    f_echantillon = 5000
    t = np.linspace(0, 1, f_echantillon)
    BRUIT = bruit(t)
    # ==============================================================================
    amps = (
        lambda x : np.sin(x),
        lambda x : np.cos(x),
        lambda x : np.cos(x) * np.sin(x)
    )
    capacities = (5e-7, 4e-7, 2e-7)
    phases_var = (np.pi / 2, np.pi, 0)
    # =================================================================
    choix = input("Micro statique (S) ou dynamique (D) : ")
    if choix.lower() == "d":
        micro = MicroDynamique(100, 20, amplitudes=amps)
    else:
        micro = MicroStatique(50, 48, 20, capacities, phases_var)
    # =================================================================
    ampli = Amplificateur(10, 9)
    filtre1 = FiltrePasseBas(500e-5, 2000)
    filtre2 = FiltrePasseBande()

    # =================================================================
    signal1 = micro.get_output(t, BRUIT)
    signal2 = ampli.get_output(signal1)
    signal3 = filtre1.get_output(signal2, t)
    # =================================================================

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True)
    ax1.plot(t, signal1)
    ax2.plot(t, signal2)
    ax3.plot(t, signal3)

    plt.tight_layout()
    plt.show()
