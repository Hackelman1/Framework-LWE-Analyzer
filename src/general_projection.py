import numpy as np
from typing import Dict

class GeneralProjection:
    """
    Módulo 1 de la Fase 4: Proyección Algebraica Generalizada Z_q -> Z_m.
    Transforma instancias LWE desde Z_q hacia cualquier anillo modular Z_m (m >= 2).
    Calcula el ruido efectivo observable:
    e_eff = (b_m - A_m * s_m) mod m
    """

    def __init__(self, target_modulus: int = 6):
        self.m = target_modulus

    @staticmethod
    def project_lwe(lwe_instance: Dict, m: int) -> Dict:
        """
        Proyecta los componentes de la instancia LWE a Z_m.
        """
        A = lwe_instance['A']
        b = lwe_instance['b']
        s = lwe_instance['s']
        e = lwe_instance['e']
        q = lwe_instance['q']

        Am = A % m
        bm = b % m
        sm = s % m
        em = e % m
        e_eff = (bm - Am.dot(sm)) % m

        return {
            'Am': Am,
            'bm': bm,
            'sm': sm,
            'em': em,
            'e_effective_m': e_eff,
            'q': q,
            'm': m
        }

    @staticmethod
    def compute_effective_noise(bm: np.ndarray, Am: np.ndarray, sm: np.ndarray, m: int) -> np.ndarray:
        """
        Calcula e_eff = (bm - Am * sm) mod m
        """
        return (bm - Am.dot(sm)) % m
