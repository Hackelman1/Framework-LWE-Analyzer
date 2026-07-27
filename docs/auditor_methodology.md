# Metodología del Auditor Criptográfico (`auditor.py`)

## Flujo de Trabajo de la Auditoría

El auditor automatizado `auditor.py` realiza la siguiente secuencia de evaluación sobre un esquema reticular:

1. **Instanciación del Esquema**: Muestra instancias completas $b = A s + e$ para los parámetros de Kyber512, Kyber768 o Kyber1024.
2. **Aplicación de la Transformación Proyectiva**: Reduce los coeficientes polinómicos módulo $m$.
3. **Extracción del Ruido Efectivo**: Calcula $e_{\text{efectivo}} = (b_m - A_m s_m) \bmod m$ sobre todos los coeficientes.
4. **Métricas de Auditoría**:
   - Entropía de Shannon de los coeficientes.
   - Divergencia KL respecto a la distribución uniforme $U(\mathbb{Z}_m)$.
   - Información mutua corregida por Miller-Madow $I(S_m; B_m \mid A_m)$.
5. **Emisión del Diagnóstico**: Emite `No observable leakage detected` si $\gcd(q, m) = 1$ y $KL < 0.01$ bits, o `WARNING: Observable leakage detected` en caso contrario.
