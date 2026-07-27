import numpy as np
from typing import Dict

class Comparators:
    """
    Módulo 7: Comparadores y Baselines de Referencia.
    Permite separar:
    - Reducción trivial del espacio de búsqueda (q^n -> 6^n).
    - Ventaja estadística real aportada por la proyección.
    """

    @staticmethod
    def baseline1_random_guess(n: int, mod: int = 6) -> Dict:
        """
        Baseline 1: Ataque completamente aleatorio.
        Tasa de éxito teórica: 1 / (6^n)
        """
        success_prob = 1.0 / (mod ** n)
        return {
            'baseline_name': 'Baseline 1: Random Guess',
            'success_rate_theoretical': float(success_prob * 100.0),
            'expected_attempts': int(mod ** n)
        }

    @staticmethod
    def baseline2_prior_entropy(n: int, mod: int = 6) -> Dict:
        """
        Baseline 2: Distribución previa del secreto (Entropía máxima).
        """
        prior_entropy_bits = n * np.log2(mod)
        return {
            'baseline_name': 'Baseline 2: Prior Distribution',
            'prior_entropy_bits': float(prior_entropy_bits),
            'space_size': int(mod ** n)
        }

    @classmethod
    def evaluate_advantage(cls, mle_results: Dict, n: int, mod: int = 6) -> Dict:
        """
        Compara los resultados del atacante MLE frente a las baselines.
        Calcula la ventaja empírica sobre el azar.
        """
        b1 = cls.baseline1_random_guess(n, mod)
        b2 = cls.baseline2_prior_entropy(n, mod)

        mle_success_rate = mle_results['success_rate']
        random_success_rate = b1['success_rate_theoretical']

        advantage = mle_success_rate - random_success_rate

        return {
            'n': n,
            'mod': mod,
            'mle_success_rate': mle_success_rate,
            'random_success_rate': random_success_rate,
            'advantage_over_random_pct': float(advantage),
            'mean_llr': mle_results['mean_llr'],
            'prior_entropy_bits': b2['prior_entropy_bits'],
            'search_space_reduction_ratio': float((6.0 / 3329.0) ** n)  # q=3329 -> 6
        }
