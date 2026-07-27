import numpy as np
from scipy.special import comb
from scipy.stats import chisquare

class NoiseModel:
    """
    Módulo 3: Modelo Estadístico del Ruido Proyectado.
    Calcula PMF teórica de CBD(eta) mod 6, PMF empírica, entropía de Shannon,
    divergencia KL (frente a uniforme y teórica) y prueba de chi^2.
    """

    def __init__(self, mod: int = 6):
        self.mod = mod

    def theoretical_cbd_pmf(self, eta: int = 2) -> np.ndarray:
        """
        Calcula la PMF teórica exacta de CBD(eta) proyectada modulo 6.
        CBD(eta) produce valores k in [-eta, eta] con prob binom(2*eta, eta + k) / 2^(2*eta).
        """
        pmf = np.zeros(self.mod, dtype=float)
        total_outcomes = 2 ** (2 * eta)
        
        for k in range(-eta, eta + 1):
            prob = comb(2 * eta, eta + k) / total_outcomes
            residue = k % self.mod
            pmf[residue] += prob

        return pmf

    def empirical_pmf(self, e_samples: np.ndarray) -> np.ndarray:
        """
        Calcula la PMF empírica a partir de una muestra de valores de ruido mod 6.
        """
        counts = np.bincount(e_samples % self.mod, minlength=self.mod)
        return counts / np.sum(counts)

    @staticmethod
    def shannon_entropy(pmf: np.ndarray, base: float = 2.0) -> float:
        """
        Calcula la entropía de Shannon H(X) en bits (base 2 por defecto).
        """
        nonzero_p = pmf[pmf > 0]
        return float(-np.sum(nonzero_p * np.log2(nonzero_p) / np.log2(base)))

    @staticmethod
    def kl_divergence(p: np.ndarray, q: np.ndarray, eps: float = 1e-12) -> float:
        """
        Calcula la Divergencia de Kullback-Leibler D_KL(P || Q) en bits.
        """
        p_smooth = np.clip(p, eps, 1.0)
        q_smooth = np.clip(q, eps, 1.0)
        p_smooth /= np.sum(p_smooth)
        q_smooth /= np.sum(q_smooth)
        
        return float(np.sum(p_smooth * np.log2(p_smooth / q_smooth)))

    def chi_squared_test(self, e_samples: np.ndarray, expected_pmf: np.ndarray = None):
        """
        Realiza la prueba de bondad de ajuste chi^2 entre los conteos observados
        y una PMF esperada (por defecto la PMF uniforme o teórica).
        
        :return: dict con chi2_stat, p_value
        """
        counts = np.bincount(e_samples % self.mod, minlength=self.mod)
        N = len(e_samples)
        
        if expected_pmf is None:
            expected_counts = np.full(self.mod, N / self.mod)
        else:
            expected_counts = expected_pmf * N
            
        # Evitar ceros en frecuencias esperadas ajustando eps
        expected_counts = np.maximum(expected_counts, 1e-6)
        
        stat, p_val = chisquare(counts, f_exp=expected_counts)
        return {
            'chi2_stat': float(stat),
            'p_value': float(p_val),
            'observed_counts': counts.tolist(),
            'expected_counts': expected_counts.tolist()
        }

    def analyze_noise(self, e_samples: np.ndarray, e_eff_samples: np.ndarray = None, eta: int = 2) -> dict:
        """
        Análisis estadístico completo del ruido proyectado (directo y efectivo).
        """
        emp_pmf = self.empirical_pmf(e_samples)
        theo_pmf = self.theoretical_cbd_pmf(eta)
        unif_pmf = np.full(self.mod, 1.0 / self.mod)

        entropy_emp = self.shannon_entropy(emp_pmf)
        entropy_theo = self.shannon_entropy(theo_pmf)
        entropy_max = float(np.log2(self.mod)) # log2(6) ~ 2.585

        kl_vs_unif = self.kl_divergence(emp_pmf, unif_pmf)
        kl_vs_theo = self.kl_divergence(emp_pmf, theo_pmf)

        chi2_unif = self.chi_squared_test(e_samples, unif_pmf)
        chi2_theo = self.chi_squared_test(e_samples, theo_pmf)

        res = {
            'empirical_pmf': emp_pmf.tolist(),
            'theoretical_pmf': theo_pmf.tolist(),
            'uniform_pmf': unif_pmf.tolist(),
            'entropy_empirical': entropy_emp,
            'entropy_theoretical': entropy_theo,
            'entropy_max': entropy_max,
            'kl_vs_uniform': kl_vs_unif,
            'kl_vs_theoretical': kl_vs_theo,
            'chi2_uniform': chi2_unif,
            'chi2_theoretical': chi2_theo
        }

        if e_eff_samples is not None:
            emp_eff_pmf = self.empirical_pmf(e_eff_samples)
            res['effective_empirical_pmf'] = emp_eff_pmf.tolist()
            res['effective_entropy'] = self.shannon_entropy(emp_eff_pmf)
            res['effective_kl_vs_uniform'] = self.kl_divergence(emp_eff_pmf, unif_pmf)
            res['effective_chi2_uniform'] = self.chi_squared_test(e_eff_samples, unif_pmf)

        return res

