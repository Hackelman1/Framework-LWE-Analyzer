import os
import math
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Tuple, Dict, Any, Union
from scipy.stats import chisquare

def decompose_fips204(r: Union[int, np.ndarray], gamma2: int, q: int = 8380417) -> Tuple[Union[int, np.ndarray], Union[int, np.ndarray]]:
    """
    Algoritmo de referencia Decompose según FIPS 204 (ML-DSA / Dilithium).
    Divide r en parte alta r1 y parte baja r0 acotada en [-gamma2, gamma2].
    Cumple: r = r1 * 2 * gamma2 + r0 (mod q)
    """
    is_scalar = isinstance(r, (int, np.integer))
    r_arr = np.atleast_1d(np.array(r, dtype=np.int64)) % q

    r0 = r_arr % (2 * gamma2)
    r0 = np.where(r0 > gamma2, r0 - 2 * gamma2, r0)

    cond = ((q - 1 - (r_arr - r0)) == 0)
    r1 = np.where(cond, 0, (r_arr - r0) // (2 * gamma2))
    r0 = np.where(cond, r0 - 1, r0)

    if is_scalar:
        return int(r1[0]), int(r0[0])
    return r1, r0

def audit_decompose_transformation(q: int = 8380417, gamma2: int = 95232, eta: int = 2,
                                    num_samples: int = 500000, seed: int = 42,
                                    export_csv: bool = True) -> Dict[str, Any]:
    """
    Ejecuta el test de auditoría estadística sobre la función Decompose de ML-DSA (FIPS 204).
    Mide la uniformidad y ausencia de filtración de información mutua I(S1; r0).
    """
    np.random.seed(seed)

    # 1. Generación de Dataset Sintético
    # S1 con distribución discreta acotada en [-eta, eta]
    s1 = np.random.randint(-eta, eta + 1, size=num_samples, dtype=np.int64)
    # Y vector de enmascaramiento uniforme en Z_q
    y = np.random.randint(0, q, size=num_samples, dtype=np.int64)
    # C vector de desafío en {-1, 0, 1}
    c = np.random.choice([-1, 0, 1], size=num_samples).astype(np.int64)

    # r = (Y + C * S1) mod q
    r = (y + c * s1) % q

    # 2. Aplicación de Decompose
    r1, r0 = decompose_fips204(r, gamma2, q)

    # 3. Métricas Estadísticas sobre r0 en [-gamma2, gamma2]
    K = 2 * gamma2 + 1
    r0_idx = (r0 + gamma2).astype(np.int64)

    counts = np.bincount(r0_idx, minlength=K)
    emp_pmf = counts / float(num_samples)
    unif_pmf = np.full(K, 1.0 / K)

    # Entropía de Shannon
    nonzero_p = emp_pmf[emp_pmf > 0]
    h_r0 = float(-np.sum(nonzero_p * np.log2(nonzero_p)))
    max_h = float(np.log2(K))

    # Distancia de Variación Total (TVD)
    tvd = float(0.5 * np.sum(np.abs(emp_pmf - unif_pmf)))

    # Test de Chi-Cuadrado
    exp_counts = unif_pmf * num_samples
    exp_counts = np.maximum(exp_counts, 1e-6)
    chi2_stat, p_val = chisquare(counts, f_exp=exp_counts)

    # Información Mutua I(S1; r0) = H(r0) - H(r0 | S1) con corrección de sesgo muestral
    s1_vals = np.unique(s1)
    K_X = len(s1_vals)
    h_cond = 0.0
    for s_val in s1_vals:
        mask = (s1 == s_val)
        n_s = np.sum(mask)
        if n_s == 0:
            continue
        p_s = n_s / float(num_samples)
        r0_s = r0_idx[mask]
        counts_s = np.bincount(r0_s, minlength=K)
        p_r0_s = counts_s / float(n_s)
        nz_s = p_r0_s[p_r0_s > 0]
        h_s = -np.sum(nz_s * np.log2(nz_s))
        h_cond += p_s * h_s

    mi_raw = float(h_r0 - h_cond)

    # Corrección de sesgo muestral analítico para K bins:
    # E[H(N)] - E[H(N/K_X)] = (K - 1)*(K_X - 1) / (2 * N * ln(2))
    bias_mi = ((K - 1) * (K_X - 1)) / (2.0 * num_samples * np.log(2))
    mi_corrected = max(0.0, float(mi_raw - bias_mi))






    # 4. Información Mutua Robusta con Permutaciones
    from transformations.dsa.audit_utils import compute_mutual_information_robust
    mi_stats = compute_mutual_information_robust(
        s_vec=s1,
        out_vec=r0_idx,
        num_bins=min(256, K),
        n_permutations=500 if num_samples >= 10000 else 50,
        seed=seed
    )

    is_safe = bool((mi_corrected < 1e-3) and (p_val > 0.01))
    
    scheme_name = f"ML-DSA-44" if gamma2 == 95232 else f"ML-DSA-65/87"
    if is_safe:
        interpretation = f"Low-part r0 reveals no secret leakage (MI={mi_corrected:.6f} bits) and retains uniform distribution (p={float(p_val):.4f}) [PASS]"
    else:
        interpretation = f"WARNING: Observable leakage or non-uniformity detected in low-part r0 (MI={mi_corrected:.6f} bits, p={float(p_val):.4f}) [FAIL]"

    status_str = "PASS" if is_safe else "FAIL"
    param_str = f"gamma2={gamma2}, eta={eta}"

    result_dict = {
        'scheme': scheme_name,
        'function': 'Decompose',
        'transformation': 'Decompose',
        'parameter': param_str,
        'q': int(q),
        'gamma2': int(gamma2),
        'eta': int(eta),
        'entropy_bits': float(h_r0),
        'entropy_r0': float(h_r0),
        'max_entropy_bits': float(max_h),
        'max_entropy': float(max_h),
        'tvd': float(tvd),
        'chi2_stat': float(chi2_stat),
        'chi2_pvalue': float(p_val),
        'chi2_p_value': float(p_val),
        'empirical_p_value': mi_stats['empirical_p_value'],
        'mi_mm_display': mi_stats['mi_mm_display'],
        'mutual_info_s1': float(mi_corrected),
        'mutual_info_s2': 0.0,
        'mutual_information': float(mi_corrected),
        'status': status_str,
        'is_safe': is_safe,
        'num_samples': int(num_samples),
        'interpretation': interpretation
    }

    # 5. Exportación a CSV (results/dsa_transform_table.csv)
    if export_csv:
        root_dir = Path(__file__).resolve().parent.parent.parent
        results_dir = root_dir / "results"
        results_dir.mkdir(parents=True, exist_ok=True)
        csv_path = results_dir / "dsa_transform_table.csv"

        csv_columns = [
            'scheme', 'function', 'parameter', 'entropy_bits', 'max_entropy_bits',
            'tvd', 'chi2_pvalue', 'mutual_info_s1', 'mutual_info_s2', 'status', 'num_samples'
        ]

        row_data = {col: result_dict[col] for col in csv_columns if col in result_dict}
        df_row = pd.DataFrame([row_data])

        if csv_path.exists():
            try:
                existing_df = pd.read_csv(csv_path)
                combined_df = pd.concat([existing_df, df_row], ignore_index=True)
                combined_df.to_csv(csv_path, index=False)
            except Exception:
                df_row.to_csv(csv_path, mode='a', header=False, index=False)
        else:
            df_row.to_csv(csv_path, mode='w', header=True, index=False)

        print(f"SUCCESS: Resultado de auditoría ML-DSA guardado en '{csv_path}'")

    return result_dict

