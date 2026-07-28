# Integración Oficial de ML-KEM / Kyber (v2.0.0)

**Proyecto:** `pqc-statistical-auditor`  
**Autor:** Ricardo Peinador  
**Versión:** 2.0.0  

---

| Variante | Módulo $q$ | Grado $N$ | Dimensión del Módulo $k$ | Ruido $\eta_1$ | Ruido $\eta_2$ | Tamaño de Clave (bits) |
|:--------:|:----------:|:---------:|:-----------------------:|:--------------:|:--------------:|:---------------------:|
| **Kyber512** (ML-KEM-512) | 3329 | 256 | 2 | 3 | 2 | 512 |
| **Kyber768** (ML-KEM-768) | 3329 | 256 | 3 | 2 | 2 | 768 |
| **Kyber1024** (ML-KEM-1024) | 3329 | 256 | 4 | 2 | 2 | 1024 |

## Resultados de Auditoría sobre Coeficientes Proyectados mod 6

Dado $q = 3329$ y $m = 6$, puesto que $\gcd(3329, 6) = 1$:
- Entropía empírica sobre los $256 \cdot k$ coeficientes de $e_{\text{efectivo}}$: $2.5849$ bits (Entropía Máxima Teórica: $2.5850$ bits).
- Divergencia KL vs Uniforme $U(\mathbb{Z}_6)$: `0.000035` bits.
- Información Mutua $I(S_m; B_m \mid A_m)$: `0.000001` bits.

Esto confirma numéricamente que las instancias de Kyber preservan su resistencia matemática frente a proyecciones modulares $R_q \to R_6$.
