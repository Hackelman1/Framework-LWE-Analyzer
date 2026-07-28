# Metodología del Auditor Criptográfico (`auditor.py`) (v2.0.0)

**Proyecto:** `pqc-statistical-auditor`  
**Autor:** Ricardo Peinador  
**Versión:** 2.0.0  

---

## Flujo de Trabajo de la Auditoría

El auditor automatizado `auditor.py` realiza la siguiente secuencia de evaluación sobre un esquema reticular:

1. **Instanciación del Esquema**: Muestra instancias completas $b = A s + e$ para los parámetros de ML-KEM (Kyber512, Kyber768, Kyber1024) y ML-DSA (FIPS 204).
2. **Aplicación de la Transformación Proyectiva / Aritmética**: Reduce coeficientes módulo $m$ o aplica operadores de compresión, desintegración y generación de hints.
3. **Extracción del Ruido Efectivo o Salida**: Calcula $e_{\text{efectivo}} = (b_m - A_m s_m) \bmod m$ sobre todos los coeficientes.
4. **Métricas Estadísticas Robustas (v2.0.0)**:
   - Discretización por binios fijos ($B = 256$) garantizando $N \gg K_{XY}$.
   - Entropía de Shannon de los coeficientes.
   - Divergencia KL respecto a la distribución uniforme $U(\mathbb{Z}_m)$.
   - Información mutua corregida por Miller-Madow en bits:
     $$\text{Bias}_{\text{MM}} = \frac{K_{XY} - K_X - K_Y + 1}{2 N \ln 2}$$
   - Tests de permutación ($P = 500$, `seed=42`) con suavizado Add-One de Phipson & Smyth (2010).
   - Control de FDR vía Benjamini-Hochberg ($M = 23$) sobre la familia de fuga.
5. **Emisión del Diagnóstico**: Emite `PASS` ($q > 0.05$) o `WARNING` en caso contrario.

