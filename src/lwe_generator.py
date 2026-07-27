import numpy as np

class LWEGenerator:
    """
    Módulo 1: Generador de Instancias LWE.
    Soporta la generación de instancias LWE realistas con secreto uniforme,
    matriz pública uniforme y ruido con Distribución Binomial Centrada (CBD).
    """

    def __init__(self, n: int, m: int, q: int = 3329, eta: int = 2, seed: int = None):
        """
        :param n: Dimensión secreta
        :param m: Número de muestras
        :param q: Módulo (por defecto 3329, tipo Kyber)
        :param eta: Parámetro CBD (por defecto 2)
        :param seed: Semilla opcional para reproducibilidad
        """
        self.n = n
        self.m = m
        self.q = q
        self.eta = eta
        if seed is not None:
            np.random.seed(seed)

    @staticmethod
    def sample_cbd(eta: int, size: int) -> np.ndarray:
        """
        Muestra valores de una Distribución Binomial Centrada CBD(eta).
        e = sum_{i=1}^{eta} a_i - sum_{i=1}^{eta} b_i, donde a_i, b_i in {0, 1}
        Rango de salida: [-eta, eta]
        """
        a = np.random.randint(0, 2, size=(eta, size))
        b = np.random.randint(0, 2, size=(eta, size))
        return np.sum(a, axis=0) - np.sum(b, axis=0)

    def generate_instance(self):
        """
        Genera una instancia LWE:
        s <- U(Z_q^n)
        A <- U(Z_q^{m x n})
        e <- CBD(eta)^m
        b = A*s + e (mod q)

        :return: dict con s, A, b, e
        """
        s = np.random.randint(0, self.q, size=self.n)
        A = np.random.randint(0, self.q, size=(self.m, self.n))
        e = self.sample_cbd(self.eta, self.m)
        
        # b = A*s + e mod q
        b = (A.dot(s) + e) % self.q

        return {
            's': s,
            'A': A,
            'b': b,
            'e': e,
            'n': self.n,
            'm': self.m,
            'q': self.q,
            'eta': self.eta
        }
