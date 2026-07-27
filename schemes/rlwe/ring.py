import numpy as np

class PolynomialRing:
    """
    Operaciones en el anillo R_q = Z_q[x] / (x^N + 1).
    Soporta polinomios de grado N-1 con reducción por x^N + 1 (negacycle convolution).
    """

    def __init__(self, N: int = 256, q: int = 3329):
        self.N = N
        self.q = q

    def poly_mul(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """
        Multiplicación de polinomios en Z_q[x] / (x^N + 1).
        a, b son arreglos de coeficientes de tamaño N.
        """
        res = np.zeros(2 * self.N - 1, dtype=int)
        for i in range(self.N):
            for j in range(self.N):
                res[i + j] = (res[i + j] + int(a[i]) * int(b[j])) % self.q

        # Reducción x^N = -1 (negacyclic)
        c = np.zeros(self.N, dtype=int)
        for i in range(self.N):
            c[i] = res[i]
        for i in range(self.N - 1):
            c[i] = (c[i] - res[i + self.N]) % self.q

        return c % self.q

    def poly_add(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        return (a + b) % self.q

    def poly_sub(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        return (a - b) % self.q
