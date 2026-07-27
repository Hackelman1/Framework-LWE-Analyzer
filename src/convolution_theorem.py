import math
import numpy as np
from typing import Dict
from src.noise_model import NoiseModel
from src.subgroup_analysis import SubgroupAnalysis

class ConvolutionTheorem:
    """
    Módulo 2 de la Fase 5: Demostración del Teorema por Convolución Circular.
    Demuestra que P(e_eff) = P(e mod m) * P(k*q mod m) resulta aproximadamente uniforme
    cuando P(k mod m) es uniforme y gcd(q, m) = 1.
    """

    @staticmethod
    def circular_convolution(P: np.ndarray, Q: np.ndarray, m: int) -> np.ndarray:
        """
        Calcula la convolución circular discreta (P * Q)[r] = sum_{j=0}^{m-1} P[j] * Q[(r - j) % m].
        """
        conv = np.zeros(m, dtype=float)
        for r in range(m):
            for j in range(m):
                conv[r] += P[j] * Q[(r - j) % m]
        return conv

    @classmethod
    def verify_uniformization(cls, e_pmf: np.ndarray, wrap_pmf: np.ndarray, q: int, m: int) -> Dict:
        """
        Calcula P(k*q mod m) a partir de P(k mod m) y realiza la convolución con P(e mod m).
        Verifica si el resultado converge a la distribución uniforme en Z_m (si gcd=1) o en G(q,m) (si gcd>1).
        """
        gcd_val = math.gcd(q, m)
        is_full = (gcd_val == 1)

        # Mapear P(k mod m) a P(kq mod m)
        kq_pmf = np.zeros(m, dtype=float)
        for k_val, p_val in enumerate(wrap_pmf):
            target_res = (k_val * q) % m
            kq_pmf[target_res] += p_val

        # Convolución circular P(e mod m) * P(kq mod m)
        eff_pmf = cls.circular_convolution(e_pmf, kq_pmf, m)

        unif_pmf = np.full(m, 1.0 / m)
        noise_model = NoiseModel(mod=m)

        kl_eff_vs_unif = noise_model.kl_divergence(eff_pmf, unif_pmf)
        kl_kq_vs_unif = noise_model.kl_divergence(kq_pmf, unif_pmf)

        return {
            'q': q,
            'm': m,
            'gcd': gcd_val,
            'is_full_subgroup': is_full,
            'effective_pmf': eff_pmf.tolist(),
            'kq_pmf': kq_pmf.tolist(),
            'kl_kq_vs_uniform': float(kl_kq_vs_unif),
            'kl_effective_vs_uniform': float(kl_eff_vs_unif),
            'subgroup_size': m // gcd_val
        }
