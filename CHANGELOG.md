# Changelog

Todos los cambios notables en este proyecto se documentarán en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/)
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] - 2026-07-28

### Añadido
- **Auditoría Integral de ML-DSA (FIPS 204)**: Cobertura completa para las transformaciones aritméticas de firma digital `Decompose` ($r_0$), `Power2Round` ($t_0$) y `MakeHint`/`UseHint` ($h$).
- **Discretización por Binios Fijos ($B = 256$)**: Implementación de agrupamiento en $256$ binios continuos para acotar el espacio bidimensional conjunto $K_{XY} \le 2,304$ celdas, garantizando un régimen de muestreo denso ($N / K_{XY} \ge 217.0$ muestras/celda para $N = 500,000$).
- **Suavizado Add-One de Phipson & Smyth (2010)**: Estimación de $p$-valores empíricos mediante $p = (1 + \text{count}) / (P + 1)$ con $P = 500$ permutaciones y semilla fija (`seed = 42`), eliminando reportes inválidos de $p = 0.0$.
- **Agregación Bonferroni Interna para Barridos Paramétricos**: Transformación $\tilde{p}_m = \min(K_m \cdot p_{\min}, 1.0)$ para consolidar barridos internos de $K$ subconfiguraciones, preservando la validez estocástica $P(\tilde{p} \le t) \le t$ bajo $H_0$.
- **Separación Estricta de Familias de Hipótesis**: Desacoplamiento explícito entre la familia de fuga de información ($\mathbb{H}_0^{\text{leakage}}$) y la familia de uniformidad marginal ($\mathbb{H}_0^{\text{uniformity}}$).
- **Ajuste Global de Benjamini-Hochberg (BH-FDR)**: Control de multiplicidad aplicado exclusivamente sobre las $M = 23$ hipótesis de fuga, demostrando su convergencia exacta a FWER bajo la nula global ($\mathbb{H}_0^{\text{global}}$).
- **Suite de Pruebas Unitarias Aumentada**: Cobertura expandida a 28/28 tests pasados con éxito, incluyendo validaciones de casos límite para FDR ($N = 0, 1$) y preservación de distribuciones nulas con signo.

### Cambiado
- **Corrección Analítica de Miller-Madow**: Unificación del factor $\ln 2$ en el denominador para expresar el sesgo estrictamente en bits: $\text{Bias}_{\text{MM}} = (K_{XY} - K_X - K_Y + 1) / (2 N \ln 2)$.
- **Eliminación del Sesgo de Jensen**: Eliminación del recorte prematuro `max(0, ...)` sobre la distribución nula durante el bucle de permutaciones, garantizando una comparación estocástica neutral.
- **Homogeneización de Autoría y Metadatos**: Actualización unificada del autor a Ricardo Peinador en `paper/main.md`, `CITATION.cff`, `README.md` y archivos de documentación interna en `docs/`.
- **Estructura del Proyecto**: Repositorio renombrado oficialmente a `pqc-statistical-auditor`.

### Corregido
- **Aumento de Potencia en Permutaciones**: Sustitución del parámetro obsoleto $P = 5$ por $P = 500$ iteraciones, otorgando resolución estadística suficiente ($p_{\min} \approx 0.001996$) para pruebas de hipótesis formales.
- **Inconsistencia de Notación en Teoremas**: Reclasificación del Teorema de Contracción a "Nivel 1 Condicional", explicitando la necesidad de la condición de independencia $e \bmod m \perp\!\!\!\perp k q \bmod m$ garantizada por el término de enmascaramiento $A s \bmod q$.
- **Incompatibilidad de SciPy**: Actualización de dependencias en `requirements.txt` a `scipy>=1.11.0` para soporte nativo de `scipy.stats.false_discovery_control`.


## [v1.0.0] - 2026-07-27

### Añadido
- **Fase 11: Auditoría de Transformaciones Reales en ML-KEM / Kyber (FIPS 203)**:
  - Módulo `transformations/kyber_transformations.py` para compresión $\text{Compress}_d$, descompresión $\text{Decompress}_d$, reducción modular (`exact`, `centered`, `biased`), empaquetamiento de bits/bytes (`coefficient_pack/unpack`) y simulación de error de redondeo.
  - Módulo `schemes/module_lwe/kyber_transform_audit.py` con la clase `KyberTransformAuditor`.
  - Experimentos T (sesgo de compresión), U (ruido de redondeo), V (reducción modular real vs imprecisa) y W (filtración por empaquetamiento de bytes).
  - Nueva sección 8 en `paper/main.md`: *"Implementation-Level Transformations in ML-KEM"*.
  - Suite de auditoría integrada en `auditor.py` mediante la llamada `analyze_scheme(scheme, transformation, parameters)`.
- **Fase 10: Integración Module-LWE y Kyber**:
  - Parámetros Kyber512, Kyber768 y Kyber1024 en `schemes/module_lwe/`.
  - Experimentos Q, R, S para análisis de entropía de coeficientes y comparación entre LWE, RLWE y Module-LWE.
- **Fases 1 a 9: Framework Core & Teorema de Uniformización Modular**:
  - Teorema de Uniformización y cota de distancia estadística de convolución circular.
  - Experimentos A a P para evaluación de sesgo, independencia y ataques MLE.
- **Reproducibilidad y Automatización**:
  - Script maestro `scripts/rebuild_all.py` y script de limpieza `scripts/clean_results.py`.
  - Rutas relativas dinámicas (`Path(__file__)`) y semillas deterministas (`seed=42`).
  - Suite de pruebas unitarias completa en `tests/`.

### Cambios
- Unificación del ejecutor principal en `run_all_experiments.py` cubriendo los 23 experimentos (A a W).
- Actualización completa de la documentación técnica en `docs/` y manuscrito científico en `paper/main.md`.
