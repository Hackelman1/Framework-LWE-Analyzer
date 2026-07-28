**Español** | [English](README_ENG.md)

# Framework de Evaluación y Auditoría Estadística de LWE / ML-KEM / ML-DSA (Release v2.0)
[![DOI](https://zenodo.org/badge/1313642539.svg)](https://doi.org/10.5281/zenodo.21622274)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Release v2.0.0](https://img.shields.io/badge/release-v2.0.0-green.svg)](https://github.com/Hackelman1/Framework-LWE-Analyzer)


Release oficial v2.0.0 del framework teórico y experimental para el análisis de uniformización estadística de ruido en Learning With Errors (LWE), Ring-LWE, Module-LWE y auditoría estadística integral de transformaciones reales de implementación en **ML-KEM (FIPS 203)** y **ML-DSA (FIPS 204)**.

---

## 1. Alcance y Descubrimientos Clave

1. **Teorema de Uniformización Modular en LWE**: Cota contractiva de distancia estadística mediante convolución circular:
   $$\delta(P(e_{\text{effective}}), U(\mathbb{Z}_m)) \le \delta(P(k q \bmod m), U(\mathbb{Z}_m))$$
2. **Criterios Algebraicos**: La uniformización completa del ruido efectivo exige $\gcd(q, m) = 1$ y dispersión suficiente del término de envolvente modular $k = \lfloor (A s + e)/q \rfloor \bmod m$.
3. **Prueba Sin Ruido ($e=0$)**: Demostración matemática y empírica de que la uniformización es producida intrínsecamente por el término de envolvente $k$, independientemente de la magnitud de $e$.
4. **Auditoría de Transformaciones Reales en ML-KEM / Kyber (FIPS 203)**:
   - Compresión ($\text{Compress}_d$) y Descompresión ($\text{Decompress}_d$).
   - Ruido por error de redondeo *round-trip*.
   - Reducción modular real e imprecisa (`exact` vs `biased`).
   - Empaquetamiento de bits/bytes (`coefficient_pack/unpack`).
   - **Conclusión de Auditoría**: Las transformaciones de implementación preservan la independencia estadística del ruido y no filtran información mutua sobre el secreto ($I(S; \text{Salida}) \approx 0.0000$ bits).
5. **Auditoría de Funciones de Redondeo, Descomposición y Pistas en ML-DSA / Dilithium (FIPS 204)**:
   - **`Decompose`**: Verificación empírica de que el residuo de parte baja $r_0 \in [-\gamma_2, \gamma_2]$ generado durante la firma no filtra información sobre la clave secreta $S_1$ ($I(S_1; r_0) = 0.000000$ bits) para todos los niveles de seguridad.
   - **`Power2Round`**: Demostración de que el residuo truncado de la clave pública $t_0 \in [-4095, 4096]$ ($d=13$) actúa como ruido discreto uniforme de $13$ bits, sin revelar información mutua apreciable respecto a $S_1$ ni $S_2$ ($I(S; t_0) \le 0.0031$ bits) y superando la prueba de ajuste de Chi-Cuadrado ($\chi^2 p\text{-valor} > 0.57$).
   - **`MakeHint` / `UseHint`**: Verificación de que los vectores binarios de pistas $h \in \{0, 1\}^K$ transmitidos públicamente en las firmas digitales no filtran información mutua sobre las claves secretas ($I(S_1; h) = I(S_2; h) = 0.000000$ bits) y presentan una distribución espacial homogénea ($\chi^2 p\text{-valor} > 0.69$).

---

## 2. Estructura del Repositorio

```
Framework-LWE-Analyzer/
├── src/                         # Módulos centrales de generación, proyección y ataques
├── schemes/                     # Definición de parámetros e instancias (Module-LWE / Kyber)
│   └── module_lwe/              # Kyber512, Kyber768, Kyber1024 y KyberTransformAuditor
├── transformations/             # Operaciones reales Kyber y ML-DSA (compresión, redondeo, hints)
│   └── dsa/                     # Módulos de auditoría FIPS 204 (decompose, power2round, hint)
├── tests/                       # Suite de pruebas unitarias automatizadas (23 tests)
├── docs/                        # Documentación teórica y metodológica
├── paper/                       # Manuscrito principal en Markdown (main.md)
├── results/                     # Datasets CSV, gráficos PNG y reportes consolidados
├── config/                      # Configuración centralizada YAML (default.yaml)
├── scripts/                     # Scripts auxiliares de reconstrucción y limpieza
│   ├── clean_results.py
│   └── rebuild_all.py
├── run_all_experiments.py       # Punto de entrada único para los experimentos
├── auditor.py                   # Interfaz principal de auditoría estadística
├── README.md
├── README_ENG.md
├── CHANGELOG.md
├── requirements.txt
├── LICENSE
└── CITATION.cff
```

---

## 3. Instalación

```bash
git clone https://github.com/Hackelman1/Framework-LWE-Analyzer.git
cd Framework-LWE-Analyzer
pip install -r requirements.txt
```

---

## 4. Ejecución y Reproducibilidad

### Reproducción Automatizada Completa Desde Cero
Para limpiar resultados previos, ejecutar la suite de pruebas unitarias, correr todos los experimentos y regenerar los CSVs, gráficos e informes:

```bash
python scripts/rebuild_all.py
```

### Invocación de la Auditoría Estadística Directa
Para auditar una transformación concreta desde la interfaz de auditoría:

```python
from auditor import analyze_scheme

# Auditoría de compresión d=10 en Kyber512
analyze_scheme(scheme="Kyber512", transformation="compression", parameters={"d": 10})
```

---

## 5. Artefactos Generados (`results/`)

- `final_table.csv`: Dataset unificado de experimentos LWE y proyecciones $Z_q \to Z_m$.
- `kyber_transform_table.csv`: Dataset de auditoría de transformaciones reales en Kyber512/768/1024.
- `dsa_transform_table.csv`: Dataset unificado de auditoría para las transformaciones en ML-DSA (FIPS 204).
- `summary_report.md`: Reporte ejecutivo consolidado.
- `final_validation_report.md`: Reporte de validación técnica.
- `*.png`: Gráficos de robustez, mapas de uniformización y sesgos de compresión/redondeo.

### Resultados de Auditoría ML-DSA (FIPS 204) — Muestra $N = 500,000$

| Esquema | Transformación | Parámetros | Entropía $H$ (bits) | Max $H$ | $\chi^2$ $p$-valor | $I(S_1; \text{out})$ | $I(S_2; \text{out})$ | Estado |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **ML-DSA-44** | `Decompose` | $\gamma_2=95232, \eta=2$ | $17.2347$ | $17.5392$ | $0.4364$ | $0.000000$ | $0.000000$ | **PASS** |
| **ML-DSA-65/87** | `Decompose` | $\gamma_2=261888, \eta=4$ | $18.1350$ | $18.9986$ | $0.1689$ | $0.000000$ | $0.000000$ | **PASS** |
| **ML-DSA-44** | `Power2Round` | $d=13, \eta=2$ | $12.9884$ | $13.0000$ | $0.9207$ | $0.000519$ | $0.001273$ | **PASS** |
| **ML-DSA-65/87** | `Power2Round` | $d=13, \eta=4$ | $12.9882$ | $13.0000$ | $0.5779$ | $0.002707$ | $0.003116$ | **PASS** |
| **ML-DSA-44** | `MakeHint` | $\gamma_2=95232, \eta=2$ | $0.0833$ | $1.0000$ | $0.8672$ | $0.000000$ | $0.000000$ | **PASS** |
| **ML-DSA-65/87** | `MakeHint` | $\gamma_2=261888, \eta=4$ | $0.0258$ | $1.0000$ | $0.6950$ | $0.000000$ | $0.000000$ | **PASS** |

---

## 6. Lo Que Demuestra y NO Demuestra Este Framework

- **SÍ Demuestra**:
  - Que las proyecciones modulares con $\gcd(q, m) = 1$ destruyen la estructura estadística observada del ruido en LWE, ML-KEM y ML-DSA.
  - Que las transformaciones reales de compresión, redondeo, descomposición y generación de pistas en Kyber (FIPS 203) y ML-DSA (FIPS 204) conservan una alta uniformidad y no aportan ventaja estadística al atacante.
- **NO Demuestra**:
  - Una ruptura de la seguridad criptográfica de ML-KEM / Kyber (FIPS 203) o ML-DSA / Dilithium (FIPS 204).
  - Vulnerabilidades de canal lateral físico (SPA/DPA) fuera del modelo estadístico de datos.

---

## 7. Cita

```bibtex
@software{Hackelman_LWE_MLKEM_MLDSA_Audit_2026,
  author = {Hackelman},
  title = {Modular Projection Effects and Implementation Audit in LWE, ML-KEM, and ML-DSA},
  year = {2026},
  version = {2.0.0},
  url = {https://github.com/Hackelman1/Framework-LWE-Analyzer}
}
```

---

## 8. Licencia

Distribuido bajo la Licencia [MIT](LICENSE).
