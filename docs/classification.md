# Clasificación General de Proyecciones LWE $\mathbb{Z}_q \to \mathbb{Z}_m$

Este documento establece la taxonomía completa y la clasificación técnica del comportamiento del ruido efectivo observable $e_{\text{efectivo}} = (b_m - A_m s_m) \bmod m$ al proyectar instancias LWE desde un anillo primario $\mathbb{Z}_q$ hacia cualquier anillo modular objetivo $\mathbb{Z}_m$ ($m \ge 2$).

---

## 1. Taxonomía de Tres Casos de Proyección

```
                      Proyección LWE: Z_q  ───>  Z_m
                                   │
              ┌────────────────────┴────────────────────┐
              ▼                                         ▼
      gcd(q, m) = 1                             gcd(q, m) > 1
   [Subgrupo Total |<q>| = m]               [Subgrupo Propio |<q>| = m/g < m]
              │                                         │
     ┌────────┴────────┐                                │
     ▼                 ▼                                ▼
P(k mod m) ≈ U   P(k mod m) !≈ U                   CASO B:
   CASO A:           CASO C:                 Mezcla Restringida
Mezcla Completa   Mezcla Parcial             (Ruido Residual / Vulnerable)
 (UNIFORME)     (Sesgo Residual)
```

### Caso A: Mezcla Completa (Uniformización Absoluta)
- **Condiciones**: $\gcd(q, m) = 1$ Y $P(k \bmod m) \approx U(\mathbb{Z}_m)$.
- **Estructura de Subgrupo**: $G(q,m) = \langle q \rangle = \mathbb{Z}_m$ (tamaño $|G| = m$).
- **Resultado del Ruido Efectivo**: $P(e_{\text{efectivo}}) \equiv P(e \bmod m) \circledast U(\mathbb{Z}_m) = U(\mathbb{Z}_m)$.
- **Divergencia KL**: $KL(e_{\text{efectivo}} \parallel U(\mathbb{Z}_m)) \approx 0.0000$ bits.
- **Impacto Criptográfico**: Destrucción total de la estructura estadística observable del error. El atacante bayesiano ideal no obtiene ninguna ventaja sobre la adivinación uniforme.

### Caso B: Mezcla Restringida al Subgrupo (Vulnerabilidad Residual)
- **Condiciones**: $\gcd(q, m) = g > 1$.
- **Estructura de Subgrupo**: $G(q,m) = \langle q \rangle \subset \mathbb{Z}_m$ es un subgrupo propio estricto de tamaño $|G| = m/g < m$.
- **Resultado del Ruido Efectivo**: La convolución circular se restringe al subgrupo $G(q,m)$, imposibilitando cubrir las $m$ clases de $\mathbb{Z}_m$.
- **Divergencia KL**: $KL(e_{\text{efectivo}} \parallel U(\mathbb{Z}_m)) > 0$ bits (significativa).
- **Caso Extremo ($q \equiv 0 \pmod m$)**: $G(q,m) = \{0\}$, el término de envoltorio desaparece mod $m$, y $e_{\text{efectivo}} \equiv e \bmod m$ conserva íntegramente la no-uniformidad del ruido original, permitiendo un **100% de éxito al atacante MLE**.

### Caso C: Mezcla Parcial por Sesgo de Envoltorio (Módulo Reducido $q$)
- **Condiciones**: $\gcd(q, m) = 1$, pero la escala $q / m$ es pequeña, provocando que $P(k \bmod m)$ no sea perfectamente uniforme.
- **Resultado del Ruido Efectivo**: Muestra pequeñas desviaciones residuales $KL > 0$ que decaen exponencialmente al aumentar $q$.

---

## 2. Tabla General de Clasificación por Pares $(q, m)$

| Módulo $q$ | Módulo $m$ | $\gcd(q,m)$ | Subgrupo Generado $G(q,m)$ | $|G(q,m)|$ | Clasificación de Proyección | KL Esperado vs $U(\mathbb{Z}_m)$ | Tasa Éxito MLE Ideal |
|:----------:|:----------:|:-----------:|:--------------------------:|:----------:|:---------------------------:|:--------------------------------:|:--------------------:|
| **3329** (Kyber) | **2** | **1** | $\mathbb{Z}_2 = \{0, 1\}$ | **2 / 2** | **Caso A (Mezcla Completa)** | $\approx 0.0000$ bits | $1 / 2^n$ (Azar) |
| **3329** (Kyber) | **3** | **1** | $\mathbb{Z}_3 = \{0, 1, 2\}$ | **3 / 3** | **Caso A (Mezcla Completa)** | $\approx 0.0000$ bits | $1 / 3^n$ (Azar) |
| **3329** (Kyber) | **4** | **1** | $\mathbb{Z}_4 = \{0, 1, 2, 3\}$ | **4 / 4** | **Caso A (Mezcla Completa)** | $\approx 0.0000$ bits | $1 / 4^n$ (Azar) |
| **3329** (Kyber) | **5** | **1** | $\mathbb{Z}_5 = \{0, \dots, 4\}$ | **5 / 5** | **Caso A (Mezcla Completa)** | $\approx 0.0000$ bits | $1 / 5^n$ (Azar) |
| **3329** (Kyber) | **6** | **1** | $\mathbb{Z}_6 = \{0, \dots, 5\}$ | **6 / 6** | **Caso A (Mezcla Completa)** | $\approx 0.0000$ bits | $1 / 6^n$ (Azar) |
| **3329** (Kyber) | **12** | **1** | $\mathbb{Z}_{12} = \{0, \dots, 11\}$ | **12 / 12** | **Caso A (Mezcla Completa)** | $\approx 0.0000$ bits | $1 / 12^n$ (Azar) |
| 3328 | 4 | 4 | $\{0\}$ | 1 / 4 | **Caso B (Restringida)** | $\approx 0.0900$ bits | Elevada |
| 3328 | 8 | 8 | $\{0\}$ | 1 / 8 | **Caso B (Restringida)** | $\approx 0.9606$ bits | Elevada |
| 3330 | 5 | 5 | $\{0\}$ | 1 / 5 | **Caso B (Restringida)** | $\approx 0.2862$ bits | Elevada |
| **3330** | **6** | **6** | **$\{0\}$** | **1 / 6** | **Caso B (Vulnerable 100%)** | **`0.5632` bits** | **100.0% (Éxito Total)** |
| 3330 | 9 | 9 | $\{0\}$ | 1 / 9 | **Caso B (Restringida)** | $\approx 1.1396$ bits | Elevada |
| **7681** (Falcon) | **6** | **1** | $\mathbb{Z}_6 = \{0, \dots, 5\}$ | **6 / 6** | **Caso A (Mezcla Completa)** | $\approx 0.0000$ bits | $1 / 6^n$ (Azar) |
| **12289** (NewHope) | **6** | **1** | $\mathbb{Z}_6 = \{0, \dots, 5\}$ | **6 / 6** | **Caso A (Mezcla Completa)** | $\approx 0.0000$ bits | $1 / 6^n$ (Azar) |
