import itertools
import numpy as np
from typing import Dict
from src.noise_model import NoiseModel

class TheoreticalIndependence:
    """
    Módulo de Análisis Teórico Simbólico / Enumeración Exacta (Fase 7):
    Evalúa la distribución conjunta exacta P(k_m, s_m) mediante enumeración completa
    sobre un espacio discreto reducido (n=1 o 2, q pequeño) para comprobar si
    I(k_m; s_m) = 0 teóricamente en ausencia de sesgos Monte Carlo.
    """

    @staticmethod
    def evaluate_exact_joint_distribution(q: int = 17, m: int = 6, n: int = 1, eta: int = 1) -> Dict:
        """
        Calcula mediante enumeración exhaustiva la PMF conjunta P(k_m, s_m).
        """
        # Generar PMF del error CBD(eta) mod q
        noise_model = NoiseModel(mod=q)
        cbd_pmf = noise_model.theoretical_cbd_pmf(eta)
        errors = np.arange(-eta, eta + 1)
        
        # Mapear errores a probabilidades
        # En CBD(eta), p(e) para e in [-eta, eta]
        # CBD(1): [-1, 0, 1] -> [0.25, 0.5, 0.25]
        # CBD(2): [-2, -1, 0, 1, 2] -> [1/16, 4/16, 6/16, 4/16, 1/16]
        if eta == 1:
            p_e_dict = {-1: 0.25, 0: 0.5, 1: 0.25}
        elif eta == 2:
            p_e_dict = {-2: 1/16, -1: 4/16, 0: 6/16, 1: 4/16, 2: 1/16}
        else:
            p_e_dict = {0: 1.0}

        joint_counts = {}
        s_counts = {}
        k_counts = {}

        total_weight = 0.0

        all_s = list(itertools.product(range(q), repeat=n))
        all_A = list(itertools.product(range(q), repeat=n))

        p_A = 1.0 / (q ** n)
        p_s = 1.0 / (q ** n)

        for s_vec in all_s:
            s_arr = np.array(s_vec)
            s_m_val = tuple(s_arr % m)
            for A_vec in all_A:
                A_arr = np.array(A_vec)
                dot_val = int(np.dot(A_arr, s_arr))
                for err, p_err in p_e_dict.items():
                    y = dot_val + err
                    k_val = int(np.floor(y / q)) % m

                    weight = p_A * p_s * p_err
                    total_weight += weight

                    joint_counts[(k_val, s_m_val)] = joint_counts.get((k_val, s_m_val), 0.0) + weight
                    s_counts[s_m_val] = s_counts.get(s_m_val, 0.0) + weight
                    k_counts[k_val] = k_counts.get(k_val, 0.0) + weight

        # Calcular información mutua teórica exactísima
        mi_exact = 0.0
        for (k_val, s_m_val), p_ks in joint_counts.items():
            p_k = k_counts[k_val]
            p_sm = s_counts[s_m_val]
            if p_ks > 0 and p_k > 0 and p_sm > 0:
                mi_exact += p_ks * np.log2(p_ks / (p_k * p_sm))

        return {
            'q': q,
            'm': m,
            'n': n,
            'eta': eta,
            'exact_MI_k_sm': float(mi_exact),
            'total_space_size': (q**n) * (q**n) * len(p_e_dict)
        }
