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


def run_dsa_suite() -> list[dict[str, Any]]:
    """Ejecuta la suite de auditoría ML-DSA / FIPS 204 (3 Experimentos: Decompose, Power2Round, MakeHint)."""
    res_dec = audit_decompose_transformation(gamma2=95232, eta=2, num_samples=10000, seed=42, export_csv=False)
    res_dec["experiment_id"] = "DSA_Decompose_g2_95232"

    res_p2r = audit_power2round_transformation(d=13, eta=2, num_samples=10000, seed=42, export_csv=False)
    res_p2r["experiment_id"] = "DSA_Power2Round_d_13"

    res_hnt = audit_hint_transformation(gamma2=95232, eta=2, num_samples=10000, seed=42, export_csv=False)
    res_hnt["experiment_id"] = "DSA_MakeHint_g2_95232"

    return [res_dec, res_p2r, res_hnt]

