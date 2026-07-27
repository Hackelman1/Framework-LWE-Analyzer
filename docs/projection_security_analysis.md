# Análisis Criptográfico de Seguridad en Proyecciones Modulares

## Diagnóstico de Seguridad

Este documento resume las pautas de análisis para clasificar la seguridad estocástica de transformaciones proyectivas en esquemas reticulares:

1. **Condición de Mezcla Perfecta ($\gcd(q, m) = 1$)**:
   - Para esquemas estándar ($q=3329$), la proyección a $m \in \{2, 3, 4, 5, 6, 8, 12, 16, 32\}$ satisface $\gcd(3329, m) = 1$.
   - El ruido efectivo observable resulta indistinguible de uniforme. **No existe filtración de información útil sobre la clave**.

2. **Diagnóstico de Vulnerabilidad ($\gcd(q, m) > 1$)**:
   - Si se modificara artificialmente el módulo $q$ a un valor par o múltiplo de $m$ (ej. $q=3330, m=6 \implies \gcd=6$), el subgrupo generado se colapsa a $\{0\}$.
   - El ruido observable conserva la distribución CBD original y el atacante Bayesiano recupera el secreto con un **100% de éxito**.
