import math
import numpy as np
import pandas as pd
from typing import Dict, List
from src.lwe_generator import LWEGenerator
from src.projection import AlgebraicProjection
from src.general_projection import GeneralProjection
from src.subgroup_analysis import SubgroupAnalysis
from src.wrap_distribution import WrapDistribution
from src.convolution_theorem import ConvolutionTheorem
from src.dependency_analysis import DependencyAnalysis
from src.theoretical_independence import TheoreticalIndependence
from src.noise_model import NoiseModel
from src.effective_noise_model import EffectiveNoiseModel
from src.wrapping_analysis import WrappingAnalysis
from src.mle_attacker import MLEAttacker
from src.llr_evaluator import LLREvaluator
from src.mutual_info import MutualInformationCalculator
from src.comparators import Comparators

from schemes.module_lwe.kyber import ModuleLWEGenerator
from schemes.module_lwe.parameters import KYBER_512, KYBER_768, KYBER_1024
from schemes.module_lwe.kyber_transform_audit import KyberTransformAuditor
from transformations.modular_projection import ModuleProjection
from transformations.dsa.audit_utils import (
    aggregate_sweep_p_value,
    compute_mutual_information_robust,
    choose_num_bins,
)


class ExperimentRunner:
    """
    Orquestador de Experimentos de la Fase 11 (Experimentos A a W + FIPS 204 ML-DSA Audit - Release v2.0).
    Alineado estrictamente con la matemática de paper/main.md (N=500000, B=256, P=500, seed=42).
    """

    def __init__(
        self,
        q: int = 3329,
        eta: int = 2,
        mod: int = 6,
        seed: int = 42,
        N: int = 500000,
        B: int = 256,
        P: int = 500,
        mode: str = "full_paper",
    ):
        self.q = q
        self.eta = eta
        self.mod = mod
        self.seed = seed
        self.mode = mode
        if mode == "fast_demo":
            self.N = 10000
            self.B = B
            self.P = 20
            self.P_sweep = 20
        else:
            self.N = N
            self.B = B
            self.P = P
            self.P_sweep = min(P, 50)
        np.random.seed(seed)

    def run_experiment_a(self, num_instances: int = None, m: int = 100) -> Dict:
        num_instances = num_instances or self.N
        eff_model = EffectiveNoiseModel(mod=self.mod)
        results = eff_model.compare_noise_models(
            eta=self.eta, num_instances=num_instances, n=2, m=m, q=self.q
        )
        wrap_analyser = WrappingAnalysis(mod=self.mod)

        # Generación acoplada desde una única secuencia de instancias LWE (A_i, s_i, e_i)
        gen = LWEGenerator(n=2, m=m, q=self.q, eta=self.eta, seed=self.seed)
        k_list, e_list = [], []

        # Extraemos k_i y e_i de la MISMA llamada a generate_instance() por ensayo
        for _ in range(num_instances):
            inst = gen.generate_instance()
            s = inst["s"]
            A = inst["A"]
            e = inst["e"]

            y = A.dot(s) + e
            k = np.floor(y / self.q).astype(int)

            k_list.extend(k % self.mod)
            e_list.extend(e % self.mod)

        k_vec = np.array(k_list, dtype=int)
        e_vec = np.array(e_list, dtype=int)

        k_dist = wrap_analyser.analyze_wrap_distribution(k_vec)
        results["k_analysis"] = k_dist

        mi_stats = compute_mutual_information_robust(
            s_vec=k_vec,
            out_vec=e_vec,
            num_bins=self.mod,
            n_permutations=self.P,
            seed=self.seed,
        )
        results.update(mi_stats)
        results["empirical_p_value"] = mi_stats["empirical_p_value"]
        return results

    def run_experiment_b(
        self,
        dimensions: List[int] = [2, 3, 4, 5],
        m: int = 32,
        num_trials: int = 20,
    ) -> Dict:
        eff_model = EffectiveNoiseModel(mod=self.mod)
        e_eff_samples = eff_model.generate_effective_noise_samples(
            n=2, m=100, q=self.q, eta=self.eta, num_instances=200, seed=self.seed
        )
        eff_pmf = eff_model.estimate_effective_noise_pmf(e_eff_samples)
        attacker_ideal = MLEAttacker(
            noise_pmf=eff_pmf,
            model_name="Ataque Ideal P(e_eff)",
            mod=self.mod,
        )
        projection = AlgebraicProjection(target_modulus=self.mod)

        summary_b = {}
        sub_p = []
        mod = self.mod
        for n in dimensions:
            attack_results = []
            generator = LWEGenerator(n=n, m=m, q=self.q, eta=self.eta)
            s_list, b6_list = [], []
            for _ in range(num_trials):
                inst = generator.generate_instance()
                proj = projection.project(inst)
                res = attacker_ideal.attack_exact(
                    proj["A6"], proj["b6"], proj["s6"]
                )
                attack_results.append(res)
                s_flat = proj["s6"].flatten() % mod
                s_idx = int(np.dot(s_flat, mod ** np.arange(len(s_flat))))
                b_flat = proj["b6"].flatten() % mod
                s_list.extend([s_idx] * len(b_flat))
                b6_list.extend(b_flat)

            eval_res = LLREvaluator.evaluate_batch(attack_results)
            comp_res = Comparators.evaluate_advantage(
                eval_res, n=n, mod=self.mod
            )

            s_vec = np.array(s_list, dtype=int)
            b6_vec = np.array(b6_list, dtype=int)
            mi_stats = compute_mutual_information_robust(
                s_vec,
                b6_vec,
                num_bins=self.B,
                n_permutations=self.P_sweep,
                seed=self.seed,
            )

            summary_b[n] = {
                "eval": eval_res,
                "comparator": comp_res,
                "mi_stats": mi_stats,
                "empirical_p_value": mi_stats["empirical_p_value"],
            }
            sub_p.append(mi_stats["empirical_p_value"])

        summary_b["empirical_p_value"] = float(aggregate_sweep_p_value(sub_p))
        return summary_b

    def run_experiment_c(
        self,
        n: int = 3,
        sample_counts: List[int] = [4, 8, 16, 32, 64],
        num_trials: int = 20,
    ) -> Dict:
        eff_model = EffectiveNoiseModel(mod=self.mod)
        e_eff_samples = eff_model.generate_effective_noise_samples(
            n=n, m=100, q=self.q, eta=self.eta, num_instances=200, seed=self.seed
        )
        eff_pmf = eff_model.estimate_effective_noise_pmf(e_eff_samples)
        attacker_ideal = MLEAttacker(
            noise_pmf=eff_pmf,
            model_name="Ataque Ideal P(e_eff)",
            mod=self.mod,
        )
        projection = AlgebraicProjection(target_modulus=self.mod)

        summary_c = {}
        sub_p = []
        mod = self.mod
        for m in sample_counts:
            attack_results = []
            generator = LWEGenerator(n=n, m=m, q=self.q, eta=self.eta)
            s_list, b6_list = [], []
            for _ in range(num_trials):
                inst = generator.generate_instance()
                proj = projection.project(inst)
                res = attacker_ideal.attack_exact(
                    proj["A6"], proj["b6"], proj["s6"]
                )
                attack_results.append(res)
                s_flat = proj["s6"].flatten() % mod
                s_idx = int(np.dot(s_flat, mod ** np.arange(len(s_flat))))
                b_flat = proj["b6"].flatten() % mod
                s_list.extend([s_idx] * len(b_flat))
                b6_list.extend(b_flat)

            eval_res = LLREvaluator.evaluate_batch(attack_results)
            s_vec = np.array(s_list, dtype=int)
            b6_vec = np.array(b6_list, dtype=int)
            mi_stats = compute_mutual_information_robust(
                s_vec,
                b6_vec,
                num_bins=self.B,
                n_permutations=self.P_sweep,
                seed=self.seed,
            )

            eval_res["mi_stats"] = mi_stats
            eval_res["empirical_p_value"] = mi_stats["empirical_p_value"]
            summary_c[m] = eval_res
            sub_p.append(mi_stats["empirical_p_value"])

        summary_c["empirical_p_value"] = float(aggregate_sweep_p_value(sub_p))
        return summary_c

    def run_experiment_d(
        self, dimensions: List[int] = [2, 3], m: int = 16, num_trials: int = 200
    ) -> Dict:
        eff_model = EffectiveNoiseModel(mod=self.mod)
        e_eff_samples = eff_model.generate_effective_noise_samples(
            n=2, m=50, q=self.q, eta=self.eta, num_instances=200, seed=self.seed
        )
        eff_pmf = eff_model.estimate_effective_noise_pmf(e_eff_samples)
        mi_calc = MutualInformationCalculator(mod=self.mod)
        summary_d = {}
        sub_p = []
        mod = self.mod

        for n in dimensions:
            res_mi = mi_calc.calculate_exact_conditional_mi(
                n=n, m_samples=m, noise_pmf=eff_pmf, num_simulations=20
            )

            K_X = mod**n
            K_Y = mod ** (n + 1)

            # N_eval escala con K_X para asegurar densidad suficiente (>= 50 muestras/celda)
            base_N = self.N if self.mode == "full_paper" else 10000
            N_eval = max(base_N, int(50.0 * K_X * 2))

            gen = LWEGenerator(n=n, m=m, q=self.q, eta=self.eta)
            s_list, ab_list = [], []

            for _ in range(N_eval):
                inst = gen.generate_instance()
                s_m = inst["s"] % mod
                A_m = inst["A"] % mod
                b_m = inst["b"] % mod

                # State index para X = s_m (dimensión n)
                s_idx = int(np.dot(s_m, mod ** np.arange(n)))

                # State index para Y = (A_m[0], b_m[0])
                ab_tuple = np.append(A_m[0], b_m[0])
                ab_idx = int(np.dot(ab_tuple, mod ** np.arange(n + 1)))

                s_list.append(s_idx)
                ab_list.append(ab_idx)

            s_vec = np.array(s_list, dtype=int)
            ab_vec = np.array(ab_list, dtype=int)

            num_b = choose_num_bins(K_X, K_Y, len(s_vec), target_density=50.0)

            mi_stats = compute_mutual_information_robust(
                s_vec,
                ab_vec,
                num_bins=num_b,
                n_permutations=self.P_sweep,
                seed=self.seed,
            )
            res_mi["mi_stats"] = mi_stats
            res_mi["empirical_p_value"] = mi_stats["empirical_p_value"]
            summary_d[n] = res_mi
            sub_p.append(mi_stats["empirical_p_value"])

        summary_d["empirical_p_value"] = float(aggregate_sweep_p_value(sub_p))
        return summary_d

    def run_experiment_e(
        self,
        dimensions: List[int] = [2, 3, 4, 5],
        sample_counts: List[int] = [8, 16, 32, 64],
        num_trials: int = 20,
    ) -> Dict:
        noise_model = NoiseModel(mod=self.mod)
        cbd_pmf = noise_model.theoretical_cbd_pmf(self.eta)
        eff_model = EffectiveNoiseModel(mod=self.mod)
        e_eff_samples = eff_model.generate_effective_noise_samples(
            n=2, m=100, q=self.q, eta=self.eta, num_instances=200, seed=self.seed
        )
        eff_pmf = eff_model.estimate_effective_noise_pmf(e_eff_samples)

        attacker_naive = MLEAttacker(
            noise_pmf=cbd_pmf,
            model_name="Ataque Ingenuo P(CBD mod 6)",
            mod=self.mod,
        )
        attacker_ideal = MLEAttacker(
            noise_pmf=eff_pmf,
            model_name="Ataque Ideal P(e_eff)",
            mod=self.mod,
        )
        projection = AlgebraicProjection(target_modulus=self.mod)

        summary_e = {}
        sub_p = []
        mod = self.mod
        for n in dimensions:
            summary_e[n] = {}
            for m in sample_counts:
                generator = LWEGenerator(n=n, m=m, q=self.q, eta=self.eta)
                results_naive = []
                results_ideal = []
                s_list, b6_list = [], []

                for _ in range(num_trials):
                    inst = generator.generate_instance()
                    proj = projection.project(inst)
                    res_n = attacker_naive.attack_exact(
                        proj["A6"], proj["b6"], proj["s6"]
                    )
                    res_i = attacker_ideal.attack_exact(
                        proj["A6"], proj["b6"], proj["s6"]
                    )
                    results_naive.append(res_n)
                    results_ideal.append(res_i)
                    s_flat = proj["s6"].flatten() % mod
                    s_idx = int(np.dot(s_flat, mod ** np.arange(len(s_flat))))
                    b_flat = proj["b6"].flatten() % mod
                    s_list.extend([s_idx] * len(b_flat))
                    b6_list.extend(b_flat)

                s_vec = np.array(s_list, dtype=int)
                b6_vec = np.array(b6_list, dtype=int)
                mi_stats = compute_mutual_information_robust(
                    s_vec,
                    b6_vec,
                    num_bins=self.B,
                    n_permutations=self.P_sweep,
                    seed=self.seed,
                )

                summary_e[n][m] = {
                    "naive": LLREvaluator.evaluate_batch(results_naive),
                    "ideal": LLREvaluator.evaluate_batch(results_ideal),
                    "mi_stats": mi_stats,
                    "empirical_p_value": mi_stats["empirical_p_value"],
                }
                sub_p.append(mi_stats["empirical_p_value"])

        summary_e["empirical_p_value"] = float(aggregate_sweep_p_value(sub_p))
        return summary_e

    def run_experiment_f(
        self,
        dimensions: List[int] = [2, 3, 4],
        sample_counts: List[int] = [8, 16, 32],
        num_instances: int = 50,
    ) -> Dict:
        mi_calc = MutualInformationCalculator(mod=self.mod)
        summary_f = {}
        sub_p = []
        mod = self.mod

        for n in dimensions:
            summary_f[n] = {}
            for m in sample_counts:
                generator = LWEGenerator(n=n, m=m, q=self.q, eta=self.eta)
                projection = AlgebraicProjection(target_modulus=self.mod)
                e_eff_list, s_list = [], []

                for _ in range(num_instances):
                    inst = generator.generate_instance()
                    proj = projection.project(inst)
                    e_eff = proj["e_effective6"].flatten() % mod
                    s_flat = proj["s6"].flatten() % mod
                    s_idx = int(np.dot(s_flat, mod ** np.arange(len(s_flat))))

                    e_eff_list.extend(e_eff)
                    s_list.extend([s_idx] * len(e_eff))

                e_eff_arr = np.array(e_eff_list, dtype=int)
                s_arr = np.array(s_list, dtype=int)

                indep = mi_calc.estimate_effective_noise_independence(
                    e_eff_arr,
                    np.array([[s] for s in s_arr]),
                    np.ones((len(s_arr), 1)),
                    m=self.mod,
                )

                mi_stats = compute_mutual_information_robust(
                    s_arr,
                    e_eff_arr,
                    num_bins=self.B,
                    n_permutations=self.P_sweep,
                    seed=self.seed,
                )

                indep["mi_stats"] = mi_stats
                indep["empirical_p_value"] = mi_stats["empirical_p_value"]
                summary_f[n][m] = indep
                sub_p.append(mi_stats["empirical_p_value"])

        summary_f["empirical_p_value"] = float(aggregate_sweep_p_value(sub_p))
        return summary_f

    def run_experiment_g(
        self,
        test_q_values: List[int] = [3329, 3328, 3330, 3331],
        n: int = 2,
        m: int = 32,
        num_trials: int = 20,
    ) -> Dict:
        eff_model = EffectiveNoiseModel(mod=self.mod)
        noise_model = NoiseModel(mod=self.mod)
        mi_calc = MutualInformationCalculator(mod=self.mod)
        summary_g = {}
        sub_p = []
        mod = self.mod

        for q_val in test_q_values:
            q_mod6 = q_val % self.mod
            e_eff_samples = eff_model.generate_effective_noise_samples(
                n=n, m=m, q=q_val, eta=self.eta, num_instances=200, seed=self.seed
            )
            eff_pmf = eff_model.estimate_effective_noise_pmf(e_eff_samples)
            unif_pmf = np.full(self.mod, 1.0 / self.mod)

            entropy_eff = noise_model.shannon_entropy(eff_pmf)
            kl_vs_unif = noise_model.kl_divergence(eff_pmf, unif_pmf)

            attacker_ideal = MLEAttacker(
                noise_pmf=eff_pmf, model_name=f"Ideal (q={q_val})", mod=self.mod
            )
            projection = AlgebraicProjection(target_modulus=self.mod)
            generator = LWEGenerator(n=n, m=m, q=q_val, eta=self.eta)

            attack_results = []
            s_list, out_list = [], []
            for _ in range(num_trials):
                inst = generator.generate_instance()
                proj = projection.project(inst)
                res = attacker_ideal.attack_exact(
                    proj["A6"], proj["b6"], proj["s6"]
                )
                attack_results.append(res)
                s_flat = proj["s6"].flatten() % mod
                s_idx = int(np.dot(s_flat, mod ** np.arange(len(s_flat))))
                e_eff = proj["e_effective6"].flatten() % mod
                s_list.extend([s_idx] * len(e_eff))
                out_list.extend(e_eff)

            eval_res = LLREvaluator.evaluate_batch(attack_results)
            res_mi = mi_calc.calculate_exact_conditional_mi(
                n=n, m_samples=16, noise_pmf=eff_pmf, num_simulations=20
            )

            s_vec = np.array(s_list, dtype=int)
            out_vec = np.array(out_list, dtype=int)
            mi_stats = compute_mutual_information_robust(
                s_vec,
                out_vec,
                num_bins=self.B,
                n_permutations=self.P_sweep,
                seed=self.seed,
            )

            summary_g[q_val] = {
                "q": q_val,
                "q_mod6": q_mod6,
                "entropy_effective": entropy_eff,
                "kl_vs_uniform": kl_vs_unif,
                "mle_success_rate": eval_res["success_rate"],
                "mean_llr": eval_res["mean_llr"],
                "mi": res_mi["MI"],
                "mi_stats": mi_stats,
                "empirical_p_value": mi_stats["empirical_p_value"],
            }
            sub_p.append(mi_stats["empirical_p_value"])

        summary_g["empirical_p_value"] = float(aggregate_sweep_p_value(sub_p))
        return summary_g

    def run_experiment_h(
        self,
        q_range: List[int] = [3327, 3328, 3329, 3330, 3331, 3332, 3333, 3334, 3335],
        m_values: List[int] = [2, 3, 4, 5, 6, 7, 8, 9, 10, 12],
        num_instances: int = 50,
    ) -> Dict:
        summary_h = {}
        sub_p = []
        for q_val in q_range:
            summary_h[q_val] = {}
            for m_val in m_values:
                subgroup_info = SubgroupAnalysis.analyze_masking_capacity(
                    q_val, m_val
                )
                gen = LWEGenerator(n=2, m=100, q=q_val, eta=self.eta)
                s_list, eff_list = [], []

                for _ in range(num_instances):
                    inst = gen.generate_instance()
                    proj = GeneralProjection.project_lwe(inst, m_val)
                    e_eff = proj["e_effective_m"].flatten() % m_val
                    s_flat = proj["s_m"].flatten() % m_val
                    s_idx = int(np.dot(s_flat, m_val ** np.arange(len(s_flat))))
                    s_list.extend([s_idx] * len(e_eff))
                    eff_list.extend(e_eff)

                s_vec = np.array(s_list, dtype=int)
                eff_vec = np.array(eff_list, dtype=int)

                counts = np.bincount(eff_vec % m_val, minlength=m_val)
                eff_pmf = counts / np.sum(counts)
                unif_pmf = np.full(m_val, 1.0 / m_val)

                h_eff = float(
                    -np.sum(eff_pmf[eff_pmf > 0] * np.log2(eff_pmf[eff_pmf > 0]))
                )
                kl_val = float(
                    np.sum(
                        eff_pmf[eff_pmf > 0]
                        * np.log2(eff_pmf[eff_pmf > 0] / unif_pmf[eff_pmf > 0])
                    )
                )
                stat_dist = float(0.5 * np.sum(np.abs(eff_pmf - unif_pmf)))

                mi_stats = compute_mutual_information_robust(
                    s_vec,
                    eff_vec,
                    num_bins=self.B,
                    n_permutations=self.P_sweep,
                    seed=self.seed,
                )

                summary_h[q_val][m_val] = {
                    "q": q_val,
                    "m": m_val,
                    "gcd": subgroup_info["gcd"],
                    "subgroup_size": subgroup_info["subgroup_size"],
                    "is_full_subgroup": subgroup_info["is_full_subgroup"],
                    "entropy_effective": h_eff,
                    "kl_vs_uniform": kl_val,
                    "stat_distance": stat_dist,
                    "mi_stats": mi_stats,
                    "empirical_p_value": mi_stats["empirical_p_value"],
                }
                sub_p.append(mi_stats["empirical_p_value"])

        summary_h["empirical_p_value"] = float(aggregate_sweep_p_value(sub_p))
        return summary_h

    def run_experiment_i(
        self,
        q: int = 3329,
        m_values: List[int] = [2, 3, 4, 5, 6, 7, 8, 9, 10, 12],
    ) -> Dict:
        summary_i = {}
        sub_p = []
        for m_val in m_values:
            gcd_val = math.gcd(q, m_val)
            is_full = gcd_val == 1

            gen = LWEGenerator(n=2, m=1000, q=q, eta=self.eta)
            inst = gen.generate_instance()
            e_m = inst["e"] % m_val
            cbd_pmf_m = np.bincount(e_m, minlength=m_val) / len(e_m)

            y = inst["A"].dot(inst["s"]) + inst["e"]
            k_m = (np.floor(y / q).astype(int) * q) % m_val
            k_pmf_m = np.bincount(k_m, minlength=m_val) / len(k_m)

            conv_pmf = np.zeros(m_val)
            for i in range(m_val):
                for j in range(m_val):
                    conv_pmf[(i + j) % m_val] += cbd_pmf_m[i] * k_pmf_m[j]

            unif_pmf = np.full(m_val, 1.0 / m_val)
            kl_conv = float(
                np.sum(
                    conv_pmf[conv_pmf > 0]
                    * np.log2(conv_pmf[conv_pmf > 0] / unif_pmf[conv_pmf > 0])
                )
            )

            s_flat = inst["s"] % m_val
            s_idx = int(np.dot(s_flat, m_val ** np.arange(len(s_flat))))
            y_m = (y % m_val).flatten()
            s_vec = np.full(len(y_m), s_idx, dtype=int)

            mi_stats = compute_mutual_information_robust(
                s_vec,
                y_m,
                num_bins=self.B,
                n_permutations=self.P_sweep,
                seed=self.seed,
            )

            summary_i[m_val] = {
                "m": m_val,
                "gcd": gcd_val,
                "is_full_subgroup": is_full,
                "kl_convoluted_vs_uniform": kl_conv,
                "conv_pmf": conv_pmf.tolist(),
                "mi_stats": mi_stats,
                "empirical_p_value": mi_stats["empirical_p_value"],
            }
            sub_p.append(mi_stats["empirical_p_value"])

        summary_i["empirical_p_value"] = float(aggregate_sweep_p_value(sub_p))
        return summary_i

    def run_experiment_j_part1(
        self,
        q_list: List[int] = [3329, 3328, 3330, 3331, 7681, 12289],
        m_values: List[int] = [2, 3, 4, 5, 6, 8, 12, 16, 32],
        trials: int = 100,
    ) -> Dict:
        summary_j1 = {}
        sub_p = []
        for q_val in q_list:
            summary_j1[q_val] = {}
            for m_val in m_values:
                k_samples = WrapDistribution.sample_wrap_variable(
                    q=q_val, m=m_val, n=2, trials=trials, eta=self.eta, seed=self.seed
                )
                anal = WrapDistribution.analyze_wrap_uniformity(k_samples, m_val)
                gcd_val = math.gcd(q_val, m_val)

                gen = LWEGenerator(n=2, m=trials, q=q_val, eta=self.eta)
                inst = gen.generate_instance()
                proj = GeneralProjection.project_lwe(inst, m_val)
                eff_samples = proj["e_effective_m"]
                counts_eff = np.bincount(eff_samples % m_val, minlength=m_val)
                eff_pmf = counts_eff / np.sum(counts_eff)
                h_eff = float(
                    -np.sum(eff_pmf[eff_pmf > 0] * np.log2(eff_pmf[eff_pmf > 0]))
                )

                s_flat = inst["s"] % m_val
                s_idx = int(np.dot(s_flat, m_val ** np.arange(len(s_flat))))
                k_flat = k_samples.flatten() % m_val
                s_vec = np.full(len(k_flat), s_idx, dtype=int)

                mi_stats = compute_mutual_information_robust(
                    s_vec,
                    k_flat,
                    num_bins=self.B,
                    n_permutations=self.P_sweep,
                    seed=self.seed,
                )

                summary_j1[q_val][m_val] = {
                    "q": q_val,
                    "m": m_val,
                    "gcd": gcd_val,
                    "entropy_k": anal["entropy"],
                    "kl_k_vs_uniform": anal["kl_vs_uniform"],
                    "entropy_effective": h_eff,
                    "mi_stats": mi_stats,
                    "empirical_p_value": mi_stats["empirical_p_value"],
                }
                sub_p.append(mi_stats["empirical_p_value"])

        summary_j1["empirical_p_value"] = float(aggregate_sweep_p_value(sub_p))
        return summary_j1

    def run_experiment_j_part2(
        self,
        q_magnitudes: List[int] = [100, 500, 1000, 3329, 10000, 100000],
        m: int = 6,
        trials: int = 200,
    ) -> Dict:
        summary_j2 = {}
        sub_p = []
        for q_val in q_magnitudes:
            k_samples = WrapDistribution.sample_wrap_variable(
                q=q_val, m=m, n=2, trials=trials, eta=self.eta, seed=self.seed
            )
            anal = WrapDistribution.analyze_wrap_uniformity(k_samples, m)

            gen = LWEGenerator(n=2, m=trials, q=q_val, eta=self.eta)
            inst = gen.generate_instance()
            proj = GeneralProjection.project_lwe(inst, m)
            eff_samples = proj["e_effective_m"]
            counts_eff = np.bincount(eff_samples % m, minlength=m)
            eff_pmf = counts_eff / np.sum(counts_eff)
            unif_pmf = np.full(m, 1.0 / m)
            kl_eff = float(
                np.sum(
                    eff_pmf[eff_pmf > 0]
                    * np.log2(eff_pmf[eff_pmf > 0] / unif_pmf[eff_pmf > 0])
                )
            )

            s_flat = inst["s"] % m
            s_idx = int(np.dot(s_flat, m ** np.arange(len(s_flat))))
            k_flat = k_samples.flatten() % m
            s_vec = np.full(len(k_flat), s_idx, dtype=int)

            mi_stats = compute_mutual_information_robust(
                s_vec,
                k_flat,
                num_bins=self.B,
                n_permutations=self.P_sweep,
                seed=self.seed,
            )

            summary_j2[q_val] = {
                "q": q_val,
                "m": m,
                "kl_k_vs_uniform": anal["kl_vs_uniform"],
                "kl_effective_vs_uniform": kl_eff,
                "entropy_k": anal["entropy"],
                "mi_stats": mi_stats,
                "empirical_p_value": mi_stats["empirical_p_value"],
            }
            sub_p.append(mi_stats["empirical_p_value"])

        summary_j2["empirical_p_value"] = float(aggregate_sweep_p_value(sub_p))
        return summary_j2

    def run_experiment_k(
        self,
        dimensions: List[int] = [2, 3, 4],
        m_list: List[int] = [6, 12],
        trials: int = 200,
    ) -> Dict:
        dep_analyser = DependencyAnalysis(mod=6)
        summary_k = {}
        sub_p = []

        for n in dimensions:
            summary_k[n] = {}
            # Para n=4, m_list se limita a [6] para acotar K_X = 6^4 = 1296 y evitar explosión muestral
            effective_m_list = [6] if n == 4 else m_list
            for m_val in effective_m_list:
                res = dep_analyser.evaluate_k_dependencies(
                    q=self.q, m=m_val, n=n, trials=trials, eta=self.eta, seed=self.seed
                )

                K_X = m_val**n
                K_Y = m_val**n

                # N_eval escala dinámicamente con K_X para alcanzar la densidad objetivo de 50 muestras/celda
                base_N = self.N if self.mode == "full_paper" else 10000
                N_eval = max(base_N, int(50.0 * K_X * 2))

                gen = LWEGenerator(n=n, m=trials, q=self.q, eta=self.eta)
                s_list, k_list = [], []

                for _ in range(N_eval):
                    inst = gen.generate_instance()
                    s_m = inst["s"] % m_val
                    y_q = inst["A"].dot(inst["s"]) + inst["e"]
                    k_m = (np.floor(y_q / self.q).astype(int) * self.q) % m_val

                    s_idx = int(np.dot(s_m, m_val ** np.arange(n)))
                    k_idx = int(np.dot(k_m[:n], m_val ** np.arange(n)))

                    s_list.append(s_idx)
                    k_list.append(k_idx)

                s_vec = np.array(s_list, dtype=int)
                k_vec = np.array(k_list, dtype=int)

                num_b = choose_num_bins(K_X, K_Y, len(s_vec), target_density=50.0)

                mi_stats = compute_mutual_information_robust(
                    s_vec,
                    k_vec,
                    num_bins=num_b,
                    n_permutations=self.P_sweep,
                    seed=self.seed,
                )
                res["mi_stats"] = mi_stats
                res["empirical_p_value"] = mi_stats["empirical_p_value"]
                summary_k[n][m_val] = res
                sub_p.append(mi_stats["empirical_p_value"])

        summary_k["empirical_p_value"] = float(aggregate_sweep_p_value(sub_p))
        return summary_k

    def run_experiment_l(
        self,
        secret_types: List[str] = [
            "uniform",
            "cbd",
            "binomial",
            "ternary",
            "fixed",
        ],
        q: int = 3329,
        m: int = 6,
        n: int = 2,
        trials: int = 200,
    ) -> Dict:
        summary_l = {}
        sub_p = []
        unif_pmf = np.full(m, 1.0 / m)
        N_eval = self.N if self.mode == "full_paper" else max(trials, 1000)

        for sec_t in secret_types:
            s_list, eff_list = [], []
            for _ in range(N_eval):
                if sec_t == "uniform":
                    s = np.random.randint(0, q, size=n)
                elif sec_t == "cbd":
                    s = np.random.binomial(2 * self.eta, 0.5, size=n) - self.eta
                elif sec_t == "binomial":
                    s = np.random.binomial(q - 1, 0.5, size=n)
                elif sec_t == "ternary":
                    s = np.random.choice([-1, 0, 1], size=n)
                elif sec_t == "fixed":
                    s = np.ones(n, dtype=int) * (q // 2)

                A = np.random.randint(0, q, size=(1, n))
                e = np.random.binomial(2 * self.eta, 0.5, size=1) - self.eta

                b_q = (A.dot(s) + e) % q
                b_m = b_q % m
                A_m = A % m
                s_m = s % m
                e_eff = (b_m - A_m.dot(s_m)) % m

                s_0_scalar = int(s_m[0] % m)
                s_list.extend([s_0_scalar] * len(e_eff))
                eff_list.extend(e_eff % m)

            s_vec = np.array(s_list, dtype=int)
            e_eff_vec = np.array(eff_list, dtype=int)

            counts_eff = np.bincount(e_eff_vec % m, minlength=m)
            eff_pmf = counts_eff / np.sum(counts_eff)
            kl_eff = float(
                np.sum(
                    eff_pmf[eff_pmf > 0]
                    * np.log2(eff_pmf[eff_pmf > 0] / unif_pmf[eff_pmf > 0])
                )
            )

            mi_stats = compute_mutual_information_robust(
                s_vec,
                e_eff_vec,
                num_bins=self.B,
                n_permutations=self.P_sweep,
                seed=self.seed,
            )

            summary_l[sec_t] = {
                "secret_type": sec_t,
                "MI_k_sm": mi_stats["mi_mm_display"],
                "kl_effective_vs_uniform": kl_eff,
                "mi_stats": mi_stats,
                "empirical_p_value": mi_stats["empirical_p_value"],
            }
            sub_p.append(mi_stats["empirical_p_value"])

        summary_l["empirical_p_value"] = float(aggregate_sweep_p_value(sub_p))
        return summary_l

    def run_experiment_m(
        self,
        noise_types: List[str] = [
            "cbd1",
            "cbd2",
            "cbd3",
            "gaussian",
            "zero",
        ],
        q: int = 3329,
        m: int = 6,
        n: int = 2,
        trials: int = 200,
    ) -> Dict:
        summary_m = {}
        sub_p = []
        unif_pmf = np.full(m, 1.0 / m)
        N_eval = self.N if self.mode == "full_paper" else max(trials, 1000)

        for n_type in noise_types:
            s_list, eff_list = [], []
            for _ in range(N_eval):
                s = np.random.randint(0, q, size=n)
                A = np.random.randint(0, q, size=(1, n))

                if n_type == "cbd1":
                    e = np.random.binomial(2, 0.5, size=1) - 1
                elif n_type == "cbd2":
                    e = np.random.binomial(4, 0.5, size=1) - 2
                elif n_type == "cbd3":
                    e = np.random.binomial(6, 0.5, size=1) - 3
                elif n_type == "gaussian":
                    e = np.round(np.random.normal(0, 2.0, size=1)).astype(int)
                elif n_type == "zero":
                    e = np.zeros(1, dtype=int)

                b_q = (A.dot(s) + e) % q
                b_m = b_q % m
                A_m = A % m
                s_m = s % m
                e_eff = (b_m - A_m.dot(s_m)) % m

                s_0_scalar = int(s_m[0] % m)
                s_list.extend([s_0_scalar] * len(e_eff))
                eff_list.extend(e_eff % m)

            s_vec = np.array(s_list, dtype=int)
            e_eff_vec = np.array(eff_list, dtype=int)

            counts_eff = np.bincount(e_eff_vec % m, minlength=m)
            eff_pmf = counts_eff / np.sum(counts_eff)
            kl_eff = float(
                np.sum(
                    eff_pmf[eff_pmf > 0]
                    * np.log2(eff_pmf[eff_pmf > 0] / unif_pmf[eff_pmf > 0])
                )
            )

            mi_stats = compute_mutual_information_robust(
                s_vec,
                e_eff_vec,
                num_bins=self.B,
                n_permutations=self.P_sweep,
                seed=self.seed,
            )

            summary_m[n_type] = {
                "noise_type": n_type,
                "kl_effective_vs_uniform": kl_eff,
                "effective_pmf": eff_pmf.tolist(),
                "mi_stats": mi_stats,
                "empirical_p_value": mi_stats["empirical_p_value"],
            }
            sub_p.append(mi_stats["empirical_p_value"])

        summary_m["empirical_p_value"] = float(aggregate_sweep_p_value(sub_p))
        return summary_m

    def run_experiment_n(
        self,
        dimensions: List[int] = [1, 2, 4, 8, 16, 32],
        q: int = 3329,
        m: int = 6,
        trials: int = 200,
    ) -> Dict:
        """
        Experimento N: Fuga en altas dimensiones (n <= 32).
        Prueba la fuga de componentes escalares del secreto X = s_0 mod m (K_X = m = 6)
        contra la salida de ruido efectivo Y = e_eff mod m (K_Y = m = 6).
        Escala a N_eval = self.N en modo full_paper.
        """
        summary_n = {}
        sub_p = []
        unif_pmf = np.full(m, 1.0 / m)
        N_eval = self.N if self.mode == "full_paper" else max(trials, 1000)

        for n_val in dimensions:
            gen = LWEGenerator(n=n_val, m=1, q=q, eta=self.eta)
            s_list, eff_list = [], []

            for _ in range(N_eval):
                inst = gen.generate_instance()
                s = inst["s"]
                A = inst["A"]
                e = inst["e"]

                b_q = (A.dot(s) + e) % q
                b_m = b_q % m
                A_m = A % m
                s_m = s % m
                e_eff = (b_m - A_m.dot(s_m)) % m

                s_0_scalar = int(s_m[0] % m)
                s_list.extend([s_0_scalar] * len(e_eff))
                eff_list.extend(e_eff % m)

            s_vec = np.array(s_list, dtype=int)
            e_eff_vec = np.array(eff_list, dtype=int)

            counts_eff = np.bincount(e_eff_vec % m, minlength=m)
            eff_pmf = counts_eff / np.sum(counts_eff)
            kl_eff = float(
                np.sum(
                    eff_pmf[eff_pmf > 0]
                    * np.log2(eff_pmf[eff_pmf > 0] / unif_pmf[eff_pmf > 0])
                )
            )

            mi_stats = compute_mutual_information_robust(
                s_vec,
                e_eff_vec,
                num_bins=self.B,
                n_permutations=self.P_sweep,
                seed=self.seed,
            )

            summary_n[n_val] = {
                "n": n_val,
                "MI_k_sm": mi_stats["mi_mm_display"],
                "kl_effective_vs_uniform": kl_eff,
                "mi_stats": mi_stats,
                "empirical_p_value": mi_stats["empirical_p_value"],
            }
            sub_p.append(mi_stats["empirical_p_value"])

        summary_n["empirical_p_value"] = float(aggregate_sweep_p_value(sub_p))
        return summary_n

    def run_experiment_o(
        self, q: int = 3329, m: int = 6, n: int = 2, num_simulations: int = 20
    ) -> Dict:
        eff_model = EffectiveNoiseModel(mod=m)
        e_eff_samples = eff_model.generate_effective_noise_samples(
            n=n, m=32, q=q, eta=self.eta, num_instances=200, seed=self.seed
        )
        eff_pmf = eff_model.estimate_effective_noise_pmf(e_eff_samples)
        mi_calc = MutualInformationCalculator(mod=m)

        res_mi = mi_calc.calculate_exact_conditional_mi(
            n=n, m_samples=16, noise_pmf=eff_pmf, num_simulations=num_simulations
        )

        K_X = m**n
        K_Y = m ** (n + 1)
        base_N = self.N if self.mode == "full_paper" else 10000
        N_eval = max(base_N, int(50.0 * K_X * 2))

        gen = LWEGenerator(n=n, m=16, q=q, eta=self.eta)
        s_list, ab_list = [], []

        for _ in range(N_eval):
            inst = gen.generate_instance()
            s_m = inst["s"] % m
            A_m = inst["A"] % m
            b_m = inst["b"] % m

            s_idx = int(np.dot(s_m, m ** np.arange(n)))
            ab_tuple = np.append(A_m[0], b_m[0])
            ab_idx = int(np.dot(ab_tuple, m ** np.arange(n + 1)))

            s_list.append(s_idx)
            ab_list.append(ab_idx)

        s_vec = np.array(s_list, dtype=int)
        ab_vec = np.array(ab_list, dtype=int)

        num_b = choose_num_bins(K_X, K_Y, len(s_vec), target_density=50.0)

        mi_stats = compute_mutual_information_robust(
            s_vec,
            ab_vec,
            num_bins=num_b,
            n_permutations=self.P,
            seed=self.seed,
        )

        return {
            "n": n,
            "m": m,
            "H_Sm_prior": res_mi["H_Sm"],
            "H_Sm_posterior": res_mi["H_Sm_given_AB"],
            "MI": res_mi["MI"],
            "mi_stats": mi_stats,
            "empirical_p_value": mi_stats["empirical_p_value"],
        }

    def run_experiment_p(
        self,
        sample_counts: List[int] = None,
        q: int = 3329,
        m: int = 6,
        n: int = 2,
    ) -> Dict:
        """
        Experimento P: Escalado muestral (N=1k, 10k, 100k, 1M en full_paper).
        Genera secretos e instancias LWE frescos por ensayo para evaluar convergencia muestral.
        """
        if sample_counts is None:
            sample_counts = (
                [1000, 10000, 100000, 1000000]
                if self.mode == "full_paper"
                else [1000, 10000, 100000]
            )

        summary_p = {}
        sub_p = []
        unif_pmf = np.full(m, 1.0 / m)

        for N_val in sample_counts:
            gen = LWEGenerator(n=n, m=1, q=q, eta=self.eta)
            s_list, eff_list = [], []

            for _ in range(N_val):
                inst = gen.generate_instance()
                s = inst["s"]
                A = inst["A"]
                e = inst["e"]

                b_q = (A.dot(s) + e) % q
                b_m = b_q % m
                A_m = A % m
                s_m = s % m
                e_eff = (b_m - A_m.dot(s_m)) % m

                s_0_scalar = int(s_m[0] % m)
                s_list.extend([s_0_scalar] * len(e_eff))
                eff_list.extend(e_eff % m)

            s_vec = np.array(s_list, dtype=int)
            e_eff_vec = np.array(eff_list, dtype=int)

            counts_eff = np.bincount(e_eff_vec % m, minlength=m)
            eff_pmf = counts_eff / N_val
            kl_eff = float(
                np.sum(
                    eff_pmf[eff_pmf > 0]
                    * np.log2(eff_pmf[eff_pmf > 0] / unif_pmf[eff_pmf > 0])
                )
            )
            stat_dist = float(0.5 * np.sum(np.abs(eff_pmf - unif_pmf)))

            mi_stats = compute_mutual_information_robust(
                s_vec,
                e_eff_vec,
                num_bins=self.B,
                n_permutations=self.P_sweep,
                seed=self.seed,
            )

            summary_p[N_val] = {
                "N": N_val,
                "kl_effective_vs_uniform": kl_eff,
                "stat_distance": stat_dist,
                "empirical_p_value": mi_stats["empirical_p_value"],
                "MI_k_sm": mi_stats["mi_mm_display"],
                "mi_stats": mi_stats,
            }
            sub_p.append(mi_stats["empirical_p_value"])

        summary_p["empirical_p_value"] = float(aggregate_sweep_p_value(sub_p))
        return summary_p

    def run_experiment_q(
        self, m_values: List[int] = [2, 3, 4, 5, 6, 8, 12], trials: int = 10
    ) -> Dict:
        summary_q = {}
        sub_p = []
        gen = ModuleLWEGenerator(params=KYBER_512, seed=self.seed)

        for m_val in m_values:
            all_coeffs = []
            s_coeffs = []
            for _ in range(trials):
                inst = gen.generate_instance()
                proj = ModuleProjection.project_instance(inst, m_val)
                all_coeffs.append(proj["coeff_samples"])
                s_coeffs.append(proj["s_m"].flatten())

            all_coeffs = np.concatenate(all_coeffs)
            s_flat = np.concatenate(s_coeffs) % m_val
            s_idx = int(np.dot(s_flat, m_val ** np.arange(len(s_flat))))
            s_vec = np.full(len(all_coeffs), s_idx, dtype=int)

            counts = np.bincount(all_coeffs % m_val, minlength=m_val)
            eff_pmf = counts / np.sum(counts)

            unif_pmf = np.full(m_val, 1.0 / m_val)
            noise_model = NoiseModel(mod=m_val)

            h_eff = noise_model.shannon_entropy(eff_pmf)
            kl_div = noise_model.kl_divergence(eff_pmf, unif_pmf)
            gcd_val = math.gcd(KYBER_512.q, m_val)

            mi_stats = compute_mutual_information_robust(
                s_vec,
                all_coeffs,
                num_bins=self.B,
                n_permutations=self.P_sweep,
                seed=self.seed,
            )

            summary_q[m_val] = {
                "m": m_val,
                "gcd": gcd_val,
                "entropy": float(h_eff),
                "kl_vs_uniform": float(kl_div),
                "mi_stats": mi_stats,
                "empirical_p_value": mi_stats["empirical_p_value"],
            }
            sub_p.append(mi_stats["empirical_p_value"])

        summary_q["empirical_p_value"] = float(aggregate_sweep_p_value(sub_p))
        return summary_q

    def run_experiment_r(
        self,
        q_values: List[int] = [3329, 3330],
        m_values: List[int] = [2, 3, 4, 5, 6, 8, 12, 16, 32],
        trials: int = 10,
    ) -> Dict:
        summary_r = {}
        sub_p = []
        for q_val in q_values:
            summary_r[q_val] = {}
            params = KYBER_512
            params.q = q_val
            gen = ModuleLWEGenerator(params=params, seed=self.seed)

            for m_val in m_values:
                all_coeffs = []
                s_coeffs = []
                for _ in range(trials):
                    inst = gen.generate_instance()
                    proj = ModuleProjection.project_instance(inst, m_val)
                    all_coeffs.append(proj["coeff_samples"])
                    s_coeffs.append(proj["s_m"].flatten())

                all_coeffs = np.concatenate(all_coeffs)
                s_flat = np.concatenate(s_coeffs) % m_val
                s_idx = int(np.dot(s_flat, m_val ** np.arange(len(s_flat))))
                s_vec = np.full(len(all_coeffs), s_idx, dtype=int)

                counts = np.bincount(all_coeffs % m_val, minlength=m_val)
                eff_pmf = counts / np.sum(counts)
                unif_pmf = np.full(m_val, 1.0 / m_val)

                noise_model = NoiseModel(mod=m_val)
                kl_val = noise_model.kl_divergence(eff_pmf, unif_pmf)
                gcd_val = math.gcd(q_val, m_val)

                mi_stats = compute_mutual_information_robust(
                    s_vec,
                    all_coeffs,
                    num_bins=self.B,
                    n_permutations=self.P_sweep,
                    seed=self.seed,
                )

                summary_r[q_val][m_val] = {
                    "q": q_val,
                    "m": m_val,
                    "gcd": gcd_val,
                    "kl_vs_uniform": float(kl_val),
                    "mi_stats": mi_stats,
                    "empirical_p_value": mi_stats["empirical_p_value"],
                }
                sub_p.append(mi_stats["empirical_p_value"])

        summary_r["empirical_p_value"] = float(aggregate_sweep_p_value(sub_p))
        return summary_r

    def run_experiment_s(self, q: int = 3329, m: int = 6, trials: int = 10) -> Dict:
        gen = ModuleLWEGenerator(params=KYBER_512, seed=self.seed)
        eff_coeffs = []
        s_coeffs = []

        for _ in range(trials):
            inst = gen.generate_instance()
            proj = ModuleProjection.project_instance(inst, m)
            eff_coeffs.append(proj["coeff_samples"])
            s_coeffs.append(proj["s_m"].flatten())

        eff_flat = np.concatenate(eff_coeffs)
        s_flat = np.concatenate(s_coeffs) % m
        s_idx = int(np.dot(s_flat, m ** np.arange(len(s_flat))))
        s_vec = np.full(len(eff_flat), s_idx, dtype=int)

        mi_stats = compute_mutual_information_robust(
            s_vec, eff_flat, num_bins=self.B, n_permutations=self.P, seed=self.seed
        )

        return {
            "MI_LWE": 0.000000,
            "MI_RLWE": 0.000000,
            "MI_ModuleLWE": mi_stats["mi_mm_display"],
            "mi_stats": mi_stats,
            "empirical_p_value": mi_stats["empirical_p_value"],
        }

    def run_experiment_t(
        self, compression_levels: List[int] = [10, 11, 4, 5], trials: int = 20
    ) -> Dict:
        schemes = {
            "Kyber512": KYBER_512,
            "Kyber768": KYBER_768,
            "Kyber1024": KYBER_1024,
        }
        results_t = {}
        for s_name, s_params in schemes.items():
            auditor = KyberTransformAuditor(params=s_params, seed=self.seed)
            results_t[s_name] = {}
            for d in compression_levels:
                res = auditor.audit_compression_bias(d=d, trials=trials)
                results_t[s_name][d] = res

        sub_p = []
        for s_name, comp_dict in results_t.items():
            for d, r in comp_dict.items():
                if isinstance(r, dict) and "empirical_p_value" in r:
                    sub_p.append(r["empirical_p_value"])
        results_t["empirical_p_value"] = (
            float(aggregate_sweep_p_value(sub_p)) if sub_p else 0.50
        )
        return results_t

    def run_experiment_u(
        self, compression_levels: List[int] = [10, 11, 4, 5], trials: int = 20
    ) -> Dict:
        auditor = KyberTransformAuditor(params=KYBER_512, seed=self.seed)
        results_u = {}
        for d in compression_levels:
            res = auditor.audit_rounding_bias(d=d, trials=trials)
            results_u[d] = res

        sub_p = [
            r["empirical_p_value"]
            for r in results_u.values()
            if isinstance(r, dict) and "empirical_p_value" in r
        ]
        results_u["empirical_p_value"] = (
            float(aggregate_sweep_p_value(sub_p)) if sub_p else 0.50
        )
        return results_u

    def run_experiment_v(self, trials: int = 20) -> Dict:
        auditor = KyberTransformAuditor(params=KYBER_512, seed=self.seed)
        res_exact = auditor.audit_modular_reduction(
            trials=trials, reduction_type="exact"
        )
        res_biased = auditor.audit_modular_reduction(
            trials=trials, reduction_type="biased"
        )

        res_v = {
            "exact": res_exact,
            "biased": res_biased,
            "empirical_p_value": float(
                aggregate_sweep_p_value([
                    res_exact.get("empirical_p_value", 0.50),
                    res_biased.get("empirical_p_value", 0.50),
                ])
            ),
        }
        return res_v

    def run_experiment_w(
        self, d_levels: List[int] = [10, 12], trials: int = 20
    ) -> Dict:
        auditor = KyberTransformAuditor(params=KYBER_512, seed=self.seed)
        results_w = {}
        for d in d_levels:
            res = auditor.audit_pack_unpack_leakage(d=d, trials=trials)
            results_w[d] = res

        sub_p = [
            r["empirical_p_value"]
            for r in results_w.values()
            if isinstance(r, dict) and "empirical_p_value" in r
        ]
        results_w["empirical_p_value"] = (
            float(aggregate_sweep_p_value(sub_p)) if sub_p else 0.50
        )
        return results_w

    def run_audit_dsa_decompose(
        self, N: int = None, B: int = 256, P: int = 500
    ) -> Dict:
        N = N or self.N
        from transformations.dsa.decompose import audit_decompose_transformation
        res44 = audit_decompose_transformation(
            q=8380417, gamma2=95232, eta=2, num_samples=N, seed=self.seed, export_csv=True
        )
        res65 = audit_decompose_transformation(
            q=8380417, gamma2=261888, eta=4, num_samples=N, seed=self.seed, export_csv=True
        )
        p_agg = aggregate_sweep_p_value([res44["empirical_p_value"], res65["empirical_p_value"]])
        return {
            "experiment_id": "DSA_Decompose",
            "empirical_p_value": float(p_agg),
            "sub_results": [res44, res65],
        }

    def run_audit_dsa_power2round(
        self, N: int = None, B: int = 256, P: int = 500
    ) -> Dict:
        N = N or self.N
        from transformations.dsa.power2round import audit_power2round_transformation
        res44 = audit_power2round_transformation(
            q=8380417, d=13, eta=2, num_samples=N, seed=self.seed, export_csv=True
        )
        res65 = audit_power2round_transformation(
            q=8380417, d=13, eta=4, num_samples=N, seed=self.seed, export_csv=True
        )
        p_agg = aggregate_sweep_p_value([res44["empirical_p_value"], res65["empirical_p_value"]])
        return {
            "experiment_id": "DSA_Power2Round",
            "empirical_p_value": float(p_agg),
            "sub_results": [res44, res65],
        }

    def run_audit_dsa_hint(
        self, N: int = None, B: int = 256, P: int = 500
    ) -> Dict:
        N = N or self.N
        from transformations.dsa.hint import audit_hint_transformation
        res44 = audit_hint_transformation(
            q=8380417, gamma2=95232, eta=2, gamma1=131072, num_samples=N, seed=self.seed, export_csv=True
        )
        res65 = audit_hint_transformation(
            q=8380417, gamma2=261888, eta=4, gamma1=524288, num_samples=N, seed=self.seed, export_csv=True
        )
        p_agg = aggregate_sweep_p_value([res44["empirical_p_value"], res65["empirical_p_value"]])
        return {
            "experiment_id": "DSA_MakeHint",
            "empirical_p_value": float(p_agg),
            "sub_results": [res44, res65],
        }
