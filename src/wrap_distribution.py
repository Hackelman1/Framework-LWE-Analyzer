import numpy as np
from scipy import stats
from scipy.stats import chisquare
from typing import Dict, Tuple
from src.lwe_generator import LWEGenerator
from src.noise_model import NoiseModel

class WrapDistribution:
    """
    Módulo 1 de la Fase 5: Análisis Probabilístico del Término de Envoltorio.
    k = floor((A * s + e) / q) mod m
    Estudia experimentalmente la PMF de k mod m y su convergencia a la uniforme U(Z_m).
    """

    def __init__(self, mod: int = 6):
        self.mod = mod

    @staticmethod
    def sample_wrap_variable(q: int, m: int, n: int = 2, trials: int = 1000, 
                             eta: int = 2, seed: int = None) -> np.ndarray:
        """
        Genera instancias LWE y extrae k = floor((A*s + e) / q) mod m.
        """
        if seed is not None:
            np.random.seed(seed)

        generator = LWEGenerator(n=n, m=trials, q=q, eta=eta)
        inst = generator.generate_instance()

        s = inst['s']
        A = inst['A']
        e = inst['e']

        y = A.dot(s) + e
        k = np.floor(y / q).astype(int)
        return k % m

    @staticmethod
    def estimate_wrap_pmf(k_samples: np.ndarray, m: int) -> np.ndarray:
        """
        Calcula la PMF empírica P(k mod m).
        """
        counts = np.bincount(k_samples % m, minlength=m)
        return counts / np.sum(counts)

    @classmethod
    def analyze_wrap_uniformity(cls, k_samples: np.ndarray, m: int) -> Dict:
        """
        Métricas de uniformidad: Entropía Shannon, KL vs uniforme, Distancia Estadística y Chi^2.
        """
        pmf = cls.estimate_wrap_pmf(k_samples, m)
        unif_pmf = np.full(m, 1.0 / m)

        noise_model = NoiseModel(mod=m)
        entropy = noise_model.shannon_entropy(pmf)
        max_entropy = float(np.log2(m))

        kl_vs_unif = noise_model.kl_divergence(pmf, unif_pmf)
        stat_dist = float(0.5 * np.sum(np.abs(pmf - unif_pmf)))
        chi2_res = noise_model.chi_squared_test(k_samples, unif_pmf)

        # Intervalo de confianza del 95% para la entropía vía bootstrap
        N = len(k_samples)
        num_boot = 50
        boot_entropies = []
        for _ in range(num_boot):
            boot_idx = np.random.randint(0, N, size=N)
            b_pmf = np.bincount(k_samples[boot_idx] % m, minlength=m) / N
            boot_entropies.append(noise_model.shannon_entropy(b_pmf))

        ci_low, ci_high = np.percentile(boot_entropies, [2.5, 97.5])

        return {
            'm': m,
            'pmf': pmf.tolist(),
            'entropy': float(entropy),
            'max_entropy': max_entropy,
            'kl_vs_uniform': float(kl_vs_unif),
            'stat_distance': stat_dist,
            'chi2_p_value': chi2_res['p_value'],
            'ci_95_entropy': (float(ci_low), float(ci_high)),
            'N': N
        }
