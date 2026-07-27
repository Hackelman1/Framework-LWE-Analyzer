import unittest
import numpy as np

from src.lwe_generator import LWEGenerator
from src.general_projection import GeneralProjection
from src.subgroup_analysis import SubgroupAnalysis
from src.wrap_distribution import WrapDistribution
from src.convolution_theorem import ConvolutionTheorem
from src.dependency_analysis import DependencyAnalysis
from src.theoretical_independence import TheoreticalIndependence

class TestLWEProjectionFrameworkPhase8(unittest.TestCase):

    def setUp(self):
        self.n = 2
        self.m = 6
        self.q = 3329
        self.eta = 2

    def test_convolution_contraction_bound(self):
        e_pmf = np.array([0.4, 0.3, 0.3])
        wrap_pmf = np.array([0.33, 0.33, 0.34])
        unif = np.full(3, 1.0 / 3)

        eff_pmf = ConvolutionTheorem.circular_convolution(e_pmf, wrap_pmf, m=3)

        d_wrap = 0.5 * np.sum(np.abs(wrap_pmf - unif))
        d_eff = 0.5 * np.sum(np.abs(eff_pmf - unif))

        # Cota de Contracción de Distancia Estadística
        self.assertLessEqual(d_eff, d_wrap + 1e-9)

if __name__ == '__main__':
    unittest.main()
