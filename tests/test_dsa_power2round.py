import unittest
import numpy as np
from pathlib import Path

from transformations.dsa.power2round import power2round_fips204, audit_power2round_transformation

class TestMLDSAPower2RoundPhase2(unittest.TestCase):

    def setUp(self):
        self.q = 8380417
        self.d = 13

    def test_power2round_correctness_mldsa44(self):
        t_samples = np.random.randint(0, self.q, size=1000, dtype=np.int64)
        t1, t0 = power2round_fips204(t_samples, d=self.d, q=self.q)

        # 1. Rango de t0 en [-2^(d-1) + 1, 2^(d-1)] = [-4095, 4096]
        min_t0 = -(2**(self.d - 1) - 1) # -4095
        max_t0 = 2**(self.d - 1)        # 4096
        self.assertTrue(np.all(t0 >= min_t0))
        self.assertTrue(np.all(t0 <= max_t0))

        # 2. Reconstrucción modular: t == t1 * 2^d + t0 (mod q)
        t_reconstructed = (t1 * (2**self.d) + t0) % self.q
        np.testing.assert_array_equal(t_samples % self.q, t_reconstructed)

    def test_power2round_scalar_and_multidim_input(self):
        # Escalar
        t_scalar = 1234567
        t1, t0 = power2round_fips204(t_scalar, d=self.d, q=self.q)
        self.assertIsInstance(t1, int)
        self.assertIsInstance(t0, int)
        self.assertEqual((t1 * (2**self.d) + t0) % self.q, t_scalar % self.q)

        # Matriz 2D
        t_2d = np.random.randint(0, self.q, size=(5, 5), dtype=np.int64)
        t1_2d, t0_2d = power2round_fips204(t_2d, d=self.d, q=self.q)
        self.assertEqual(t1_2d.shape, (5, 5))
        self.assertEqual(t0_2d.shape, (5, 5))
        t_rec_2d = (t1_2d * (2**self.d) + t0_2d) % self.q
        np.testing.assert_array_equal(t_2d % self.q, t_rec_2d)

    def test_audit_power2round_fast_mldsa44(self):
        res = audit_power2round_transformation(q=self.q, d=self.d, eta=2, num_samples=10000, seed=42, fast=True, export_csv=False)
        self.assertEqual(res['scheme'], "ML-DSA-44")
        self.assertEqual(res['status'], "PASS")
        self.assertGreater(res['entropy_bits'], 12.0)
        self.assertLess(res['mutual_info_s1'], 1e-3)
        self.assertLess(res['mutual_info_s2'], 1e-3)
        self.assertGreater(res['chi2_pvalue'], 0.01)

    def test_audit_power2round_fast_mldsa65(self):
        res = audit_power2round_transformation(q=self.q, d=self.d, eta=4, num_samples=10000, seed=42, fast=True, export_csv=False)
        self.assertEqual(res['scheme'], "ML-DSA-65/87")
        self.assertEqual(res['status'], "PASS")
        self.assertGreater(res['entropy_bits'], 12.0)
        self.assertLess(res['mutual_info_s1'], 1e-3)
        self.assertLess(res['mutual_info_s2'], 1e-3)
        self.assertGreater(res['chi2_pvalue'], 0.01)

    def test_csv_export_append(self):
        root_dir = Path(__file__).resolve().parent.parent
        results_dir = root_dir / "results"
        results_dir.mkdir(parents=True, exist_ok=True)
        csv_path = results_dir / "dsa_transform_table.csv"

        if csv_path.exists():
            csv_path.unlink()

        audit_power2round_transformation(q=self.q, d=self.d, eta=2, num_samples=2000, seed=42, export_csv=True)
        self.assertTrue(csv_path.exists())

        audit_power2round_transformation(q=self.q, d=self.d, eta=4, num_samples=2000, seed=43, export_csv=True)
        with open(csv_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        self.assertGreaterEqual(len(lines), 3) # Header + at least 2 rows

if __name__ == '__main__':
    unittest.main()
