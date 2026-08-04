import numpy as np
import math
from typing import Dict, Any
from scipy.stats import chisquare

from schemes.module_lwe.kyber import ModuleLWEGenerator
from schemes.module_lwe.parameters import KyberParams, KYBER_512
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

class KyberTransformAuditor:
    """
    Auditor de Transformaciones Nivel Implementación para ML-KEM / Kyber.
    Analiza compresión, redondeo, reducción modular y empaquetamiento de coeficientes.
    """

    def __init__(self, params: KyberParams = KYBER_512, seed: int = 42):
        self.params = params
        self.generator = ModuleLWEGenerator(params=params, seed=seed)

    def audit_compression_bias(self, d: int = 10, trials: int = 50) -> Dict[str, Any]:
        """
        Audita el sesgo introducido por la compresión en Z_{2^d}.
        Mide H(coef_comprimido), KL vs uniforme, distancia estadística e I(secret; compressed).
        """
        compressed_coeffs = []
        secrets = []

        for _ in range(trials):
            inst = self.generator.generate_instance()
            b = inst['b']
            s = inst['s']
            c_b = compress_q(b, self.params.q, d)
            compressed_coeffs.append(c_b.flatten())
            secrets.append(s.flatten())

        all_comp = np.concatenate(compressed_coeffs)
        all_sec = np.concatenate(secrets)

        bins_d = 1 << d
        counts = np.bincount(all_comp, minlength=bins_d)
        emp_pmf = counts / float(np.sum(counts))
        unif_pmf = np.full(bins_d, 1.0 / bins_d)

        h_emp = compute_entropy(all_comp, num_bins=bins_d)
        h_max = float(d)
        kl_div = compute_kl_divergence(emp_pmf, unif_pmf)
        stat_dist = compute_statistical_distance(emp_pmf, unif_pmf)

        # Muestra esperada para Chi^2
        exp_counts = unif_pmf * len(all_comp)
        exp_counts = np.maximum(exp_counts, 1e-6)
        chi2_stat, p_val = chisquare(counts, f_exp=exp_counts)

        mi_secret = compute_mutual_information(all_sec, all_comp, bins_y=bins_d)

        # Ventaja Atacante Bayesiano
        p_prior = 1.0 / bins_d
        p_max_obs = float(np.max(emp_pmf))
        bayes_gain = float(max(0.0, p_max_obs - p_prior))

        from transformations.dsa.audit_utils import compute_mutual_information_robust
        mi_stats = compute_mutual_information_robust(
            s_vec=all_sec,
            out_vec=all_comp,
            num_bins=256,
            n_permutations=50,
            seed=42
        )

        if kl_div < 0.05 and bayes_gain < 0.01:
            interpretation = "Compress transformation preserves high uniformity (Low risk)"
        else:
            interpretation = "WARNING: Compression introduces detectable statistical bias or variance reduction"

        return {
            'scheme': self.params.name,
            'transformation': 'compression',
            'd': d,
            'entropy_before': float(np.log2(self.params.q)),
            'entropy_after': float(h_emp),
            'max_entropy_after': h_max,
            'kl_divergence': float(kl_div),
            'statistical_distance': float(stat_dist),
            'chi2_stat': float(chi2_stat),
            'chi2_pvalue': float(p_val),
            'chi2_p_value': float(p_val),
            'empirical_p_value': mi_stats['empirical_p_value'],
            'mi_mm_display': mi_stats['mi_mm_display'],
            'mutual_information': float(mi_secret),
            'bayesian_attacker_gain': bayes_gain,
            'interpretation': interpretation
        }

    def audit_rounding_bias(self, d: int = 10, trials: int = 50) -> Dict[str, Any]:
        """
        Audita el ruido introducido por el ciclo round-trip (Compress_d -> Decompress_d).
        """
        rounding_errors = []
        secrets = []

        for _ in range(trials):
            inst = self.generator.generate_instance()
            b = inst['b']
            s = inst['s']
            sim = simulate_kyber_rounding(b, self.params.q, d)
            rounding_errors.append(sim['rounding_error'].flatten())
            secrets.append(s.flatten())

        all_err = np.concatenate(rounding_errors)
        all_sec = np.concatenate(secrets)

        # Distribución del error de redondeo
        shift_err = all_err + (self.params.q // 2)
        bins_err = self.params.q
        counts = np.bincount(shift_err, minlength=bins_err)
        emp_pmf = counts[counts > 0] / float(np.sum(counts))

        h_err = compute_entropy(shift_err, num_bins=bins_err)
        mean_err = float(np.mean(all_err))
        std_err = float(np.std(all_err))

        # Divergencia KL comparada con una distribución de error redondeado ideal acotada
        max_round_err = self.params.q / float(1 << (d + 1))
        ideal_width = max(1, int(2 * max_round_err + 1))
        unif_err_pmf = np.full(ideal_width, 1.0 / ideal_width)

        obs_width_counts = counts[counts > 0]
        obs_width_pmf = obs_width_counts / float(np.sum(obs_width_counts))

        if len(obs_width_pmf) == len(unif_err_pmf):
            kl_div = compute_kl_divergence(obs_width_pmf, unif_err_pmf)
            stat_dist = compute_statistical_distance(obs_width_pmf, unif_err_pmf)
        else:
            kl_div = float(abs(h_err - np.log2(ideal_width)))
            stat_dist = float(abs(1.0 - (len(obs_width_pmf) / float(ideal_width))))

        mi_secret = compute_mutual_information(all_sec, shift_err, bins_y=bins_err)
        bayes_gain = float(max(0.0, (1.0 / len(obs_width_pmf)) - (1.0 / ideal_width))) if len(obs_width_pmf) > 0 else 0.0

        from transformations.dsa.audit_utils import compute_mutual_information_robust
        mi_stats = compute_mutual_information_robust(
            s_vec=all_sec,
            out_vec=all_err,
            num_bins=256,
            n_permutations=50,
            seed=42
        )

        if abs(mean_err) < 0.5 and mi_secret < 0.05:
            interpretation = "Rounding introduces zero-centered bounded error with negligible secret correlation"
        else:
            interpretation = "WARNING: Rounding error is non-zero centered or exhibits dependence with secret"

        return {
            'scheme': self.params.name,
            'transformation': 'rounding',
            'd': d,
            'entropy_rounding_error': float(h_err),
            'mean_error': mean_err,
            'std_error': std_err,
            'kl_divergence': float(kl_div),
            'statistical_distance': float(stat_dist),
            'empirical_p_value': mi_stats['empirical_p_value'],
            'mi_mm_display': mi_stats['mi_mm_display'],
            'mutual_information': float(mi_secret),
            'bayesian_attacker_gain': bayes_gain,
            'interpretation': interpretation
        }

    def audit_modular_reduction(self, trials: int = 50, reduction_type: str = "biased") -> Dict[str, Any]:
        """
        Audita el comportamiento de reducciones modulares reales/imprecisas frente a la reducción exacta mod q.
        """
        raw_values = []
        reduced_values = []
        secrets = []

        for _ in range(trials):
            inst = self.generator.generate_instance()
            b = inst['b']
            s = inst['s']
            # b + un desplazamiento arbitrario para evaluar reducción
            raw = b + np.random.randint(0, 2 * self.params.q, size=b.shape)
            red = modular_reduce(raw, self.params.q, mode=reduction_type)
            raw_values.append(raw.flatten())
            reduced_values.append(red.flatten())
            secrets.append(s.flatten())

        all_red = np.concatenate(reduced_values)
        all_sec = np.concatenate(secrets)

        counts = np.bincount(all_red % self.params.q, minlength=self.params.q)
        emp_pmf = counts / float(np.sum(counts))
        unif_pmf = np.full(self.params.q, 1.0 / self.params.q)

        h_emp = compute_entropy(all_red % self.params.q, num_bins=self.params.q)
        h_max = float(np.log2(self.params.q))
        kl_div = compute_kl_divergence(emp_pmf, unif_pmf)
        stat_dist = compute_statistical_distance(emp_pmf, unif_pmf)

        exp_counts = unif_pmf * len(all_red)
        exp_counts = np.maximum(exp_counts, 1e-6)
        chi2_stat, p_val = chisquare(counts, f_exp=exp_counts)

        mi_secret = compute_mutual_information(all_sec, all_red % self.params.q, bins_y=self.params.q)
        bayes_gain = float(max(0.0, np.max(emp_pmf) - (1.0 / self.params.q)))

        from transformations.dsa.audit_utils import compute_mutual_information_robust
        mi_stats = compute_mutual_information_robust(
            s_vec=all_sec,
            out_vec=all_red % self.params.q,
            num_bins=256,
            n_permutations=50,
            seed=42
        )

        if reduction_type == "exact":
            interpretation = "Exact modular reduction preserves complete coefficient distribution integrity"
        else:
            interpretation = "WARNING: Biased modular reduction introduces observable frequency skewness"

        return {
            'scheme': self.params.name,
            'transformation': f'modular_reduction_{reduction_type}',
            'reduction_type': reduction_type,
            'entropy_before': h_max,
            'entropy_after': float(h_emp),
            'kl_divergence': float(kl_div),
            'statistical_distance': float(stat_dist),
            'chi2_stat': float(chi2_stat),
            'chi2_pvalue': float(p_val),
            'chi2_p_value': float(p_val),
            'empirical_p_value': mi_stats['empirical_p_value'],
            'mi_mm_display': mi_stats['mi_mm_display'],
            'mutual_information': float(mi_secret),
            'bayesian_attacker_gain': bayes_gain,
            'interpretation': interpretation
        }

    def audit_pack_unpack_leakage(self, d: int = 12, trials: int = 50) -> Dict[str, Any]:
        """
        Audita el flujo de bytes serializado producido por coefficient_pack / coefficient_unpack.
        Mide la entropía a nivel de byte (frente a 8 bits) y sesgos en el empaquetado.
        """
        all_bytes = bytearray()
        secrets = []

        for _ in range(trials):
            inst = self.generator.generate_instance()
            b = inst['b']
            s = inst['s']
            poly = b[0] # tomar el primer polinomio del vector
            packed_bytes = coefficient_pack(poly, self.params.q, d)
            all_bytes.extend(packed_bytes)
            secrets.append(s[0].flatten())

        byte_arr = np.frombuffer(bytes(all_bytes), dtype=np.uint8)
        counts = np.bincount(byte_arr, minlength=256)
        emp_pmf = counts / float(np.sum(counts))
        unif_pmf = np.full(256, 1.0 / 256)

        h_byte = compute_entropy(byte_arr, num_bins=256)
        h_max = 8.0
        kl_div = compute_kl_divergence(emp_pmf, unif_pmf)
        stat_dist = compute_statistical_distance(emp_pmf, unif_pmf)

        exp_counts = unif_pmf * len(byte_arr)
        exp_counts = np.maximum(exp_counts, 1e-6)
        chi2_stat, p_val = chisquare(counts, f_exp=exp_counts)

        # Mide la información mutua del secreto con la muestra de bytes reducida
        sec_sample = np.concatenate(secrets)[:len(byte_arr)]
        byte_sample = byte_arr[:len(sec_sample)]
        mi_secret = compute_mutual_information(sec_sample, byte_sample, bins_y=256)
        bayes_gain = float(max(0.0, np.max(emp_pmf) - (1.0 / 256)))

        from transformations.dsa.audit_utils import compute_mutual_information_robust
        mi_stats = compute_mutual_information_robust(
            s_vec=sec_sample,
            out_vec=byte_sample,
            num_bins=256,
            n_permutations=50,
            seed=42
        )

        if kl_div < 0.05 and bayes_gain < 0.02:
            interpretation = "Byte packing stream exhibits high byte-entropy and no structural leakage"
        else:
            interpretation = "WARNING: Coefficient bit-packing produces non-uniform byte distribution"

        return {
            'scheme': self.params.name,
            'transformation': 'pack_unpack',
            'd': d,
            'byte_entropy': float(h_byte),
            'max_byte_entropy': h_max,
            'kl_divergence': float(kl_div),
            'statistical_distance': float(stat_dist),
            'chi2_stat': float(chi2_stat),
            'chi2_pvalue': float(p_val),
            'chi2_p_value': float(p_val),
            'empirical_p_value': mi_stats['empirical_p_value'],
            'mi_mm_display': mi_stats['mi_mm_display'],
            'mutual_information': float(mi_secret),
            'bayesian_attacker_gain': bayes_gain,
            'interpretation': interpretation
        }

    def audit_secret_leakage_after_transform(self, transformation_name: str = "compression",
                                             transform_kwargs: Dict = None, trials: int = 50) -> Dict[str, Any]:
        """
        Método genérico para evaluar filtración respecto al secreto tras cualquier transformador Kyber.
        """
        if transform_kwargs is None:
            transform_kwargs = {'d': 10}

        if transformation_name == "compression":
            res = self.audit_compression_bias(d=transform_kwargs.get('d', 10), trials=trials)
        elif transformation_name == "rounding":
            res = self.audit_rounding_bias(d=transform_kwargs.get('d', 10), trials=trials)
        elif transformation_name == "modular_reduction":
            res = self.audit_modular_reduction(trials=trials, reduction_type=transform_kwargs.get('reduction_type', 'biased'))
        elif transformation_name == "pack_unpack":
            res = self.audit_pack_unpack_leakage(d=transform_kwargs.get('d', 12), trials=trials)
        else:
            raise ValueError(f"Transformación desconocida: {transformation_name}")

        return res
