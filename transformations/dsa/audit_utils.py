import numpy as np
from scipy.stats import false_discovery_control


def aggregate_sweep_p_value(p_values: list[float] | np.ndarray) -> float:
    """Consolida un barrido paramétrico de K subconfiguraciones en un p-valor
    representante válido mediante la corrección interna de Bonferroni.
    Garantiza que P(p_tilde <= t) <= t bajo H0.
    """
    if not p_values:
        raise ValueError(
            "La lista de p-valores del barrido no puede estar vacía."
        )

    p_arr = np.array(p_values, dtype=float)
    K = len(p_arr)
    p_min = float(np.min(p_arr))

    # Bonferroni interno: K * p_min acotado a 1.0
    return min(K * p_min, 1.0)


def choose_num_bins(
    K_X: int, native_K_Y: int, N: int, target_density: float = 50.0
) -> int | None:
    """Calcula el número dinámico de bines para garantizar una densidad mínima
    objetivo de muestras por celda en el espacio conjunto (target_density >= 50).
    Si la densidad nativa ya es >= target_density, devuelve None (sin agrupamiento).
    Valida y señala explícitamente si la densidad objetivo es inalcanzable solo agrupando Y.
    """
    total_cells = K_X * native_K_Y
    if total_cells == 0:
        return None
    native_density = N / total_cells
    if native_density >= target_density:
        return None  # Resolución nativa completa sin binning

    max_bins = max(2, int(N / (target_density * K_X)))
    chosen_bins = min(native_K_Y, max_bins)
    achieved_density = N / (K_X * chosen_bins)

    if achieved_density < target_density:
        raise ValueError(
            f"Densidad objetivo inalcanzable solo agrupando Y: K_X={K_X} ya excede "
            f"el límite para N={N} a target_density={target_density} (densidad alcanzada={achieved_density:.2f} < {target_density}). "
            f"Aumenta el número de muestras N o ajusta los parámetros de estado del experimento."
        )

    return chosen_bins


def compute_mutual_information_robust(
    s_vec: np.ndarray,
    out_vec: np.ndarray,
    num_bins: int | None = 256,
    n_permutations: int = 500,
    seed: int = 42,
) -> dict:
    """Calcula Información Mutua con B bines adaptativos o resolución nativa (num_bins=None),
    corrección Miller-Madow (bits), test de permutación add-one (Phipson & Smyth, 2010)
    y distribución nula con signo.
    """
    rng = np.random.default_rng(seed)
    s_vec = np.asarray(s_vec).flatten()
    out_vec = np.asarray(out_vec).flatten()

    # Validar que las longitudes sean strictly idénticas (evita auto-relleno espurio)
    if len(s_vec) != len(out_vec):
        raise ValueError(
            f"s_vec (N={len(s_vec)}) y out_vec (N={len(out_vec)}) deben tener exactamente la misma longitud — "
            f"verifica el protocolo de muestreo del experimento que llama a esta función."
        )
    N = len(s_vec)

    # 1. Agrupamiento adaptativo seguro ante NoneType
    if num_bins is not None and len(np.unique(out_vec)) > num_bins:
        min_val, max_val = np.min(out_vec), np.max(out_vec)
        bins = np.linspace(min_val, max_val, num_bins + 1)
        out_binned = np.digitize(out_vec, bins) - 1
        out_binned = np.clip(out_binned, 0, num_bins - 1)
    else:
        out_binned = out_vec

    # 2. Histograma conjunto y probabilidades
    s_states, s_counts = np.unique(s_vec, return_counts=True)
    out_states, out_counts = np.unique(out_binned, return_counts=True)

    K_X = len(s_states)
    K_Y = len(out_states)
    K_XY = K_X * K_Y

    bins_s = np.append(s_states, s_states[-1] + 1) - 0.5
    bins_out = np.append(out_states, out_states[-1] + 1) - 0.5

    joint_hist, _, _ = np.histogram2d(s_vec, out_binned, bins=[bins_s, bins_out])

    p_xy = joint_hist / N
    p_x = s_counts / N
    p_y = out_counts / N

    # MI Plug-in (bits)
    mask = p_xy > 0
    mi_plugin = np.sum(
        p_xy[mask] * np.log2(p_xy[mask] / (p_x[:, None] * p_y[None, :])[mask])
    )

    # Corrección Miller-Madow exacta en BITS (dividida por ln 2)
    bias_mm_bits = (K_XY - K_X - K_Y + 1) / (2 * N * np.log(2))
    mi_mm_raw = mi_plugin - bias_mm_bits

    # 3. Permutaciones con signo (sin recorte prematuro por Jensen)
    mi_null_raw_list = []
    for _ in range(n_permutations):
        s_shuffled = rng.permutation(s_vec)
        joint_null, _, _ = np.histogram2d(
            s_shuffled, out_binned, bins=[bins_s, bins_out]
        )
        p_xy_null = joint_null / N
        mask_null = p_xy_null > 0
        mi_null_plugin = np.sum(
            p_xy_null[mask_null]
            * np.log2(
                p_xy_null[mask_null] / (p_x[:, None] * p_y[None, :])[mask_null]
            )
        )
        mi_null_raw_list.append(mi_null_plugin - bias_mm_bits)

    mi_null_arr = np.array(mi_null_raw_list)

    # 4. p-valor add-one (Phipson & Smyth, 2010)
    count_exceed = np.sum(mi_null_arr >= mi_mm_raw)
    empirical_p_value = float((1 + count_exceed) / (n_permutations + 1))
    percentile_vs_null = float(np.mean(mi_null_arr <= mi_mm_raw) * 100.0)

    return {
        "mi_mm_raw": float(mi_mm_raw),
        "mi_mm_display": float(max(0.0, mi_mm_raw)),
        "mi_null_mean": float(np.mean(mi_null_arr)),
        "mi_null_std": float(np.std(mi_null_arr)),
        "empirical_p_value": empirical_p_value,
        "percentile_vs_null": percentile_vs_null,
        "k_xy_cells": int(K_XY),
        "samples_per_cell": float(N / K_XY) if K_XY > 0 else 0.0,
        "num_bins_used": int(K_Y),
        "n_permutations": n_permutations,
        "seed": seed,
    }


def apply_fdr_control(
    audit_results: list[dict],
    alpha: float = 0.05,
    family_scope: str = "leakage_global",
    p_value_key: str = "empirical_p_value",
) -> list[dict]:
    """Aplica el ajuste Benjamini-Hochberg (FDR) sobre la familia especificada de hipótesis."""
    if not audit_results:
        return []

    raw_p_values = []
    for i, res in enumerate(audit_results):
        if p_value_key not in res:
            raise KeyError(
                f"Resultado en índice {i} ({res.get('experiment_id', '?')}) no contiene '{p_value_key}'"
            )
        raw_p_values.append(res[p_value_key])

    adjusted_q_values = false_discovery_control(raw_p_values)

    for i, res in enumerate(audit_results):
        q_val = float(adjusted_q_values[i])
        res["fdr_q_value"] = q_val
        res["family_scope"] = family_scope
        res["is_safe"] = q_val > alpha
        res["status"] = "PASS" if res["is_safe"] else "WARNING"

    return audit_results
