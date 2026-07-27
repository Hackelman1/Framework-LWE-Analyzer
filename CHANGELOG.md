# Changelog

Todos los cambios notables en el framework de proyección LWE y auditoría estadística serán documentados en este archivo.

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
