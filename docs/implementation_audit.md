# Auditoría de Transformaciones Nivel Implementación (v2.0.0)

**Proyecto:** `pqc-statistical-auditor`  
**Autor:** Ricardo Peinador  
**Versión:** 2.0.0  

---

## 1. Propósito de la Auditoría

El auditor de transformaciones de implementación (en `schemes/module_lwe/kyber_transform_audit.py` y `transformations/dsa/audit_dsa.py`) permite evaluar empíricamente si las transformaciones de implementación empleadas en **ML-KEM (FIPS 203)** y **ML-DSA (FIPS 204)** introducen:
1. **Pérdida de uniformidad** en los coeficientes cifrados, comprimidos o descompuestos.
2. **Sesgo estadístico** medible mediante prueba de $\chi^2$ y divergencia KL.
3. **Huellas estructurales en el empaquetamiento de bytes** (`coefficient_pack`).
4. **Filtración de información mutua** $I(S; \text{Salida})$ hacia un atacante estadístico.
5. **Ventaja Bayesiana** observada frente al intento aleatorio.

---

## 2. Métodos de Auditoría

### 2.1 `audit_compression_bias(d, trials)`
Evalúa la distribución de coeficientes comprimidos en $\mathbb{Z}_{2^d}$. Mide si la reducción de resolución altera la entropía máxima teórica de $d$ bits.

### 2.2 `audit_rounding_bias(d, trials)`
Mide la distribución del ruido efectivo añadido por redondeo $\Delta = x' - x$. Comprueba si el error es centrado en cero y si exhibe alguna dependencia con el vector secreto $S$.

### 2.3 `audit_modular_reduction(trials, reduction_type)`
Compara la reducción exacta frente a reducciones sesgadas simuladas, detectando asimetrías en histogramas mediante pruebas de bondad de ajuste $\chi^2$.

### 2.4 `audit_pack_unpack_leakage(d, trials)`
Analiza el flujo de bytes empaquetados resultantes de convertir coeficientes de $d$ bits a arreglos de 8 bits. Evalúa la entropía por byte $H_{\text{byte}} \le 8.0$ bits.

### 2.5 `audit_dsa_decompose(...)`, `audit_dsa_power2round(...)`, `audit_dsa_make_hint(...)`
Evalúa la ausencia de filtración de información mutua en los residuos de firma y clave pública de ML-DSA (FIPS 204) utilizando $B = 256$ binios fijos, test de permutaciones ($P=500$, `seed=42`) y suavizado Add-One.

---

## 3. Criterios de Riesgo e Interpretación

- **Sin filtración (PASS)**: $q$-valor ajustado por BH-FDR $q > 0.05$.
- **Alerta de Sesgo (WARNING)**: $q$-valor ajustado por BH-FDR $q \le 0.05$.

---

## 4. Matices Técnicos y Puntos de Atención en la Auditoría

1. **Estimación Dessesgada de Información Mutua $I(S; \text{Salida})$**:
   - Dado que los estimadores discretos empíricos presentan un sesgo positivo estocástico $\mathcal{O}(1/N)$, el auditor emplea la **corrección de Miller-Madow en bits**:
     $$\text{Bias}_{\text{MM}} = \frac{K_{XY} - K_X - K_Y + 1}{2 N \ln 2}$$
   - Esto evita interpretar ruido estadístico muestral como filtración real de información sobre el secreto.


2. **Implementaciones de Alto Rendimiento (AVX2 / C sin tiempo constante)**:
   - En implementaciones reales (ej. librerías optimizadas en C con instrucciones vectoriales AVX2), reducciones modulares imprecisas (Barrett/Montgomery truncados) o manipulaciones de bits en `coefficient_pack` pueden reintroducir asimetrías de frecuencia. La modalidad `reduction_type="biased"` permite auditar explícitamente estos escenarios.

3. **Supuesto de Entropía Completa en las Entradas**:
   - Las garantías de uniformidad y la ausencia de información mutua asumen que la matriz de clave pública $A$ y los secretos provienen de un generador de aleatoriedad criptográficamente seguro (CSPRNG). La degradación de entropía en el RNG invalida el supuesto de uniformización.

