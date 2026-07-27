import itertools
import numpy as np
from typing import Dict

class MLEAttacker:
    """
    Módulo 4 (Fase 2): Atacante Bayesiano / MLE Configurable.
    Permite evaluar el desempeño del atacante utilizando:
    - Ataque Ingenuo: PMF de CBD mod 6 (asume que el ruido mantiene la CBD).
    - Ataque Ideal: PMF del Ruido Efectivo Real P(e_eff) observado en (b_6 - A_6 * s_6) mod 6.
    """

    def __init__(self, noise_pmf: np.ndarray, model_name: str = "MLE", mod: int = 6, eps: float = 1e-12):
        """
        :param noise_pmf: PMF de ruido a utilizar (CBD mod 6 o e_eff estimado)
        :param model_name: Nombre descriptivo del modelo de atacante
        :param mod: Módulo (6)
        :param eps: Epsilon para suavizado logarítmico
        """
        self.mod = mod
        self.model_name = model_name
        self.noise_pmf = noise_pmf
        smoothed_pmf = np.clip(noise_pmf, eps, 1.0)
        self.log_pmf = np.log(smoothed_pmf)

    def compute_score(self, A6: np.ndarray, b6: np.ndarray, s_candidate: np.ndarray) -> float:
        """
        Calcula la log-verosimilitud para un candidato s':
        score(s') = sum_{i=1}^m log P((b_6 - A_6 * s') % 6)
        """
        residual = (b6 - A6.dot(s_candidate)) % self.mod
        return float(np.sum(self.log_pmf[residual]))

    def attack_exact(self, A6: np.ndarray, b6: np.ndarray, real_s6: np.ndarray) -> Dict:
        """
        Ataque por enumeración exhaustiva completa en Z_6^n (para n <= 5).
        """
        m, n = A6.shape
        num_candidates = self.mod ** n

        best_score = -np.inf
        best_s = None

        real_score = self.compute_score(A6, b6, real_s6)
        max_incorrect_score = -np.inf

        # Enumeración completa de candidatos
        for s_tuple in itertools.product(range(self.mod), repeat=n):
            s_cand = np.array(s_tuple, dtype=int)
            score = self.compute_score(A6, b6, s_cand)

            if np.array_equal(s_cand, real_s6):
                pass
            else:
                if score > max_incorrect_score:
                    max_incorrect_score = score

            if score > best_score:
                best_score = score
                best_s = s_cand

        is_success = np.array_equal(best_s, real_s6)

        return {
            'model_name': self.model_name,
            'estimated_s': best_s.tolist(),
            'real_s6': real_s6.tolist(),
            'max_score': best_score,
            'real_score': real_score,
            'max_incorrect_score': max_incorrect_score,
            'is_success': is_success,
            'num_candidates': num_candidates,
            'mode': 'exact'
        }

    def attack_sampled(self, A6: np.ndarray, b6: np.ndarray, real_s6: np.ndarray, num_samples: int = 10000) -> Dict:
        """
        Ataque por muestreo Monte Carlo para dimensiones mayores (n > 5).
        """
        m, n = A6.shape
        real_score = self.compute_score(A6, b6, real_s6)

        max_incorrect_score = -np.inf
        best_score = real_score
        best_s = real_s6.copy()

        for _ in range(num_samples):
            s_cand = np.random.randint(0, self.mod, size=n)
            if np.array_equal(s_cand, real_s6):
                continue

            score = self.compute_score(A6, b6, s_cand)
            if score > max_incorrect_score:
                max_incorrect_score = score

            if score > best_score:
                best_score = score
                best_s = s_cand

        is_success = np.array_equal(best_s, real_s6)

        return {
            'model_name': self.model_name,
            'estimated_s': best_s.tolist(),
            'real_s6': real_s6.tolist(),
            'max_score': best_score,
            'real_score': real_score,
            'max_incorrect_score': max_incorrect_score,
            'is_success': is_success,
            'num_candidates': num_samples + 1,
            'mode': 'sampled'
        }
