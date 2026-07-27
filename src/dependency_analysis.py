import numpy as np
from typing import Dict, Tuple
from src.lwe_generator import LWEGenerator
from src.general_projection import GeneralProjection
from src.mutual_info import MutualInformationCalculator

class DependencyAnalysis:
    """
    Módulo de Análisis de Dependencias Laterales de k (Fase 6):
    Estudia experimentalmente la independencia condicional de k mod m frente a s_m y A_m.
    Calcula Información Mutua (Miller-Madow), Correlación de Pearson y Distancia Estadística Condicional.
    """

    def __init__(self, mod: int = 6):
        self.m = mod

    def evaluate_k_dependencies(self, q: int = 3329, m: int = 6, n: int = 2, 
                                trials: int = 1000, eta: int = 2, seed: int = None) -> Dict:
        """
        Calcula I(k_m; s_m), I(k_m; A_m), correlación de Pearson y distancia estadística condicional.
        """
        if seed is not None:
            np.random.seed(seed)

        generator = LWEGenerator(n=n, m=trials, q=q, eta=eta)
        inst = generator.generate_instance()

        s = inst['s']
        A = inst['A']
        e = inst['e']

        y = A.dot(s) + e
        k_raw = np.floor(y / q).astype(int)
        k_m = k_raw % m

        s_m = s % m
        A_m = A % m

        # Repetir s_m para aparear con cada muestra i en 0..trials-1
        s_m_repeated = np.tile(s_m[0], trials) % m
        A_m_flat = A_m[:, 0] % m

        mi_calc = MutualInformationCalculator(mod=m)

        # Información Mutua con corrección Miller-Madow
        mi_k_s = mi_calc.miller_madow_mi(k_m, s_m_repeated)
        mi_k_A = mi_calc.miller_madow_mi(k_m, A_m_flat)

        # Correlación de Pearson
        corr_k_s = float(np.corrcoef(k_m, s_m_repeated)[0, 1]) if trials > 1 else 0.0
        corr_k_A = float(np.corrcoef(k_m, A_m_flat)[0, 1]) if trials > 1 else 0.0

        # Distancia Estadística Condicional: E_s [ d_stat( P(k | s) || P(k) ) ]
        k_uncond_pmf = np.bincount(k_m, minlength=m) / trials

        unique_s, s_counts = np.unique(s_m_repeated, return_counts=True)
        cond_distances = []

        for val_s in unique_s:
            k_s = k_m[s_m_repeated == val_s]
            if len(k_s) > 0:
                k_cond_pmf = np.bincount(k_s, minlength=m) / len(k_s)
                d_stat = float(0.5 * np.sum(np.abs(k_cond_pmf - k_uncond_pmf)))
                cond_distances.append(d_stat * (len(k_s) / trials))

        mean_cond_dstat = float(np.sum(cond_distances))

        return {
            'q': q,
            'm': m,
            'n': n,
            'trials': trials,
            'MI_k_sm': mi_k_s,
            'MI_k_Am': mi_k_A,
            'corr_k_sm': corr_k_s,
            'corr_k_Am': corr_k_A,
            'mean_cond_dstat': mean_cond_dstat
        }
