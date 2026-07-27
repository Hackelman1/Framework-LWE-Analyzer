# Modular Projection Effects in LWE: Algebraic Conditions for Statistical Noise Uniformization

## 01. Introducción

### Contexto y Motivación
Los esquemas de criptografía basada en retículos (Lattice-Based Cryptography), tales como **ML-KEM (Kyber)** o **Falcon**, basan su seguridad en la dureza del problema **Learning With Errors (LWE)** y sus variantes de módulo (M-LWE) y anillo (R-LWE). Una instancia LWE estándar opera sobre un anillo modular primario $\mathbb{Z}_q$, donde las observaciones públicas $b = A s + e \pmod q$ ocultan la clave secreta $s$ agregando un ruido centrado $e$ no uniforme (típicamente Binomial Centrado CBD).

En diversos escenarios de análisis algebraico y pruebas de resistencia, se estudian proyecciones homomórficas hacia anillos residuales $\mathbb{Z}_m$ con $m \ll q$. Un interrogante fundamental es: **¿Conserva el error observable bajo dicha proyección la estructura no uniforme del ruido original o se uniformiza?**

Este trabajo presenta la caracterización matemática completa y la validación experimental del **Teorema de Uniformización Modular LWE**, demostrando las condiciones algebraicas y probabilísticas exactas bajo las cuales la reducción modular uniformiza el ruido efectivo observable.
