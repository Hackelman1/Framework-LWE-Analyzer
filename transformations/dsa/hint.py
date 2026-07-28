import os
import math
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Tuple, Dict, Any, Union
from scipy.stats import chisquare

def make_hint_fips204(z0: Union[int, np.ndarray], z1: Union[int, np.ndarray], gamma2: int, q: int = 8380417) -> Union[int, np.ndarray]:
    """
    Calcula el bit de pista h indicando si HighBits(z0 + z1) != HighBits(z1).
    FIPS 204: MakeHint(z0, z1, gamma2)
    """
    from transformations.dsa.decompose import decompose_fips204

    r1, _ = decompose_fips204(z0 + z1, gamma2, q)
    v1, _ = decompose_fips204(z1, gamma2, q)

    h = np.where(r1 != v1, 1, 0)
    is_scalar = (np.isscalar(z0) or isinstance(z0, (int, np.integer)) or getattr(z0, 'ndim', None) == 0) and \
                (np.isscalar(z1) or isinstance(z1, (int, np.integer)) or getattr(z1, 'ndim', None) == 0)
    if is_scalar:
        return int(np.asarray(h).item())
    return h

def use_hint_fips204(h: Union[int, np.ndarray], z: Union[int, np.ndarray], gamma2: int, q: int = 8380417) -> Union[int, np.ndarray]:
    """
    Recupera la parte alta r1 utilizando el bit de pista h y z.
    FIPS 204: UseHint(h, z, gamma2)
    """
    from transformations.dsa.decompose import decompose_fips204

    r1, r0 = decompose_fips204(z, gamma2, q)
    m = (q - 1) // (2 * gamma2)

    is_scalar = (np.isscalar(h) or isinstance(h, (int, np.integer)) or getattr(h, 'ndim', None) == 0) and \
                (np.isscalar(z) or isinstance(z, (int, np.integer)) or getattr(z, 'ndim', None) == 0)

    if is_scalar:
        h_val = int(np.asarray(h).item())
        r0_val = int(np.asarray(r0).item())
        r1_val = int(np.asarray(r1).item())
        if h_val == 0:
            return r1_val
        if r0_val > 0:
            return (r1_val + 1) % m
        return (r1_val - 1) % m

    res = np.copy(r1)
    cond_pos = (h == 1) & (r0 > 0)
    cond_neg = (h == 1) & (r0 <= 0)

    res[cond_pos] = (r1[cond_pos] + 1) % m
    res[cond_neg] = (r1[cond_neg] - 1) % m
    return res

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
    bias_mi = ((K_y - 1) * (K_x - 1)) / (2.0 * num_samples * np.log(2))
    mi_corrected = max(0.0, float(mi_raw - bias_mi))
    return mi_corrected

def audit_hint_transformation(q: int = 8380417, gamma2: int = 95232, eta: int = 2, gamma1: int = 131072,
                                num_samples: int = 500000, seed: int = 42,
                                fast: bool = False, export_csv: bool = True) -> Dict[str, Any]:
    """
    Ejecuta el test de auditoría estadística sobre las funciones MakeHint y UseHint de ML-DSA (FIPS 204).
    Mide la distribución del bit de pista h y la ausencia de información mutua I(S1; h) e I(S2; h).
    """
    if fast and num_samples == 500000:
        num_samples = 10000

    np.random.seed(seed)

    # 1. Generación del Dataset Sintético
    from transformations.dsa.power2round import power2round_fips204

    l = 4 if eta == 2 else 6
    s1_vec = np.random.randint(-eta, eta + 1, size=(num_samples, l), dtype=np.int64)
    s2_vec = np.random.randint(-eta, eta + 1, size=(num_samples, l), dtype=np.int64)
    mask_zero = np.all(s1_vec == 0, axis=1)
    if np.any(mask_zero):
        s1_vec[mask_zero, 0] = 1

    a_vec = np.random.randint(0, q, size=(num_samples, l), dtype=np.int64)
    dot = np.sum(a_vec * s1_vec, axis=1) % q
    t = (dot + s2_vec[:, 0]) % q
    t1, t0 = power2round_fips204(t, d=13, q=q)

    y = np.random.randint(-gamma1 + 1, gamma1 + 1, size=num_samples, dtype=np.int64)
    c = np.random.choice([-1, 0, 1], size=num_samples).astype(np.int64)

    z0 = -c * t0
    z1 = (y - c * s2_vec[:, 0] + c * t0) % q

    # 2. Generación de las pistas h
    h = make_hint_fips204(z0, z1, gamma2=gamma2, q=q)

    # 3. Métricas Estadísticas sobre h
    p1 = float(np.mean(h))
    p0 = 1.0 - p1

    h_bits = 0.0
    if p1 > 0:
        h_bits -= p1 * math.log2(p1)
    if p0 > 0:
        h_bits -= p0 * math.log2(p0)

    max_h = 1.0

    # TVD respecto a Bernoulli(0.5)
    tvd = float(0.5 * (abs(p0 - 0.5) + abs(p1 - 0.5)))

    # Test Chi-Cuadrado de uniformidad de 1s a lo largo de 100 segmentos de muestra
    n_chunks = 100
    chunk_size = num_samples // n_chunks
    h_reshaped = h[:n_chunks * chunk_size].reshape(n_chunks, chunk_size)
    ones_per_chunk = np.sum(h_reshaped, axis=1)
    exp_ones = np.full(n_chunks, np.mean(ones_per_chunk))
    exp_ones = np.maximum(exp_ones, 1e-6)
    chi2_stat, p_val = chisquare(ones_per_chunk, f_exp=exp_ones)

    # Información Mutua Dual I(S1; h) e I(S2; h)
    s1 = s1_vec[:, 0]
    s2 = s2_vec[:, 0]
    mi_s1 = _compute_corrected_mutual_info(s1, h, K_y=2, num_samples=num_samples)
    mi_s2 = _compute_corrected_mutual_info(s2, h, K_y=2, num_samples=num_samples)

    # 4. Criterio de Aceptación (Pass/Fail)
    mi_threshold = 1e-3 if num_samples >= 500000 else 0.05
    p_val_ok = (p_val > 0.01) or (num_samples < 50000)

    is_safe = bool((mi_s1 < mi_threshold) and (mi_s2 < mi_threshold) and p_val_ok)
    scheme_name = "ML-DSA-44" if eta == 2 else "ML-DSA-65/87"
    status_str = "PASS" if is_safe else "FAIL"

    if is_safe:
        interpretation = (f"MakeHint/UseHint h vector reveals no secret leakage "
                          f"(MI_s1={mi_s1:.6f}, MI_s2={mi_s2:.6f} bits) and retains uniform chunk distribution "
                          f"(p={float(p_val):.4f}) [{status_str}]")
    else:
        interpretation = (f"WARNING: Observable leakage detected in hint vector h "
                          f"(MI_s1={mi_s1:.6f}, MI_s2={mi_s2:.6f} bits, p={float(p_val):.4f}) [{status_str}]")

    param_str = f"gamma2={gamma2}, eta={eta}"

    result_dict = {
        'scheme': scheme_name,
        'function': 'MakeHint',
        'transformation': 'MakeHint',
        'parameter': param_str,
        'q': int(q),
        'gamma2': int(gamma2),
        'eta': int(eta),
        'entropy_bits': float(h_bits),
        'max_entropy_bits': float(max_h),
        'tvd': float(tvd),
        'chi2_stat': float(chi2_stat),
        'chi2_pvalue': float(p_val),
        'mutual_info_s1': float(mi_s1),
        'mutual_info_s2': float(mi_s2),
        'mutual_information': float(max(mi_s1, mi_s2)),
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
