import numpy as np
from scipy.stats import chisquare
from typing import Dict, Any
from transformations.dsa.audit_utils import compute_mutual_information_robust
from transformations.dsa.decompose import audit_decompose_transformation
from transformations.dsa.power2round import audit_power2round_transformation
from transformations.dsa.hint import audit_hint_transformation


def audit_dsa_decompose(s1_vec: np.ndarray, r0_vec: np.ndarray, gamma2: int = 95232) -> Dict[str, Any]:
    """1. Test de Fuga vía Permutación (Información Mutua con B=256).

    2. Test de Uniformidad Marginal vía Chi-Cuadrado (Independiente).
    """
    mi_stats = compute_mutual_information_robust(
        s_vec=s1_vec,
        out_vec=r0_vec,
        num_bins=256,
        n_permutations=500,
        seed=42
    )

    counts, _ = np.histogram(r0_vec, bins=256)
    exp_counts = np.maximum(np.full(256, len(r0_vec) / 256.0), 1e-6)
    chi2_stat, chi2_p = chisquare(counts, f_exp=exp_counts)

    return {
        "experiment_id": f"DSA_Decompose_g2_{gamma2}",
        "empirical_p_value": mi_stats["empirical_p_value"],
        "chi2_p_value": float(chi2_p),
        "mi_mm_display": mi_stats["mi_mm_display"],
        "samples_per_cell": mi_stats["samples_per_cell"]
    }


def audit_dsa_power2round(s1_vec: np.ndarray, t0_vec: np.ndarray, d: int = 13) -> Dict[str, Any]:
    """Auditoría de Power2Round mapeando el p-valor de permutación a empirical_p_value

    y el de chi2 a chi2_p_value.
    """
    mi_stats = compute_mutual_information_robust(
        s_vec=s1_vec,
        out_vec=t0_vec,
        num_bins=256,
        n_permutations=500,
        seed=42
    )

    counts, _ = np.histogram(t0_vec, bins=256)
    exp_counts = np.maximum(np.full(256, len(t0_vec) / 256.0), 1e-6)
    chi2_stat, chi2_p = chisquare(counts, f_exp=exp_counts)

    return {
        "experiment_id": f"DSA_Power2Round_d_{d}",
        "empirical_p_value": mi_stats["empirical_p_value"],
        "chi2_p_value": float(chi2_p),
        "mi_mm_display": mi_stats["mi_mm_display"],
        "samples_per_cell": mi_stats["samples_per_cell"]
    }


def audit_dsa_make_hint(s1_vec: np.ndarray, h_vec: np.ndarray, gamma2: int = 95232) -> Dict[str, Any]:
    """Auditoría de MakeHint/UseHint mapeando el p-valor de permutación a empirical_p_value

    y el de chi2 a chi2_p_value.
    """
    mi_stats = compute_mutual_information_robust(
        s_vec=s1_vec,
        out_vec=h_vec,
        num_bins=256,
        n_permutations=500,
        seed=42
    )

    p1 = float(np.mean(h_vec))
    exp_counts = np.array([len(h_vec) * 0.5, len(h_vec) * 0.5])
    counts = np.array([len(h_vec) * (1 - p1), len(h_vec) * p1])
    chi2_stat, chi2_p = chisquare(counts, f_exp=exp_counts)

    return {
        "experiment_id": f"DSA_MakeHint_g2_{gamma2}",
        "empirical_p_value": mi_stats["empirical_p_value"],
        "chi2_p_value": float(chi2_p),
        "mi_mm_display": mi_stats["mi_mm_display"],
        "samples_per_cell": mi_stats["samples_per_cell"]
    }


def run_dsa_suite(num_samples: int = 500000, seed: int = 42) -> list[dict[str, Any]]:
    """Ejecuta la suite de auditoría ML-DSA / FIPS 204 (3 Experimentos Canónicos: Decompose, Power2Round, MakeHint)
    evaluando tanto ML-DSA-44 como ML-DSA-65/87 con N=500,000, B=256 y P=500 permutaciones.
    """
    from transformations.dsa.audit_utils import aggregate_sweep_p_value

    # 1. Decompose
    res_dec_44 = audit_decompose_transformation(q=8380417, gamma2=95232, eta=2, num_samples=num_samples, seed=seed, export_csv=True)
    res_dec_65 = audit_decompose_transformation(q=8380417, gamma2=261888, eta=4, num_samples=num_samples, seed=seed, export_csv=True)
    p_dec = float(aggregate_sweep_p_value([res_dec_44["empirical_p_value"], res_dec_65["empirical_p_value"]]))
    res_dec = {
        "experiment_id": "DSA_Decompose",
        "empirical_p_value": p_dec,
        "mi_mm_display": max(res_dec_44.get("mi_mm_display", 0.0), res_dec_65.get("mi_mm_display", 0.0)),
        "sub_results": [res_dec_44, res_dec_65]
    }

    # 2. Power2Round
    res_p2r_44 = audit_power2round_transformation(q=8380417, d=13, eta=2, num_samples=num_samples, seed=seed, export_csv=True)
    res_p2r_65 = audit_power2round_transformation(q=8380417, d=13, eta=4, num_samples=num_samples, seed=seed, export_csv=True)
    p_p2r = float(aggregate_sweep_p_value([res_p2r_44["empirical_p_value"], res_p2r_65["empirical_p_value"]]))
    res_p2r = {
        "experiment_id": "DSA_Power2Round",
        "empirical_p_value": p_p2r,
        "mi_mm_display": max(res_p2r_44.get("mi_mm_display", 0.0), res_p2r_65.get("mi_mm_display", 0.0)),
        "sub_results": [res_p2r_44, res_p2r_65]
    }

    # 3. MakeHint
    res_hnt_44 = audit_hint_transformation(q=8380417, gamma2=95232, eta=2, gamma1=131072, num_samples=num_samples, seed=seed, export_csv=True)
    res_hnt_65 = audit_hint_transformation(q=8380417, gamma2=261888, eta=4, gamma1=524288, num_samples=num_samples, seed=seed, export_csv=True)
    p_hnt = float(aggregate_sweep_p_value([res_hnt_44["empirical_p_value"], res_hnt_65["empirical_p_value"]]))
    res_hnt = {
        "experiment_id": "DSA_MakeHint",
        "empirical_p_value": p_hnt,
        "mi_mm_display": max(res_hnt_44.get("mi_mm_display", 0.0), res_hnt_65.get("mi_mm_display", 0.0)),
        "sub_results": [res_hnt_44, res_hnt_65]
    }

    return [res_dec, res_p2r, res_hnt]


