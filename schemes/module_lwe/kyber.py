import numpy as np
from typing import Dict
from schemes.rlwe.ring import PolynomialRing
from schemes.module_lwe.parameters import KyberParams, KYBER_512

class ModuleLWEGenerator:
    """
    Generador de Instancias Module-LWE / ML-KEM (Kyber).
    b = A * s + e en (Z_q[x] / (x^N + 1))^k
    """

    def __init__(self, params: KyberParams = KYBER_512, seed: int = None):
        self.params = params
        self.ring = PolynomialRing(N=params.n, q=params.q)
        self.seed = seed

    def sample_cbd_poly(self, eta: int) -> np.ndarray:
        """
        Muestra un polinomio con coeficientes distribuidos según CBD(eta).
        """
        a = np.random.binomial(eta, 0.5, size=self.params.n)
        b = np.random.binomial(eta, 0.5, size=self.params.n)
        return (a - b) % self.params.q

    def generate_instance(self) -> Dict:
        """
        Genera A (k x k de polinomios), s (k polinomios), e (k polinomios) y b = A*s + e.
        """
        if self.seed is not None:
            np.random.seed(self.seed)

        k = self.params.k
        N = self.params.n
        q = self.params.q

        # A es k x k matriz de polinomios de grado N-1
        A = np.random.randint(0, q, size=(k, k, N))

        # s y e son vectores de k polinomios con ruido CBD
        s = np.zeros((k, N), dtype=int)
        e = np.zeros((k, N), dtype=int)

        for i in range(k):
            s[i] = self.sample_cbd_poly(self.params.eta1)
            e[i] = self.sample_cbd_poly(self.params.eta2)

        # b = A * s + e (multiplicación matricial polinómica)
        b = np.zeros((k, N), dtype=int)
        for i in range(k):
            acc = np.zeros(N, dtype=int)
            for j in range(k):
                prod = self.ring.poly_mul(A[i, j], s[j])
                acc = self.ring.poly_add(acc, prod)
            b[i] = self.ring.poly_add(acc, e[i])

        return {
            'A': A,
            's': s,
            'e': e,
            'b': b,
            'params': self.params
        }
