import unittest
import numpy as np
from pathlib import Path

from transformations.dsa.decompose import decompose_fips204
from transformations.dsa.hint import make_hint_fips204, use_hint_fips204, audit_hint_transformation

class TestMLDSAHintPhase3(unittest.TestCase):

    def setUp(self):
        self.q = 8380417
        self.gamma2_44 = 95232
        self.gamma2_65 = 261888

    def test_hint_reconstruction_correctness_mldsa44(self):
        z1 = np.random.randint(0, self.q, size=1000, dtype=np.int64)
        z0 = np.random.randint(-self.gamma2_44, self.gamma2_44 + 1, size=1000, dtype=np.int64)

        h = make_hint_fips204(z0, z1, self.gamma2_44, self.q)
        r1_expected, _ = decompose_fips204(z0 + z1, self.gamma2_44, self.q)
        r1_reconstructed = use_hint_fips204(h, z1, self.gamma2_44, self.q)

        np.testing.assert_array_equal(r1_expected, r1_reconstructed)

    def test_hint_reconstruction_correctness_mldsa65(self):
        z1 = np.random.randint(0, self.q, size=1000, dtype=np.int64)
        z0 = np.random.randint(-self.gamma2_65, self.gamma2_65 + 1, size=1000, dtype=np.int64)

        h = make_hint_fips204(z0, z1, self.gamma2_65, self.q)
        r1_expected, _ = decompose_fips204(z0 + z1, self.gamma2_65, self.q)
        r1_reconstructed = use_hint_fips204(h, z1, self.gamma2_65, self.q)

        np.testing.assert_array_equal(r1_expected, r1_reconstructed)

    def test_hint_scalar_and_multidim_input(self):
        # Escalar
        z0_s = 12345
        z1_s = 67890
        h_s = make_hint_fips204(z0_s, z1_s, self.gamma2_44, self.q)
        self.assertIsInstance(h_s, int)

        r1_exp, _ = decompose_fips204(z0_s + z1_s, self.gamma2_44, self.q)
        r1_rec = use_hint_fips204(h_s, z1_s, self.gamma2_44, self.q)
        self.assertIsInstance(r1_rec, int)
        self.assertEqual(r1_exp, r1_rec)

        # Matriz 2D
        z0_2d = np.random.randint(-self.gamma2_44, self.gamma2_44 + 1, size=(5, 5), dtype=np.int64)
        z1_2d = np.random.randint(0, self.q, size=(5, 5), dtype=np.int64)

        h_2d = make_hint_fips204(z0_2d, z1_2d, self.gamma2_44, self.q)
        self.assertEqual(h_2d.shape, (5, 5))
        r1_exp_2d, _ = decompose_fips204(z0_2d + z1_2d, self.gamma2_44, self.q)
        r1_rec_2d = use_hint_fips204(h_2d, z1_2d, self.gamma2_44, self.q)
        np.testing.assert_array_equal(r1_exp_2d, r1_rec_2d)

    def test_audit_hint_fast_mldsa44(self):
        res = audit_hint_transformation(q=self.q, gamma2=self.gamma2_44, eta=2, num_samples=10000, seed=42, fast=True, export_csv=False)
        self.assertEqual(res['scheme'], "ML-DSA-44")
        self.assertEqual(res['status'], "PASS")
        self.assertIn('entropy_bits', res)
        self.assertLess(res['mutual_info_s1'], 0.05)
        self.assertLess(res['mutual_info_s2'], 0.05)

    def test_audit_hint_fast_mldsa65(self):
        res = audit_hint_transformation(q=self.q, gamma2=self.gamma2_65, eta=4, gamma1=524288, num_samples=10000, seed=42, fast=True, export_csv=False)
        self.assertEqual(res['scheme'], "ML-DSA-65/87")
        self.assertEqual(res['status'], "PASS")
        self.assertIn('entropy_bits', res)
        self.assertLess(res['mutual_info_s1'], 0.05)
        self.assertLess(res['mutual_info_s2'], 0.05)

    def test_csv_export_append(self):
        root_dir = Path(__file__).resolve().parent.parent
        results_dir = root_dir / "results"
        results_dir.mkdir(parents=True, exist_ok=True)
        csv_path = results_dir / "dsa_transform_table.csv"

        if csv_path.exists():
            csv_path.unlink()

        audit_hint_transformation(q=self.q, gamma2=self.gamma2_44, eta=2, num_samples=2000, seed=42, export_csv=True)
        self.assertTrue(csv_path.exists())

        audit_hint_transformation(q=self.q, gamma2=self.gamma2_65, eta=4, gamma1=524288, num_samples=2000, seed=43, export_csv=True)
        with open(csv_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        self.assertGreaterEqual(len(lines), 3) # Header + at least 2 rows

if __name__ == '__main__':
    unittest.main()
