# TRAVAIL DE FIN DE CYCLE (TFC) / Simulation avec Python
# Sujet de TFC : système de contrôle d'un moteur DC par la voix
# Bosolindo Edhiengene Roger L3 Génie électrique
# Faculté polytechnique de l'université de Kinshasa
# email : rogerbosolinndo34@gmail.com
# Téléphone : +243 822 460 896
# ===================================================================
# Ce module contient les classes MicroDynamique, MicroStatique,
# Amplificateur, FiltrePasseBasOrdre1 et FiltrePasseBande qui
# sont respectivement les implémentations quasi réelles des micro-
# phones dynamique et statique, de l'amplificateur en configuration
# non inverseuse, du filtre passe-bas d'ordre 1 et du filtre passe-
# bande.
# ===================================================================

import human_signal as h
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
    # ainsi que des amps aléatoires entre amp_min
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
        der = []
        for i in range(len(y) - 1):
            dy = y[i+1] - y[i]
            dx = x[i+1] - x[i]
            der.append(dy / dx)
        else:
            # ce qui suit est fait afin de permettre à liste der
            # d'avoir le même nombre d'élément que y et x pour ne
            # pas faire bugger la suite du programme
            der.append(der[-1])

        return np.array(der)

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
        return ((v_amp / v_in) * np.sqrt(2) - 1) * r1

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
            y[i] = y[i - 1] * alpha + x[i] * dt

        return y

class CelluleOrdre2:
    """Cette classe implémente une cellule
    de Sallen et Key"""
    def __init__(self, c2:float, q0:float, w0:float):
        """

        :param c2: La capacité N°2 de la cellule
        :param q0: Le facteur de qualité
        :param w0: La fréquence de résonance
        """
        self.w0 = w0
        self.c2 = c2
        self.c1 = 4 * c2 * q0 ** 2   # La capacité N°1 de la cellule
        self.r = 1 / (2 * q0 * self.w0 * c2)  # La résistance de la cellule
        self.q0 = q0

    def get_output(self, input_signal, temps):
        v = np.asarray(input_signal, dtype=float)
        temps = np.asarray(temps, dtype=float)

        if v.shape != temps.shape:
            raise ValueError("input_signal et temps doivent avoir la même forme")

        n = v.size
        if n==0 or n==1:
            return np.array([], dtype=float)
        u = np.zeros_like(v)
        du = np.zeros_like(v)  # dérivée prémière
        w0, q = self.w0, self.q0
        for i in range(1, n):
            dt = temps[i] - temps[i - 1]
            if dt <= 0:
                raise ValueError("les valeurs de 'temps' décroissantes")
            d2u = w0**2 * (v[i-1] - u[i-1]) - (w0 / q) * du[i-1]
            du[i] = du[i-1] + dt * d2u
            u[i] = u[i-1] + dt * du[i]

        return u


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
    capacities = (5e-7, 4e-7, 2e-7, 1e-7, 2.5e-7)
    phases_var = (np.pi / 2, np.pi, 0, 0, 0)
    # =================================================================
    choix = input("Micro statique (S) ou dynamique (D) : ")
    if choix.lower() == "d":
        micro = MicroDynamique(100, 20, amplitudes=amps)
    else:
        micro = MicroStatique(100, 48, 20, capacities, phases_var)
    # =================================================================
    ampli = Amplificateur(10, 9)
    filtre1 = FiltrePasseBasOrdre1(500e-6, 2000)
    filtre2 = CelluleOrdre2(500e-6, 0.5, 500 * np.pi * 2)
    # =================================================================
    signal1 = micro.get_output(t, BRUIT)
    signal2 = ampli.get_output(signal1)
    signal3 = filtre1.get_output(signal2, t)
    signal4 = filtre2.get_output(signal2, t)
    # =================================================================

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True)
    ax1.plot(t, signal2)
    ax2.plot(t, signal3)
    ax3.plot(t, signal4)

    plt.tight_layout()
    plt.show()
