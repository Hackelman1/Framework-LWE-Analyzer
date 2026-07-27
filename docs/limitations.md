# Limitaciones Explícitas y Alcance Criptográfico del Framework

Este documento delimita formalmente el alcance de las conclusiones obtenidas en el **Framework de Evaluación Experimental de Proyecciones LWE $\mathbb{Z}_q \to \mathbb{Z}_m$**.

---

## 1. Alcance Criptográfico y Seguridad de Esquemas Prácticos

> [!CAUTION]
> **No Ruptura de Seguridad**:
> Los resultados de este estudio **no constituyen ni implican una ruptura de seguridad, ataque de clave ni vulnerabilidad criptográfica** en esquemas post-cuánticos estandarizados como **ML-KEM (Kyber)** o **Falcon**.

- **Propiedad Estadística Interna**: El fenómeno analizado describe la transformación de la distribución de probabilidad del ruido observable bajo proyecciones algebraicas explícitas $\mathbb{Z}_q \to \mathbb{Z}_m$.
- **Preservación de Seguridad**: El hecho de que el ruido efectivo observable $e_{\text{efectivo}} = (b_m - A_m s_m) \bmod m$ sea **perfectamente uniforme** cuando $\gcd(q, m) = 1$ confirma que la proyección no filtra información utilizable sobre la clave reducida $s \bmod m$, preservando la dureza del problema.

---

## 2. Limitaciones de las Evaluaciones Computacionales

1. **Dimensiones Reducidas ($n \le 5$)**:
   - Las pruebas del atacante bayesiano ideal (MLE) y las estimaciones exactas a posteriori de la Información Mutua $I(S_m; B_m \mid A_m)$ se realizan mediante enumeración completa sobre el espacio de claves de tamaño $m^n$.
   - Para dimensiones prácticas (ej. Kyber-512/768/1024 con $n = 256$), la enumeración exhaustiva es computacionalmente intratable ($6^{256} \approx 10^{199}$ candidatos).

2. **Aproximación Asintótica del Envoltorio**:
   - La prueba de uniformidad de $P(k \bmod m) \to U(\mathbb{Z}_m)$ se sostiene en la aproximación asintótica para $q / m \gg 1$ y $A, s \sim U(\mathbb{Z}_q)$.
   - Si las matrices $A$ o los secretos $s$ provienen de distribuciones no uniformes o estructuradas en anillos finitos específicos (ej. Module-LWE o Ring-LWE), la tasa de convergencia requiere análisis algebraicos adicionales en retículos ideales.

3. **Supuesto de Muestreo de Múltiples Muestras**:
   - Las estimaciones experimentales asumen muestras LWE obtenidas de matrices $A$ independientes.

4. **Sesgo Positivo en Estimadores de Entropía e Información Mutua**:
   - La estimación empírica de información mutua $I(S; \text{Salida})$ sobre muestras de tamaño finito $N$ sufre del sesgo positivo inherente de la entropía plug-in de Shannon.
   - El framework aplica la **corrección de Miller-Madow**:
     $$\text{Bias}_{\text{MM}} = \frac{K_{XY} - K_X - K_Y + 1}{2 N \ln 2}$$
     junto con intervalos de confianza empíricos al $95\%$ mediante distribuciones $t$-Student para acotar la compatibilidad estadística con cero ($0.0000$ bits).

5. **Sensibilidad a Sesgos en Implementaciones de Alto Rendimiento (AVX2 / No Tiempo Constante)**:
   - Pequeños sesgos numéricos en algoritmos de reducción modular imprecisa o imprecisiones en el empaquetamiento de bits (`coefficient_pack`) en código optimizado de C/AVX2 pueden reintroducir patrones observantes o canales laterales de fuga. La opción `reduction_type="biased"` del auditor permite modelar expresamente esta desviación.

6. **Dependencia de la Uniformidad de las Entradas y Fuentes RNG**:
   - Las conclusiones de uniformización asumen que las entradas a los transformadores y generadores provienen de una distribución completamente uniforme $U(\mathbb{Z}_q)$. Si el generador de números pseudoaleatorios (RNG) sufre degradación de entropía o el secreto proviene de un subespacio sesgado, la independencia estadística puede colapsar bajo un ataque activo.

---

## 4. Declaración de Integridad Metodológica

El objetivo exclusivo de este framework es proporcionar una **caracterización rigurosa y reproducible de la física probabilística del envoltorio modular** en proyecciones LWE y auditorías de implementación en ML-KEM / Kyber, estableciendo el límite matemático exacto entre proyecciones que conservan estructura y proyecciones que uniformizan el ruido.

