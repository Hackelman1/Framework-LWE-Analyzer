import unittest
import numpy as np

from transformations.kyber_transformations import (
    compress_q,
    decompress_q,
    modular_reduce,
    coefficient_pack,
    coefficient_unpack,
    simulate_kyber_rounding,
    compute_entropy,
    compute_statistical_distance,
    compute_kl_divergence,
    compute_mutual_information
)
from schemes.module_lwe.parameters import KYBER_512
from schemes.module_lwe.kyber_transform_audit import KyberTransformAuditor
from auditor import SchemeAuditor, analyze_scheme

class TestKyberTransformationsPhase11(unittest.TestCase):

    def setUp(self):
        self.q = 3329
        self.d = 10

    def test_compression_decompression_bounds(self):
        x = 1000
        y = compress_q(x, self.q, self.d)
        self.assertGreaterEqual(y, 0)
        self.assertLess(y, 1 << self.d)

        x_rec = decompress_q(y, self.q, self.d)
        err = abs((x_rec - x + self.q // 2) % self.q - self.q // 2)
        # El error de redondeo para d=10 no debe superar q / 2^(d+1) ~ 1.62
        self.assertLessEqual(err, 3)

    def test_coefficient_pack_unpack_reversibility(self):
        poly = np.random.randint(0, 1 << 12, size=256)
        packed = coefficient_pack(poly, q=self.q, d=12)
        unpacked = coefficient_unpack(packed, q=self.q, d=12, length=256)
        np.testing.assert_array_equal(poly, unpacked)

    def test_modular_reduction_modes(self):
        arr = np.array([3330, -5, 3329])
        exact = modular_reduce(arr, self.q, mode="exact")
        np.testing.assert_array_equal(exact, [1, 3324, 0])

        centered = modular_reduce(arr, self.q, mode="centered")
        np.testing.assert_array_equal(centered, [1, -5, 0])

    def test_kyber_transform_auditor(self):
        auditor = KyberTransformAuditor(params=KYBER_512, seed=42)
        res_comp = auditor.audit_compression_bias(d=10, trials=30)
        self.assertIn('entropy_after', res_comp)
        self.assertIsInstance(res_comp['kl_divergence'], float)
        self.assertGreaterEqual(res_comp['kl_divergence'], 0.0)

        res_round = auditor.audit_rounding_bias(d=10, trials=10)
        self.assertIn('mean_error', res_round)

        res_mod = auditor.audit_modular_reduction(trials=10, reduction_type="exact")
        self.assertIn('chi2_stat', res_mod)

        res_pack = auditor.audit_pack_unpack_leakage(d=12, trials=10)
        self.assertIn('byte_entropy', res_pack)

    def test_scheme_auditor_interface(self):
        report = analyze_scheme(scheme="Kyber512", transformation="compression", parameters={"d": 10})
        self.assertIn("Transformation: Real Kyber Operation (compression)", report)

if __name__ == '__main__':
    unittest.main()
