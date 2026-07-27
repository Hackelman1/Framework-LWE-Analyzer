import numpy as np
from typing import Dict

class ModuleProjection:
    """
    Transformación de Proyección Modular sobre Module-LWE:
    Proyecta coeficientes polinómicos de b_i(x) y (A*s)_i(x) mod m.
    Calcula el ruido efectivo polinómico: e_eff,i(x) = (b_m,i(x) - (A_m * s_m)_i(x)) mod m
    """

    @staticmethod
    def project_instance(inst: Dict, m: int) -> Dict:
        """
        Proyecta la instancia Module-LWE al anillo R_m = Z_m[x]/(x^N + 1).
        """
        A = inst['A']
        s = inst['s']
        b = inst['b']
        ring = inst['params']
        N = ring.n
        q = ring.q
        k = ring.k

        A_m = A % m
        s_m = s % m
        b_m = b % m

        # Recalcular (A_m * s_m) mod m usando aritmética reducida
        As_m = np.zeros((k, N), dtype=int)
        for i in range(k):
            acc = np.zeros(N, dtype=int)
            for j in range(k):
                # Multiplicación polinómica negacíclica mod m
                res_full = np.zeros(2 * N - 1, dtype=int)
                for i_deg in range(N):
                    for j_deg in range(N):
                        res_full[i_deg + j_deg] = (res_full[i_deg + j_deg] + int(A_m[i, j, i_deg]) * int(s_m[j, j_deg])) % m

                c = np.zeros(N, dtype=int)
                for deg in range(N):
                    c[deg] = res_full[deg]
                for deg in range(N - 1):
                    c[deg] = (c[deg] - res_full[deg + N]) % m

                acc = (acc + c) % m
            As_m[i] = acc % m

        e_effective_m = (b_m - As_m) % m

        # Extraer todos los coeficientes del polinomio como muestras 1D
        coeff_samples = e_effective_m.flatten()

        return {
            'A_m': A_m,
            's_m': s_m,
            'b_m': b_m,
            'e_effective_m': e_effective_m,
            'coeff_samples': coeff_samples,
            'm': m
        }
