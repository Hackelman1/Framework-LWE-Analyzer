# Modular Projection Effects in LWE: Algebraic Conditions for Statistical Noise Uniformization and Implementation Auditing in ML-KEM & ML-DSA

## 01. Introducción

### Contexto y Motivación
Los esquemas de criptografía basada en retículos (Lattice-Based Cryptography), estandarizados por el NIST en las especificaciones **ML-KEM (Kyber / FIPS 203)** y **ML-DSA (Dilithium / FIPS 204)**, basan su seguridad en la dureza de los problemas **Learning With Errors (LWE)**, **Module-LWE (M-LWE)** y **Module Short Integer Solution (M-SIS)**. Una instancia LWE o M-LWE estándar opera sobre un anillo modular primario $\mathbb{Z}_q$, donde las observaciones públicas $b = A s + e \pmod q$ ocultan la clave secreta $s$ agregando un ruido centrado $e$ no uniforme (típicamente Binomial Centrado CBD).

En diversos escenarios de análisis algebraico, pruebas de resistencia y auditoría de implementaciones, se estudian proyecciones homomórficas hacia anillos residuales $\mathbb{Z}_m$ con $m \ll q$, así como funciones aritméticas de descomposición, truncamiento y redondeo modular. Un interrogante fundamental es: **¿Conserva el error o residuo observable bajo dichas operaciones la estructura no uniforme del ruido original o se uniformiza, y existen fugas de información mutua sobre el secreto en las transformaciones reales de implementación?**

Este trabajo presenta la caracterización matemática completa y la validación experimental del **Teorema de Uniformización Modular LWE**, extendiendo su alcance hacia la auditoría estadística rigurosa de las transformaciones de implementación de los estándares FIPS 203 (ML-KEM) y FIPS 204 (ML-DSA), abarcando desde la compresión y empaquetamiento hasta las funciones de descomposición (`Decompose`), redondeo de clave pública (`Power2Round`) y generación de vectores de pistas (`MakeHint` / `UseHint`).
