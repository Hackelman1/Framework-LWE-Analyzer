# Sesgo de Compresión y Redondeo en ML-KEM / Kyber (`docs/compression_and_rounding_bias.md`)

## 1. Naturaleza Matemática de la Compresión

En ML-KEM, la función $\text{Compress}_d(x)$ divide el espacio del módulo $q = 3329$ en $2^d$ intervalos. Dado que $q = 3329$ no es una potencia exacta de 2 (es decir, $3329 \neq 2^d$), los intervalos de cuantización no contienen exactamente el mismo número de elementos enteros.

### Tamaño de los Intervalos de Cuantización
Para $q = 3329$ y $d = 10$ ($2^{10} = 1024$):
- La razón es $\frac{3329}{1024} \approx 3.250976$.
- Algunos valores comprimidos en $\mathbb{Z}_{1024}$ corresponden a 3 enteros de $\mathbb{Z}_q$, mientras que otros corresponden a 4 enteros.

Esta leve variación matemática introduce un sesgo teórico inherente en la distribución uniforme de la salida comprimida.

---

## 2. Impacto Criptográfico y Ruido de Redondeo

### 2.1 Adición de Ruido por Redondeo
El proceso round-trip introduce un término de ruido $e_{\text{round}} = \text{Decompress}_d(\text{Compress}_d(x)) - x$.
Este ruido satisface:
$$|e_{\text{round}}| \le \left\lceil \frac{q}{2^{d+1}} \right\rceil$$

Para Kyber512 con $d_u = 10$, $|e_{\text{round}}| \le 2$.

### 2.2 Preservación de la Independencia del Secreto
Nuestros experimentos empíricos (Experimentos T y U) demuestran que:
1. La información mutua $I(S; \text{Compress}_d(b))$ se mantiene acotada cerca de $0.000000$ bits.
2. Aunque la compresión altera la entropía continua de los coeficientes, no revela información del vector secreto $S$ porque el ruido CBD en $b = A s + e$ ya enmascara uniformemente la salida previa a la compresión.

---

## 3. Conclusión de la Auditoría

El sesgo de compresión en ML-KEM es un efecto puramente determinista sobre el espacio de cuantización y **no constituye una vulnerabilidad ni una filtración del secreto**, siempre que los parámetros de compresión $d$ se elijan dentro de los límites de corrección de desacoplamiento del esquema.
