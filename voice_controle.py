# TRAVAIL DE FIN DE CYCLE (TFC) / Simulation avec Python
# Sujet de TFC : système de contrôle d'un moteur DC par la voix
# Bosolindo Edhiengene Roger L3 Génie électrique
# Faculté polytechnique de l'université de Kinshasa
# email : rogerbosolinndo34@gmail.com
# Téléphone : +243 822 460 896
# ===================================================================
# Ce module contient les classes MicroDynamique, MicroStatique,
# Amplificateur, FiltrePasseBasOrdre1 et CelluleOrdre2 qui
# ===================== INTRODUCTION ===============================
# MicroDynamique est la classe, héritant de human_signal.TensionVoice,
# qui implémente un microphone dynamique.
# MicroStatique est la classe, héritant de human_signal.CapacityVariable
# qui implément quant à lui, un microphone statique.
# La classe Amplificateur est l'implémentation d'un système
# d'amplification non inverseur.
# La classe FiltrePasseBasOrdre1 simule un filtre RC.
# La classe CelluleOrdre2 simule une configuration de Sallen-Kay pour
# un filtre passe-bas de gain unitaire
# ===================================================================

import human_signal as h
import numpy as np
from scipy import signal

def bruit(x, sigma=0.05):
    n = len(x)
    freqs = np.fft.rfftfreq(n)
    freqs[0] = 1
    spectre = np.random.randn(len(freqs)) / np.sqrt(freqs)
    return np.fft.irfft(spectre, n) * sigma

class MicroDynamique(h.TensionVoice):
    def __init__(self, r:float, f:float, amplitudes):
        """

        :param r: résistance du microphone dynamique
        :param f: fréquence du signal de sortie
        :param amplitudes: les amplitudes du signal de sorties
                           (ce sont des fonctions).
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

    @staticmethod
    def derivee(y, x):
        """Cette méthode statique calcul la dérivée
        d'une fonction dont on connait les images y
        ainsi que les antécédents x

        Nous nous sommes inspirés du cours proposé dans
        le site cpge.frama.io
        """
        y, x = np.asarray(y), np.asarray(x)
        if len(y) != len(x):
            raise ValueError("Pour utiliser derivee(y, x), y et x doivent être de la même taille")
        return np.gradient(y, x)

    def get_output(self, x, noise):
        return self.r * self.vf * self.derivee(self.get_signal(x), x) + noise

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
        gain = v_amp / v_in
        return (gain - 1) * r1

class FiltrePasseBasOrdre1:
    def __init__(self, c: float, fc: float):
        """
        :param c: la capacité du filtre passe-bas (F)
        :param fc: la fréquence de coupure (Hz)
        """
        self.r = 1 / (2 * fc * np.pi * c)    # la résistance du filtre
        self.tau = self.r * c                # tau = R.C
        self.fc = fc

    def get_output(self, input_signal, temps):
        """
        Filtre passe-bas d'ordre 1
        Utilise la solution analytique discrète :
        y[n] = y[n-1] * exp(-dt / tau) + x[n] * dt

        :param input_signal: tableau des échantillons d'entrée
        :param temps: tableau des instants correspondants aux échantillons
        :return: tableau des échantillons de sortie filtrée
        """
        x = np.asarray(input_signal, dtype=float)
        temps = np.asarray(temps, dtype=float)

        if x.shape != temps.shape:
            raise ValueError("input_signal et temps doivent avoir la même forme")

        n = x.size
        if n == 0:
            return np.array([], dtype=float)

        y = np.empty_like(x)
        y[0] = 0.0  # la condition initiale

        for i in range(1, n):
            dt = temps[i] - temps[i - 1]
            if dt <= 0:
                raise ValueError("les valeurs de 'temps' décroissantes")
            alpha = np.exp(-dt / self.tau)
            y[i] = y[i - 1] * alpha + (1 - alpha) * x[i]

        return y

class CelluleOrdre2:
    """Cette classe implémente une cellule
    de Sallen et Key
    Cette partie du programme est à grande
    partie issu de Claude.AI qui nous a aidé
    à régler le problème de 'Overflow'"""
    def __init__(self, c2:float, q0:float, w0:float):
        """

        :param c2: La capacité N°2 de la cellule
        :param q0: Le facteur de qualité
        :param w0: La fréquence de résonance
        """
        if w0 <= 0:
            raise ValueError
        if q0 <= 0:
            raise ValueError
        if c2 <= 0:
            raise ValueError
        self.w0 = w0
        self.c2 = c2
        self.c1 = 4 * c2 * q0 ** 2   # La capacité N°1 de la cellule
        self.r = 1 / (2 * q0 * self.w0 * c2)  # La résistance de la cellule
        self.q0 = q0
    def get_output(self, input_signal, temps):
        """Filtre le signal d'entrée et retourne le signal de sortie.
        """
        v = np.asarray(input_signal, dtype=float)
        temps = np.asarray(temps, dtype=float)

        if v.shape != temps.shape:
            raise ValueError
        n = v.size
        if n <= 1:
            return np.array([], dtype=float)
        dt = np.mean(np.diff(temps))
        if dt <= 0:
            raise ValueError
        fs = 1 / dt

        b_analog = [self.w0 ** 2]
        a_analog = [1, self.w0 / self.q0, self.w0 ** 2]

        b_digit, a_digit = signal.bilinear(b_analog, a_analog, fs=fs)
        return signal.lfilter(b_digit, a_digit, v)
# ================================================================================================

class AnalogPart:
    """Cette classe utilise toutes les classes définies précédemment :
    MicroDynamique ou MicroStatique, Amplificateur, FiltrePasseBasOrdre1
    et CelluleOrdre2, pour mettre en place l'implémentation finale
    du système d'acquisition de la voix. Le filtre considéré est une
    approximation d'ordre 5 de Chebyshev i.e. une cellule d'ordre 1 en
    cascade avec 2 cellules d'ordre 2
    """
    def __init__(self, r1, r2, c1, fc, c2, c3):
        self.q1 = np.sqrt(2.097 / 1.23 ** 2)  # facteur de qualité pour CelluleOrdre2 1
        self.q2 = np.sqrt(0.965 / 0.216 ** 2)  # facteur de qualité pour CelluleOrdre2 2
        self.w1 = 2 * np.pi * fc / np.sqrt(2.097)
        self.w2 = 2 * np.pi * fc / np.sqrt(0.965)

        self.amplificateur = Amplificateur(r1, r2)
        self.cellule1 = FiltrePasseBasOrdre1(c1, fc)
        self.cellule2 = CelluleOrdre2(c2, self.q1, self.w1)
        self.cellule3 = CelluleOrdre2(c3, self.q2, self.w2)

    def get_output(self, input_signal, temps):
        sortie1 = self.amplificateur.get_output(input_signal)
        sortie2 = self.cellule1.get_output(sortie1, temps)
        sortie3 = self.cellule2.get_output(sortie2, temps)
        sortie4 = self.cellule3.get_output(sortie3, temps)

        return sortie4

if __name__ == "__main__":
    pass