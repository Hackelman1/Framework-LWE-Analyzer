import unittest
import numpy as np
from transformations.dsa.audit_utils import (
    apply_fdr_control, 
    aggregate_sweep_p_value, 
    compute_mutual_information_robust
)

class TestDSAAuditUtils(unittest.TestCase):

    def test_aggregate_sweep_p_value_bonferroni(self):
        """Verifica que K * p_min se acote a 1.0 (Bonferroni interno)."""
        p_values = [0.10, 0.02, 0.15, 0.05] # K = 4, p_min = 0.02
        res = aggregate_sweep_p_value(p_values)
        self.assertAlmostEqual(res, 0.08, places=4) # 4 * 0.02 = 0.08

        # Caso donde K * p_min > 1.0
        p_values_high = [0.40, 0.30, 0.50] # K = 3, 3 * 0.30 = 0.90 -> acotado
        self.assertLessEqual(aggregate_sweep_p_value(p_values_high), 1.0)

    def test_fdr_control_empty_list(self):
        """Verifica que una lista vacía retorne [] sin errores."""
        self.assertEqual(apply_fdr_control([]), [])

    def test_fdr_control_single_element(self):
        """Verifica que N=1 retorne q_value == p_value."""
        sample_input = [{"empirical_p_value": 0.429, "experiment_id": "Exp_Single"}]
        results = apply_fdr_control(sample_input, alpha=0.05)
        self.assertEqual(len(results), 1)
        self.assertAlmostEqual(results[0]["fdr_q_value"], 0.429, places=3)
        self.assertEqual(results[0]["status"], "PASS")

    def test_fdr_control_multiple_elements(self):
        """Verifica la asignación de PASS/WARNING bajo BH-FDR."""
        sample_inputs = [
            {"empirical_p_value": 0.429, "experiment_id": "Exp_1"},
            {"empirical_p_value": 0.463, "experiment_id": "Exp_2"},
            {"empirical_p_value": 0.001, "experiment_id": "Exp_3"} # Fuga simulada
        ]
        results = apply_fdr_control(sample_inputs, alpha=0.05)
        self.assertEqual(len(results), 3)
        self.assertEqual(results[2]["status"], "WARNING") # q <= 0.05
        self.assertEqual(results[0]["status"], "PASS")

    def test_robust_mi_add_one_smoothing(self):
        """Verifica que el p-valor empírico nunca sea 0.0 exacto."""
        s_vec = np.random.randint(-2, 3, size=1000)
        out_vec = np.random.randint(0, 256, size=1000)
        stats = compute_mutual_information_robust(
            s_vec, out_vec, num_bins=256, n_permutations=100, seed=42
        )
        # Con P=100, el mínimo p-valor alcanzable es 1/101 ≈ 0.0099
        self.assertGreater(stats["empirical_p_value"], 0.0)

if __name__ == "__main__":
    unittest.main()
