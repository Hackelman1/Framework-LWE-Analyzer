import numpy as np
from scipy.stats import chisquare
from typing import Dict
from src.lwe_generator import LWEGenerator
from src.projection import AlgebraicProjection
from src.noise_model import NoiseModel

class EffectiveNoiseModel:
    """
    Módulo 1 de la Fase 2: Modelo de Ruido Efectivo.
    Genera, estima y compara la distribución del ruido efectivo observable:
    e_eff = (b_6 - A_6 * s_6) mod 6
    frente a la CBD teórica directa mod 6.
    """

    def __init__(self, mod: int = 6):
        self.mod = mod

    def generate_effective_noise_samples(self, n: int = 2, m: int = 100, q: int = 3329, 
                                        eta: int = 2, num_instances: int = 1000, seed: int = None) -> np.ndarray:
        """
        Genera múltiples instancias LWE y acumula el ruido efectivo observable real e_eff.
        """
        if seed is not None:
            np.random.seed(seed)

        generator = LWEGenerator(n=n, m=m, q=q, eta=eta)
        projection = AlgebraicProjection(target_modulus=self.mod)

        all_eff_samples = []

        for _ in range(num_instances):
            inst = generator.generate_instance()
            proj = projection.project(inst)
            all_eff_samples.append(proj['e_effective6'])

        return np.concatenate(all_eff_samples)

    def estimate_effective_noise_pmf(self, e_eff_samples: np.ndarray) -> np.ndarray:
        """
        Calcula la PMF empírica P(e_eff = 0, ..., 5) de las muestras acumuladas.
        """
        counts = np.bincount(e_eff_samples % self.mod, minlength=self.mod)
        return counts / np.sum(counts)

    @staticmethod
    def statistical_distance(p: np.ndarray, q: np.ndarray) -> float:
        """
        Calcula la distancia estadística (TVD - Total Variation Distance):
        d_stat(P, Q) = 1/2 * sum_{i} |P(i) - Q(i)|
        """
        return float(0.5 * np.sum(np.abs(p - q)))

    def compare_noise_models(self, eta: int = 2, num_instances: int = 1000, n: int = 2, m: int = 100, q: int = 3329) -> Dict:
        """
        Compara el modelo de ruido CBD directo mod 6 vs el modelo de ruido efectivo proyectado.
        Metrics: Entropía Shannon, KL div, Distancia Estadística y Chi-cuadrado.
        """
        e_eff_samples = self.generate_effective_noise_samples(n=n, m=m, q=q, eta=eta, num_instances=num_instances, seed=42)
        eff_pmf = self.estimate_effective_noise_pmf(e_eff_samples)

        noise_model = NoiseModel(mod=self.mod)
        cbd_pmf = noise_model.theoretical_cbd_pmf(eta=eta)
        unif_pmf = np.full(self.mod, 1.0 / self.mod)

        # Entropías
        h_cbd = noise_model.shannon_entropy(cbd_pmf)
        h_eff = noise_model.shannon_entropy(eff_pmf)
        h_unif = float(np.log2(self.mod))

        # Divergencias KL
        kl_cbd_vs_unif = noise_model.kl_divergence(cbd_pmf, unif_pmf)
        kl_eff_vs_unif = noise_model.kl_divergence(eff_pmf, unif_pmf)
        kl_eff_vs_cbd = noise_model.kl_divergence(eff_pmf, cbd_pmf)

        # Distancias estadísticas
        stat_dist_eff_vs_unif = self.statistical_distance(eff_pmf, unif_pmf)
        stat_dist_eff_vs_cbd = self.statistical_distance(eff_pmf, cbd_pmf)
        stat_dist_cbd_vs_unif = self.statistical_distance(cbd_pmf, unif_pmf)

        # Pruebas Chi-cuadrado
        chi2_eff_unif = noise_model.chi_squared_test(e_eff_samples, unif_pmf)
        chi2_eff_cbd = noise_model.chi_squared_test(e_eff_samples, cbd_pmf)

        return {
            'cbd_pmf': cbd_pmf.tolist(),
            'effective_pmf': eff_pmf.tolist(),
            'uniform_pmf': unif_pmf.tolist(),
            'entropy_cbd': h_cbd,
            'entropy_effective': h_eff,
            'entropy_uniform': h_unif,
            'kl_cbd_vs_uniform': kl_cbd_vs_unif,
            'kl_effective_vs_uniform': kl_eff_vs_unif,
            'kl_effective_vs_cbd': kl_eff_vs_cbd,
            'stat_dist_effective_vs_uniform': stat_dist_eff_vs_unif,
            'stat_dist_effective_vs_cbd': stat_dist_eff_vs_cbd,
            'stat_dist_cbd_vs_uniform': stat_dist_cbd_vs_unif,
            'chi2_effective_vs_uniform': chi2_eff_unif,
            'chi2_effective_vs_cbd': chi2_eff_cbd
        }
