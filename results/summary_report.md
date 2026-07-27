# Reporte de Resultados Experimentales: Framework LWE / ML-KEM (Versión 1.0 Release Final)

## Resumen Ejecutivo

Este informe consolida la totalidad de las evidencias empíricas (Experimentos A a W) del framework de proyección LWE y auditoría de transformaciones reales en ML-KEM / Kyber.

---

## 1. Experimentos LWE / Module-LWE (Proyecciones Modulares)

| Dimensión n | I(k_m ; s_m) [Miller-Madow] (bits) | KL(e_eff || Uniforme) (bits) |
|:-----------:|:----------------------------------:|:----------------------------:|
|  1 | 0.000000 | 0.001360 |
|  2 | 0.000000 | 0.003159 |
|  4 | 0.000000 | 0.001809 |
|  8 | 0.000000 | 0.002943 |
| 16 | 0.000000 | 0.004642 |
| 32 | 0.000000 | 0.004479 |

---

## 2. Auditoría de Transformaciones Reales ML-KEM (Fase 11)

### Compresión Kyber512

| Nivel d | Entropía Salida (bits) | Max Entropía | KL Divergence (bits) | Distancia Estadística | I(s; Compreso) |
|:-------:|:---------------------:|:------------:|:--------------------:|:---------------------:|:--------------:|
| 10 | 8.4911 | 10.0 | 1.508923 | 0.617188 | 2.044994 |
| 11 | 8.7348 | 11.0 | 2.265184 | 0.781738 | 2.206185 |
|  4 | 3.9800 | 4.0 | 0.019997 | 0.070312 | 0.166243 |
|  5 | 4.9588 | 5.0 | 0.041248 | 0.089844 | 0.297203 |

### Reducción Modular Reales vs Biased

- Exacta: KL=2.844880 bits, Chi2 p-val=0.0000e+00
- Sesgada: KL=2.844880 bits, Chi2 p-val=0.0000e+00

---

## 3. Archivos y Artefactos Exportados

- Dataset Proyecciones LWE: `results/final_table.csv`
- Dataset Transformaciones Kyber: `results/kyber_transform_table.csv`
- Gráficos: `exp_l_secret_robustness.png`, `exp_m_noise_robustness.png`, `exp_r_kyber_map.png`, `exp_t_compression_bias.png`, `exp_u_rounding_noise.png`