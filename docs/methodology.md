# Metodología de Auditoría Estadística de PQC (v2.0.0)

**Proyecto:** `pqc-statistical-auditor`  
**Autor:** Ricardo Peinador  
**Versión:** 2.0.0  
**Ámbito:** ML-KEM (FIPS 203), ML-DSA (FIPS 204), LWE / Ring-LWE / Module-LWE  

---

## 1. Alcance y Filosofía Metodológica

El framework `pqc-statistical-auditor` implementa una suite unificada para la evaluación empírica y teórica de la uniformización de ruido y ausencia de filtración de información mutua en esquemas basados en retículos (LWE, M-LWE) y transformaciones reales a nivel de implementación en **ML-KEM (FIPS 203)** y **ML-DSA (FIPS 204)**.

---

## 2. Garantías Estadísticas Centrales

### 2.1 Agrupamiento por Binios Fijos ($B = 256$)
Para auditar espacios de estados discretos de gran tamaño (ej. $|R_0| \in [190465, 523777]$ en la descomposicion de ML-DSA), las salidas continuas (`Decompose` y `Power2Round`) se discretizan en $B = 256$ binios de ancho fijo.
- Para $N = 500,000$ muestras, el espacio conjunto satisface $K_{XY} = |S| \times B \le 2,304$ celdas.
- Densidad muestral garantizada: $N / K_{XY} \ge 217.0$ muestras por celda ($N \gg K_{XY}$).

### 2.2 Corrección Analítica de Miller-Madow en BITS
La información mutua bruta $I_{\text{plugin}}$ se corrige mediante la fórmula exacta expresada en **bits** utilizando el logaritmo natural explícito:

$$\text{Bias}_{\text{MM}} = \frac{K_{XY} - K_X - K_Y + 1}{2 N \ln 2}$$

$$I_{\text{MM\_raw}} = I_{\text{plugin}}(S; Y) - \text{Bias}_{\text{MM}}$$

### 2.3 Test de Permutación con Suavizado Add-One
- **Permutaciones:** $P = 500$ iteraciones estocásticas con semilla determinista `seed = 42`.
- **Distribución Nula con Signo:** Los valores nulos $I_{\text{null\_raw}} = I_{\text{null\_plugin}} - \text{Bias}_{\text{MM}}$ conservan su signo real sin truncamiento prematuro por desigualdad de Jensen (`max(0, ...)`).
- **p-valor Empírico Add-One (Phipson & Smyth, 2010):**

$$p = \frac{1 + \sum_{i=1}^P \mathbb{I}\left(I_{\text{null\_raw}}^{(i)} \ge I_{\text{MM\_raw}}\right)}{P + 1}$$

### 2.4 Agregación de Barridos mediante Bonferroni Interno
Para experimentos con barridos paramétricos ($K_m$ subconfiguraciones, ej. dimensiones $n \in [1..32]$ o muestras $N \in [10^3..10^6]$), el $p$-valor de la prueba de barrido se agrega mediante la corrección conservadora interna de Bonferroni:

$$\tilde{p}_m = \min\left(K_m \cdot \min_{k \in \{1 \dots K_m\}} p_{m, k}, \; 1.0\right)$$

Garantizando que $P(\tilde{p}_m \le t) \le t$ bajo la hipótesis nula $\mathbb{H}_0$, restaurando la validez estocástica necesaria para el ajuste posterior de FDR.

### 2.5 Separación de Familias de Hipótesis
Las pruebas estadísticas se dividen en dos familias estrictamente independientes:
1. **Familia de Fuga de Información ($\mathbb{H}_0^{\text{leakage}}$):** Evaluada mediante tests de permutaciones de información mutua ($I_{\text{net}} = 0$).
2. **Familia de Uniformidad Marginal ($\mathbb{H}_0^{\text{uniformity}}$):** Evaluada mediante pruebas de bondad de ajuste de Chi-Cuadrado ($\chi^2$).

### 2.6 Control Global de FDR vía Benjamini-Hochberg ($M = 23$)
- Se aplica `scipy.stats.false_discovery_control` exclusivamente sobre el pool de $M = 23$ pruebas de la familia de fuga de información.
- **Convergencia a FWER:** Bajo la hipótesis nula global ($\mathbb{H}_0^{\text{global}}$: ausencia total de fuga en todas las transformaciones), el False Discovery Rate colapsa exactamente al Family-Wise Error Rate ($\text{FDR} = \text{FWER} = \mathbb{P}(V \ge 1)$).
- Criterio de aceptación: Se declara **PASS** si el $q$-valor ajustado satisface $q > 0.05$.
