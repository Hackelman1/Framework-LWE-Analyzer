# Referencia de API y Esquema de Datos (v2.0.0)

**Proyecto:** `pqc-statistical-auditor`  
**Autor:** Ricardo Peinador  
**Versión:** 2.0.0  

---

## 1. Módulo de Utilidades Estadísticas (`transformations/dsa/audit_utils.py`)

### `compute_mutual_information_robust(s_vec, out_vec, num_bins=256, n_permutations=500, seed=42) -> dict`
Calcula la Información Mutua robusta aplicando:
- Discretización por binios fijos ($B = 256$) para garantizar $N \gg K_{XY}$.
- Corrección analítica de sesgo de Miller-Madow en **bits** con logaritmo natural:
  $$\text{Bias}_{\text{MM}} = \frac{K_{XY} - K_X - K_Y + 1}{2 N \ln 2}$$
- Test de permutaciones ($P = 500$, `seed=42`) manteniendo la distribución nula con signo.
- $p$-valor empírico con suavizado Add-One de Phipson & Smyth (2010):
  $$p = \frac{1 + \sum_{i=1}^P \mathbb{I}\left(I_{\text{null\_raw}}^{(i)} \ge I_{\text{MM\_raw}}\right)}{P + 1}$$

### `aggregate_sweep_p_value(p_values: list[float] | np.ndarray) -> float`
Consolida un barrido paramétrico de $K$ subconfiguraciones en un único $p$-valor representante válido mediante la corrección conservadora interna de Bonferroni:
$$\tilde{p}_m = \min(K_m \cdot p_{\min}, 1.0)$$

### `apply_fdr_control(audit_results: list[dict], alpha=0.05, family_scope="leakage_global", p_value_key="empirical_p_value") -> list[dict]`
Aplica la corrección de Benjamini-Hochberg (FDR) mediante `scipy.stats.false_discovery_control` sobre la familia global de hipótesis de fuga ($M = 23$).

---

## 2. Esquema Unificado de Diccionarios de Resultados

Todos los experimentos (suites `lwe`, `kem`, `dsa`) retornan diccionarios estandarizados que contienen:

| Clave | Tipo | Descripción |
| :--- | :--- | :--- |
| `experiment_id` | `str` | Identificador único del experimento (ej. `Exp_A`, `DSA_Decompose_g2_95232`). |
| `suite` | `str` | Pertenece a `"lwe"`, `"kem"` o `"dsa"`. |
| `empirical_p_value` | `float` | $p$-valor empírico obtenido por el test de permutaciones de fuga de información. |
| `chi2_p_value` | `float` | $p$-valor de la prueba $\chi^2$ de uniformidad marginal (no entra al ajuste FDR). |
| `fdr_q_value` | `float` | $q$-valor ajustado mediante Benjamini-Hochberg sobre el pool global $M = 23$. |
| `family_scope` | `str` | Ámbito de familia de hipótesis (`"leakage_global"`). |
| `status` | `str` | Resultado de la auditoría: `"PASS"` si $q > 0.05$ o `"WARNING"` en caso contrario. |
| `is_safe` | `bool` | Booleano indicando cumplimiento del criterio de seguridad ($q > 0.05$). |
