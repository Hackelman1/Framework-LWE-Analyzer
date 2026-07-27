import unittest
import numpy as np
from pathlib import Path

from transformations.dsa.decompose import decompose_fips204, audit_decompose_transformation

class TestMLDSADecomposePhase2(unittest.TestCase):

    def setUp(self):
        self.q = 8380417
        self.gamma2_44 = 95232
        self.gamma2_65 = 261888

    def test_decompose_fips204_correctness_mldsa44(self):
        r_samples = np.random.randint(0, self.q, size=1000, dtype=np.int64)
        r1, r0 = decompose_fips204(r_samples, self.gamma2_44, self.q)

        # 1. Rango de r0 en [-gamma2, gamma2]
        self.assertTrue(np.all(r0 >= -self.gamma2_44))
        self.assertTrue(np.all(r0 <= self.gamma2_44))

        # 2. Reconstrucción modular: r == r1 * 2*gamma2 + r0 (mod q)
        r_reconstructed = (r1 * 2 * self.gamma2_44 + r0) % self.q
        np.testing.assert_array_equal(r_samples % self.q, r_reconstructed)

    def test_decompose_fips204_correctness_mldsa65(self):
        r_samples = np.random.randint(0, self.q, size=1000, dtype=np.int64)
        r1, r0 = decompose_fips204(r_samples, self.gamma2_65, self.q)

        # 1. Rango de r0 en [-gamma2, gamma2]
        self.assertTrue(np.all(r0 >= -self.gamma2_65))
        self.assertTrue(np.all(r0 <= self.gamma2_65))

        # 2. Reconstrucción modular: r == r1 * 2*gamma2 + r0 (mod q)
        r_reconstructed = (r1 * 2 * self.gamma2_65 + r0) % self.q
        np.testing.assert_array_equal(r_samples % self.q, r_reconstructed)

    def test_decompose_scalar_input(self):
        r_scalar = 1234567
        r1, r0 = decompose_fips204(r_scalar, self.gamma2_44, self.q)
        self.assertIsInstance(r1, int)
        self.assertIsInstance(r0, int)
        self.assertEqual((r1 * 2 * self.gamma2_44 + r0) % self.q, r_scalar % self.q)

    def test_audit_decompose_fast_mldsa44(self):
        res = audit_decompose_transformation(q=self.q, gamma2=self.gamma2_44, eta=2, num_samples=10000, seed=42, export_csv=False)
        self.assertEqual(res['scheme'], "ML-DSA-44")
        self.assertIn('entropy_r0', res)
        # Con N=10000 el límite empírico máximo de entropía es log2(10000) ~ 13.28 bits
        self.assertGreater(res['entropy_r0'], 12.0)
        self.assertLess(res['mutual_information'], 0.05)

    def test_audit_decompose_fast_mldsa65(self):
        res = audit_decompose_transformation(q=self.q, gamma2=self.gamma2_65, eta=4, num_samples=10000, seed=42, export_csv=False)
        self.assertEqual(res['scheme'], "ML-DSA-65/87")
        self.assertIn('entropy_r0', res)
        # Con N=10000 el límite empírico máximo de entropía es log2(10000) ~ 13.28 bits
        self.assertGreater(res['entropy_r0'], 12.0)
        self.assertLess(res['mutual_information'], 0.05)


    def test_csv_export_append(self):
        root_dir = Path(__file__).resolve().parent.parent
        results_dir = root_dir / "results"
        results_dir.mkdir(parents=True, exist_ok=True)
        csv_path = results_dir / "dsa_transform_table.csv"

        if csv_path.exists():
            csv_path.unlink()

        audit_decompose_transformation(q=self.q, gamma2=self.gamma2_44, eta=2, num_samples=2000, seed=42, export_csv=True)
        self.assertTrue(csv_path.exists())

        audit_decompose_transformation(q=self.q, gamma2=self.gamma2_65, eta=4, num_samples=2000, seed=43, export_csv=True)
        with open(csv_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        self.assertEqual(len(lines), 3) # 1 header + 2 rows

if __name__ == '__main__':
    unittest.main()
