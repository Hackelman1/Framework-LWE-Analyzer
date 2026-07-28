# Limitaciones Explícitas y Alcance Criptográfico del Framework (v2.0.0)

**Proyecto:** `pqc-statistical-auditor`  
**Autor:** Ricardo Peinador  
**Versión:** 2.0.0  

---

## 1. Alcance Criptográfico y Seguridad de Esquemas Prácticos

> [!CAUTION]
> **No Ruptura de Seguridad**:
> Los resultados de este estudio **no constituyen ni implican una ruptura de seguridad, ataque de clave ni vulnerabilidad criptográfica** en esquemas post-cuánticos estandarizados por NIST como **ML-KEM (FIPS 203)**, **ML-DSA (FIPS 204)** o **Falcon**.

- **Propiedad Estadística Interna**: El fenómeno analizado describe la transformación de la distribución de probabilidad del ruido observable y la ausencia de filtración de información mutua en proyecciones algebraicas explícitas y transformaciones de implementación.
- **Preservación de Seguridad**: El hecho de que el ruido efectivo observable $e_{\text{efectivo}} = (b_m - A_m s_m) \bmod m$ sea **perfectamente uniforme** cuando $\gcd(q, m) = 1$ confirma que la proyección no filtra información utilizable sobre la clave reducida $s \bmod m$, preservando la dureza del problema.

---

## 2. Limitaciones de las Evaluaciones Computacionales

1. **Dimensiones Reducidas ($n \le 5$)**:
   - Las pruebas del atacante bayesiano ideal (MLE) y las estimaciones exactas a posteriori de la Información Mutua $I(S_m; B_m \mid A_m)$ se realizan mediante enumeración completa sobre el espacio de claves de tamaño $m^n$.
   - Para dimensiones prácticas (ej. Kyber-512/768/1024 con $n = 256$), la enumeración exhaustiva es computacionalmente intratable ($6^{256} \approx 10^{199}$ candidatos).

2. **Criterio de Independencia Condicional**:
   - El Teorema de Contracción Condicional de la convolución circular $P(e_{\text{effective}}) = P_e \circledast P_{kq}$ requiere la condición estocástica $e \bmod m \perp\!\!\!\perp k q \bmod m$, la cual en los esquemas prácticos es garantizada por el término de enmascaramiento de alta entropía $A s \bmod q$.

3. **Agregación Bonferroni Interna y Control Global BH-FDR ($M = 23$)**:
   - Para barridos paramétricos ($K$ subconfiguraciones), los $p$-valores se agregan mediante Bonferroni interno ($\tilde{p}_m = \min(K_m \cdot p_{\min}, 1.0)$) garantizando $P(\tilde{p} \le t) \le t$ bajo $\mathbb{H}_0$.
   - Se aplica el control BH-FDR globalmente sobre el pool de $M = 23$ hipótesis de la familia de fuga, colapsando a FWER bajo $\mathbb{H}_0^{\text{global}}$. La familia de uniformidad marginal ($\chi^2$) se evalúa de forma independiente.

4. **Corrección de Sesgo de Miller-Madow en BITS**:
   - La estimación de información mutua $I(S; \text{Salida})$ sobre $B = 256$ binios fija la densidad muestral $N / K_{XY} \ge 217.0$ ($N = 500,000$) y utiliza la corrección exacta en bits:
     $$\text{Bias}_{\text{MM}} = \frac{K_{XY} - K_X - K_Y + 1}{2 N \ln 2}$$

5. **Modelo Estadístico de Datos**:
   - El análisis está restringido exclusivamente al modelo estadístico de datos observables y algoritmos numéricos. No evalúa ataques físicos de canal lateral (DPA, SPA, tiempos de microarquitectura) ni inyección de fallos.

---

## 3. Declaración de Integridad Metodológica

El objetivo exclusivo de este framework es proporcionar una **caracterización rigurosa y reproducible de la física probabilística del envoltorio modular** en proyecciones LWE y auditorías de implementación en ML-KEM (FIPS 203) y ML-DSA (FIPS 204), estableciendo el límite matemático exacto entre proyecciones que conservan estructura y proyecciones que uniformizan el ruido.


