import numpy as np
from scipy.stats import chisquare
from typing import Dict, Tuple
from src.lwe_generator import LWEGenerator
from src.projection import AlgebraicProjection
from src.noise_model import NoiseModel

class WrappingAnalysis:
    """
    Módulo de Análisis del Término de Envoltorio Modular (Fase 3):
    k = floor((A * s + e) / q)
    Estudia experimentalmente si k mod 6 se comporta como una variable
    aproximadamente uniforme e independiente bajo los parámetros analizados.
    """

    def __init__(self, mod: int = 6):
        self.mod = mod

    def sample_wrap_variable(self, n: int = 2, m: int = 100, q: int = 3329, 
                             eta: int = 2, num_instances: int = 500, seed: int = None) -> Tuple[np.ndarray, Dict]:
        """
        Extrae el cociente de envoltorio k = floor((A*s + e) / q) mod 6
        y guarda los vectores s6, A6, e6 asociados para análisis de dependencia.
        """
        if seed is not None:
            np.random.seed(seed)

        generator = LWEGenerator(n=n, m=m, q=q, eta=eta)
        projection = AlgebraicProjection(target_modulus=self.mod)

        k_samples = []
        s6_samples = []
        A6_samples = []
        e6_samples = []

        for _ in range(num_instances):
            inst = generator.generate_instance()
            proj = projection.project(inst)

            s = inst['s']
            A = inst['A']
            e = inst['e']

            # y = A*s + e en Z (sin mod q)
            y = A.dot(s) + e
            k = np.floor(y / q).astype(int)
            k_mod6 = k % self.mod

            k_samples.append(k_mod6)
            s6_samples.append(proj['s6'])
            A6_samples.append(proj['A6'])
            e6_samples.append(proj['e6'])

        k_concat = np.concatenate(k_samples)

        return k_concat, {
            's6': np.array(s6_samples),
            'A6': np.array(A6_samples),
            'e6': np.array(e6_samples)
        }

    def analyze_wrap_distribution(self, k_samples: np.ndarray) -> Dict:
        """
        Calcula entropía, KL vs uniforme, distancia estadística y prueba chi^2 para k mod 6.
        """
        counts = np.bincount(k_samples % self.mod, minlength=self.mod)
        pmf = counts / np.sum(counts)
        unif_pmf = np.full(self.mod, 1.0 / self.mod)

        noise_model = NoiseModel(mod=self.mod)
        entropy = noise_model.shannon_entropy(pmf)
        kl_vs_unif = noise_model.kl_divergence(pmf, unif_pmf)
        stat_dist = float(0.5 * np.sum(np.abs(pmf - unif_pmf)))
        chi2_res = noise_model.chi_squared_test(k_samples, unif_pmf)

        return {
            'empirical_pmf': pmf.tolist(),
            'entropy': float(entropy),
            'entropy_uniform': float(np.log2(self.mod)),
            'kl_vs_uniform': float(kl_vs_unif),
            'stat_distance_vs_uniform': stat_dist,
            'chi2_p_value': chi2_res['p_value']
        }

    def analyze_dependencies(self, k_samples: np.ndarray, extra_data: Dict) -> Dict:
        """
        Mide el grado de independencia experimental entre (k mod 6) y (s6, A6, e6).
        Calcula la correlación empírica y la información mutua empírica.
        """
        s6 = extra_data['s6'] # (num_instances, n)
        
        # Aplanar s6 repitiendo para empatar las m muestras por instancia
        num_instances, n = s6.shape
        m = len(k_samples) // num_instances

        s6_flat = np.repeat(s6[:, 0], m) # Tomar primera componente de s6

        # Correlación de Pearson entre k mod 6 y s6_flat
        corr_k_s6 = float(np.corrcoef(k_samples % self.mod, s6_flat % self.mod)[0, 1])

        return {
            'corr_k_s6': corr_k_s6,
            'num_samples': len(k_samples)
        }
