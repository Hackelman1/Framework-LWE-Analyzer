# Framework de Evaluación y Auditoría Estadística de LWE / ML-KEM (Release v1.0)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Release v1.0](https://img.shields.io/badge/release-v1.0.0-green.svg)](https://github.com/framework-lwe/modular-projection)

Release oficial v1.0.0 del framework teórico y experimental para el análisis de uniformización estadística de ruido en Learning With Errors (LWE), Ring-LWE, Module-LWE y auditoría de transformaciones reales de implementación en **ML-KEM / Kyber (FIPS 203)**.

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

---

## 2. Estructura del Repositorio

```
Framework-LWE-Analyzer/
├── src/                         # Módulos centrales de generación, proyección y ataques
├── schemes/                     # Definición de parámetros e instancias (Module-LWE / Kyber)
│   └── module_lwe/              # Kyber512, Kyber768, Kyber1024 y KyberTransformAuditor
├── transformations/             # Operaciones reales Kyber (compresión, redondeo, packing)
├── tests/                       # Suite de pruebas unitarias automatizadas
├── docs/                        # Documentación teórica y metodológica
├── paper/                       # Manuscrito principal en Markdown (main.md)
├── results/                     # Datasets CSV, gráficos PNG y reportes consolidados
├── config/                      # Configuración centralizada YAML (default.yaml)
├── scripts/                     # Scripts auxiliares de reconstrucción y limpieza
│   ├── clean_results.py
│   └── rebuild_all.py
├── run_all_experiments.py       # Punto de entrada único para los 23 experimentos (A a W)
├── auditor.py                   # Interfaz principal de auditoría estadística
├── README.md
├── CHANGELOG.md
├── requirements.txt
├── LICENSE
└── CITATION.cff
```

---

## 3. Instalación

```bash
git clone https://github.com/framework-lwe/modular-projection.git
cd modular-projection
pip install -r requirements.txt
```

---

## 4. Ejecución y Reproducibilidad

### Reproducción Automatizada Completa Desde Cero
Para limpiar resultados previos, ejecutar la suite de pruebas unitarias, correr los 23 experimentos (A a W) y regenerar todos los CSVs, gráficos e informes:

```bash
python scripts/rebuild_all.py
```

### Invocación de la Auditoría Estadística Directa
Para auditar una transformación concreta de Kyber desde la interfaz de auditoría:

```python
from auditor import analyze_scheme

# Auditoría de compresión d=10 en Kyber512
analyze_scheme(scheme="Kyber512", transformation="compression", parameters={"d": 10})
```

---

## 5. Artefactos Generados (`results/`)

- `final_table.csv`: Dataset unificado de experimentos LWE y proyecciones $Z_q \to Z_m$.
- `kyber_transform_table.csv`: Dataset de auditoría de transformaciones reales en Kyber512/768/1024.
- `summary_report.md`: Reporte ejecutivo consolidado con métricas de los experimentos A a W.
- `final_validation_report.md`: Reporte de validación técnica.
- `*.png`: Gráficos de robustez, mapas de uniformización y sesgos de compresión/redondeo.

---

## 6. Lo Que Demuestra y NO Demuestra Este Framework

- **SÍ Demuestra**:
  - Que las proyecciones modulares con $\gcd(q, m) = 1$ destruyen la estructura estadística observada del ruido en LWE y ML-KEM.
  - Que las transformaciones reales de compresión, redondeo y serialización en Kyber conservan una alta uniformidad y no aportan ventaja estadística al atacante.
- **NO Demuestra**:
  - Una ruptura de la seguridad criptográfica de ML-KEM / Kyber (FIPS 203).
  - Vulnerabilidades de canal lateral físico (SPA/DPA) fuera del modelo estadístico de datos.

---

## 7. Cita

```bibtex
@software{Peinador_LWE_MLKEM_Audit_2026,
  author = {Peinador, Ricardo},
  title = {Modular Projection Effects and Implementation Audit in LWE and ML-KEM},
  year = {2026},
  version = {1.0.0},
  url = {https://github.com/framework-lwe/modular-projection}
}
```

---

## 8. Licencia

Distribuido bajo la Licencia [MIT](LICENSE).
