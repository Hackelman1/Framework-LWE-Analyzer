# Auditoría de Transformaciones Nivel Implementación (`docs/implementation_audit.md`)

## 1. Propósito de la Auditoría

El auditor `KyberTransformAuditor` (ubicado en `schemes/module_lwe/kyber_transform_audit.py`) permite evaluar empíricamente si las transformaciones de implementación empleadas en **ML-KEM / Kyber** introducen::
1. **Pérdida de uniformidad** en los coeficientes cifrados o comprimidos.
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

### 2.5 `audit_secret_leakage_after_transform(...)`
Cuantifica la información mutua residual entre el secreto $S$ y la salida del transformador, calculando la ganancia de probabilidad de éxito de un atacante Bayesiano.

---

## 3. Criterios de Riesgo e Interpretación

- **Sin filtración (Riesgo Bajo)**: $D_{\text{KL}} < 0.05$ bits, $I(S; \text{Output}) \approx 0.000$ bits, Ventaja Bayesiana $< 0.01$.
- **Alerta de Sesgo (Riesgo Alto)**: $D_{\text{KL}} \ge 0.05$ bits, p-valor $\chi^2 < 0.01$, o $I(S; \text{Output}) > 0.05$ bits.

---

## 4. Matices Técnicos y Puntos de Atención en la Auditoría

1. **Estimación Dessesgada de Información Mutua $I(S; \text{Salida})$**:
   - Dado que los estimadores discretos empíricos presentan un sesgo positivo estocástico $\mathcal{O}(1/N)$, el auditor emplea la **corrección de Miller-Madow**:
     $$\text{Bias} = \frac{K_{XY} - K_X - K_Y + 1}{2 N \ln 2}$$
   - Esto evita interpretar ruido estadístico muestral como filtración real de información sobre el secreto.

2. **Implementaciones de Alto Rendimiento (AVX2 / C sin tiempo constante)**:
   - En implementaciones reales (ej. librerías optimizadas en C con instrucciones vectoriales AVX2), reducciones modulares imprecisas (Barrett/Montgomery truncados) o manipulaciones de bits en `coefficient_pack` pueden reintroducir asimetrías de frecuencia. La modalidad `reduction_type="biased"` permite auditar explícitamente estos escenarios.

3. **Supuesto de Entropía Completa en las Entradas**:
   - Las garantías de uniformidad y la ausencia de información mutua asumen que la matriz de clave pública $A$ y los secretos provienen de un generador de aleatoriedad criptográficamente seguro (CSPRNG). La degradación de entropía en el RNG invalida el supuesto de uniformización.

