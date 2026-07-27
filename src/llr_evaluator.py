import numpy as np
from scipy import stats
from typing import List, Dict

class LLREvaluator:
    """
    Módulo 5: Evaluación LLR (Log-Likelihood Ratio).
    Calcula LLR = score(s_real) - score(s_mejor_incorrecto) y sus estadísticas asociadas
    (media, desviación estándar, intervalo de confianza del 95% y % de LLR positivos).
    """

    @staticmethod
    def calculate_llr(real_score: float, max_incorrect_score: float) -> float:
        """
        Calcula el Log-Likelihood Ratio para una ejecución individual.
        """
        return real_score - max_incorrect_score

    @staticmethod
    def evaluate_batch(attack_results: List[Dict]) -> Dict:
        """
        Calcula métricas agregadas sobre una lista de resultados de ataques.
        """
        llrs = []
        successes = []

        for res in attack_results:
            llr = res['real_score'] - res['max_incorrect_score']
            llrs.append(llr)
            successes.append(1 if res['is_success'] else 0)

        llrs = np.array(llrs, dtype=float)
        successes = np.array(successes, dtype=float)
        N = len(llrs)

        mean_llr = float(np.mean(llrs))
        std_llr = float(np.std(llrs, ddof=1)) if N > 1 else 0.0
        sem_llr = std_llr / np.sqrt(N) if N > 0 else 0.0

        # Intervalo de confianza del 95%
        if N > 1:
            ci_low, ci_high = stats.t.interval(0.95, df=N-1, loc=mean_llr, scale=sem_llr)
        else:
            ci_low, ci_high = mean_llr, mean_llr

        pct_positive_llr = float(np.mean(llrs > 0) * 100.0)
        success_rate = float(np.mean(successes) * 100.0)

        return {
            'N': N,
            'mean_llr': mean_llr,
            'std_llr': std_llr,
            'sem_llr': sem_llr,
            'ci_95': (float(ci_low), float(ci_high)),
            'pct_positive_llr': pct_positive_llr,
            'success_rate': success_rate,
            'llrs': llrs.tolist()
        }
