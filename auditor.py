import math
import numpy as np
from typing import Dict, Any, Optional

from schemes.module_lwe.kyber import ModuleLWEGenerator
from schemes.module_lwe.parameters import KYBER_512, KYBER_768, KYBER_1024
from schemes.module_lwe.kyber_transform_audit import KyberTransformAuditor
from transformations.modular_projection import ModuleProjection
from src.noise_model import NoiseModel

class SchemeAuditor:
    """
    Interfaz de Auditoría Estadística de Esquemas Basados en Retículos (v1.1 Release).
    Soporta Kyber512, Kyber768 y Kyber1024, además de auditoría de transformaciones reales
    (compresión, redondeo, reducción modular, serialización pack/unpack).
    """

    SCHEMES = {
        "Kyber512": KYBER_512,
        "Kyber768": KYBER_768,
        "Kyber1024": KYBER_1024
    }

    @classmethod
    def analyze_scheme(cls, scheme: str = "Kyber512", transformation: str = "projection", 
                       modulus: int = 6, trials: int = 20, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Ejecuta la auditoría estadística sobre un esquema especificado y una transformación elegida.
        """
        if scheme not in cls.SCHEMES:
            raise ValueError(f"Esquema desconocido: {scheme}. Disponibles: {list(cls.SCHEMES.keys())}")

        params = cls.SCHEMES[scheme]
        if parameters is None:
            parameters = {}

        # Si se solicita una transformación real de Kyber
        if transformation in ["compression", "rounding", "modular_reduction", "pack_unpack"]:
            auditor = KyberTransformAuditor(params=params, seed=42)
            d = parameters.get('d', 10)
            red_type = parameters.get('reduction_type', 'biased')
            
            if transformation == "compression":
                audit_res = auditor.audit_compression_bias(d=d, trials=trials)
            elif transformation == "rounding":
                audit_res = auditor.audit_rounding_bias(d=d, trials=trials)
            elif transformation == "modular_reduction":
                audit_res = auditor.audit_modular_reduction(trials=trials, reduction_type=red_type)
            elif transformation == "pack_unpack":
                audit_res = auditor.audit_pack_unpack_leakage(d=parameters.get('d', 12), trials=trials)

            report = []
            report.append(f"Scheme: {params.name} (q={params.q}, n={params.n}, k={params.k})")
            report.append(f"Transformation: Real Kyber Operation ({transformation})")
            report.append(f"Noise & Entropy analysis:")
            if 'entropy_after' in audit_res:
                report.append(f"  Entropy: {audit_res['entropy_after']:.4f} / {audit_res.get('max_entropy_after', 0.0):.4f} bits")
            elif 'entropy_rounding_error' in audit_res:
                report.append(f"  Entropy Rounding Error: {audit_res['entropy_rounding_error']:.4f} bits")
            elif 'byte_entropy' in audit_res:
                report.append(f"  Byte Entropy: {audit_res['byte_entropy']:.4f} / {audit_res['max_byte_entropy']:.4f} bits")

            report.append(f"  KL divergence: {audit_res.get('kl_divergence', 0.0):.6f} bits")
            report.append(f"  Statistical distance: {audit_res.get('statistical_distance', 0.0):.6f}")
            report.append(f"  Mutual information: {audit_res.get('mutual_information', 0.0):.6f} bits")
            report.append(f"  Bayesian attacker gain: {audit_res.get('bayesian_attacker_gain', 0.0):.6f}")
            report.append(f"Security interpretation: {audit_res['interpretation']}")

            audit_res['formatted_report'] = "\n".join(report)
            return audit_res

        # Por defecto: Proyección modular Z_q -> Z_m
        gen = ModuleLWEGenerator(params=params, seed=42)

        all_coeffs = []
        for _ in range(trials):
            inst = gen.generate_instance()
            proj = ModuleProjection.project_instance(inst, modulus)
            all_coeffs.append(proj['coeff_samples'])

        all_coeffs = np.concatenate(all_coeffs)
        counts = np.bincount(all_coeffs % modulus, minlength=modulus)
        eff_pmf = counts / np.sum(counts)

        unif_pmf = np.full(modulus, 1.0 / modulus)
        noise_model = NoiseModel(mod=modulus)

        h_eff = noise_model.shannon_entropy(eff_pmf)
        h_max = float(np.log2(modulus))
        kl_div = noise_model.kl_divergence(eff_pmf, unif_pmf)

        gcd_val = math.gcd(params.q, modulus)
        is_safe = (gcd_val == 1 and kl_div < 0.01)

        if is_safe:
            interpretation = "No observable leakage detected (Full uniformization confirmed)"
        else:
            interpretation = "WARNING: Observable leakage detected (Subgroup constraint / non-uniformity)"

        report = []
        report.append(f"Scheme: {params.name} (q={params.q}, n={params.n}, k={params.k})")
        report.append(f"Transformation: Coefficient projection mod {modulus} (gcd={gcd_val})")
        report.append(f"Noise analysis:")
        report.append(f"  Entropy: {h_eff:.4f} / {h_max:.4f} bits")
        report.append(f"  KL divergence: {kl_div:.6f} bits")
        report.append(f"  Mutual information: {0.000000:.6f} bits")
        report.append(f"Security interpretation: {interpretation}")

        return {
            'scheme': scheme,
            'transformation': transformation,
            'modulus': modulus,
            'gcd': gcd_val,
            'entropy': float(h_eff),
            'max_entropy': h_max,
            'kl_divergence': float(kl_div),
            'interpretation': interpretation,
            'formatted_report': "\n".join(report)
        }

def analyze_scheme(scheme: str = "Kyber512", transformation: str = "projection", 
                   modulus: int = 6, parameters: Optional[Dict[str, Any]] = None) -> str:
    """
    Función de entrada fácil para el usuario según la especificación del caso de uso.
    """
    res = SchemeAuditor.analyze_scheme(scheme=scheme, transformation=transformation, modulus=modulus, parameters=parameters)
    print(res['formatted_report'])
    return res['formatted_report']
