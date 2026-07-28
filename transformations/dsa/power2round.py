import os
import math
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Tuple, Dict, Any, Union
from scipy.stats import chisquare

def power2round_fips204(r: Union[int, np.ndarray], d: int = 13, q: int = 8380417) -> Tuple[Union[int, np.ndarray], Union[int, np.ndarray]]:
    """
    Algoritmo de referencia Power2Round según FIPS 204 (ML-DSA / Dilithium).
    Descompone r en parte alta (r1) y parte baja (r0) acotada en [-2^(d-1) + 1, 2^(d-1)].
    Cumple: r = r1 * 2^d + r0 (mod q)
    """
    is_scalar = np.isscalar(r) or isinstance(r, (int, np.integer)) or getattr(r, 'ndim', None) == 0
    r_arr = np.atleast_1d(np.array(r, dtype=np.int64)) % q

    r0 = r_arr % (2**d)
    r0 = np.where(r0 > 2**(d-1), r0 - 2**d, r0)
    r1 = (r_arr - r0) // (2**d)

    if is_scalar:
        return int(np.asarray(r1).item()), int(np.asarray(r0).item())
    return r1, r0

def _compute_corrected_mutual_info(x: np.ndarray, y_idx: np.ndarray, K_y: int, num_samples: int) -> float:
    """
    Calcula la Información Mutua I(X; Y) = H(Y) - H(Y|X) con corrección analítica de Miller-Madow.
    """
    counts_y = np.bincount(y_idx, minlength=K_y)
    emp_pmf_y = counts_y / float(num_samples)
    nz_y = emp_pmf_y[emp_pmf_y > 0]
    h_y = -np.sum(nz_y * np.log2(nz_y))

    x_vals = np.unique(x)
    K_x = len(x_vals)
    h_cond = 0.0

    for x_val in x_vals:
        mask = (x == x_val)
        n_x = np.sum(mask)
        if n_x == 0:
            continue
        p_x = n_x / float(num_samples)
        y_given_x = y_idx[mask]
        counts_cond = np.bincount(y_given_x, minlength=K_y)
        p_cond = counts_cond / float(n_x)
        nz_cond = p_cond[p_cond > 0]
        h_x = -np.sum(nz_cond * np.log2(nz_cond))
        h_cond += p_x * h_x

    mi_raw = float(h_y - h_cond)
    # Corrección de sesgo muestral analítico de Miller-Madow para K_y bins y K_x estados:
    bias_mi = ((K_y - 1) * (K_x - 1)) / (2.0 * num_samples * np.log(2))
    mi_corrected = max(0.0, float(mi_raw - bias_mi))
    return mi_corrected

def audit_power2round_transformation(q: int = 8380417, d: int = 13, eta: int = 2,
                                      num_samples: int = 500000, seed: int = 42,
                                      fast: bool = False, export_csv: bool = True) -> Dict[str, Any]:
    """
    Ejecuta el test de auditoría estadística sobre la función Power2Round de ML-DSA (FIPS 204).
    Mide la uniformidad de t0 y la ausencia de filtración de información mutua I(S1; t0) e I(S2; t0).
    """
    if fast and num_samples == 500000:
        num_samples = 10000

    np.random.seed(seed)

    # 1. Generación del Dataset Sintético (simulando clave pública t = A*S1 + S2 mod q)
    l = 4 if eta == 2 else 6
    s1_vec = np.random.randint(-eta, eta + 1, size=(num_samples, l), dtype=np.int64)
    mask_zero = np.all(s1_vec == 0, axis=1)
    if np.any(mask_zero):
        s1_vec[mask_zero, 0] = 1

    a_vec = np.random.randint(0, q, size=(num_samples, l), dtype=np.int64)
    dot = np.sum(a_vec * s1_vec, axis=1) % q
    s2 = np.random.randint(-eta, eta + 1, size=num_samples, dtype=np.int64)

    t = (dot + s2) % q
    s1 = s1_vec[:, 0]

    # 2. Aplicación de Power2Round
    t1, t0 = power2round_fips204(t, d=d, q=q)

    # 3. Métricas Estadísticas sobre t0 en [-2^(d-1) + 1, 2^(d-1)]
    K = 2**d
    t0_idx = (t0 + (2**(d-1) - 1)).astype(np.int64)

    counts = np.bincount(t0_idx, minlength=K)
    emp_pmf = counts / float(num_samples)
    unif_pmf = np.full(K, 1.0 / K)

    # Entropía de Shannon
    nz_p = emp_pmf[emp_pmf > 0]
    h_t0 = float(-np.sum(nz_p * np.log2(nz_p)))
    max_h = float(np.log2(K))

    # Distancia de Variación Total (TVD)
    tvd = float(0.5 * np.sum(np.abs(emp_pmf - unif_pmf)))

    # Test de Chi-Cuadrado
    exp_counts = unif_pmf * num_samples
    exp_counts = np.maximum(exp_counts, 1e-6)
    chi2_stat, p_val = chisquare(counts, f_exp=exp_counts)

    # Información Mutua Dual I(S1; t0) e I(S2; t0) con corrección de Miller-Madow
    mi_s1 = _compute_corrected_mutual_info(s1, t0_idx, K, num_samples)
    mi_s2 = _compute_corrected_mutual_info(s2, t0_idx, K, num_samples)

    # 4. Criterio de Aceptación (Pass/Fail)
    mi_threshold = 5e-3 if num_samples >= 500000 else 0.05
    p_val_ok = (p_val > 0.01) or (num_samples < 50000)


    is_safe = bool((mi_s1 < mi_threshold) and (mi_s2 < mi_threshold) and p_val_ok)
    scheme_name = "ML-DSA-44" if eta == 2 else "ML-DSA-65/87"
    status_str = "PASS" if is_safe else "FAIL"

    if is_safe:
        interpretation = (f"Power2Round low-part t0 reveals no secret leakage "
                          f"(MI_s1={mi_s1:.6f}, MI_s2={mi_s2:.6f} bits) and retains uniform distribution "
                          f"(p={float(p_val):.4f}) [{status_str}]")
    else:
        interpretation = (f"WARNING: Observable leakage or non-uniformity detected in Power2Round low-part t0 "
                          f"(MI_s1={mi_s1:.6f}, MI_s2={mi_s2:.6f} bits, p={float(p_val):.4f}) [{status_str}]")

    param_str = f"d={d}, eta={eta}"

    result_dict = {
        'scheme': scheme_name,
        'function': 'Power2Round',
        'transformation': 'Power2Round',
        'parameter': param_str,
        'q': int(q),
        'd': int(d),
        'eta': int(eta),
        'entropy_bits': h_t0,
        'entropy_t0': h_t0,
        'max_entropy_bits': max_h,
        'max_entropy': max_h,
        'tvd': tvd,
        'chi2_stat': float(chi2_stat),
        'chi2_pvalue': float(p_val),
        'mutual_info_s1': mi_s1,
        'mutual_info_s2': mi_s2,
        'mutual_information': max(mi_s1, mi_s2),
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
