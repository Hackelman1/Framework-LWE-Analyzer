# 02. Preliminares Matemáticos de LWE

## Definición de LWE y Notación
Sea $q \ge 3$ un entero y $n \ge 1$ la dimensión de la clave secreta.
Una distribución LWE $\mathcal{A}_{n, q, \chi}$ genera muestras de la forma $(A, b) \in \mathbb{Z}_q^{m_{\text{muestras}} \times n} \times \mathbb{Z}_q^{m_{\text{muestras}}}$ mediante:
$$b = A s + e \pmod q$$
donde:
- $s \leftarrow U(\mathbb{Z}_q^n)$ es el vector de clave secreta.
- $A \leftarrow U(\mathbb{Z}_q^{m_{\text{muestras}} \times n})$ es la matriz pública.
- $e \sim \chi^{m_{\text{muestras}}}$ es el vector de ruido discreto con distribución $\chi$ centrada en cero (ej. $\text{CBD}(\eta)$).

## Propiedades de la Distribución Binomial Centrada (CBD)
La distribución $\text{CBD}(\eta)$ se define como la diferencia de dos variables aleatorias binomiales independientes:
$$e = \sum_{i=1}^\eta a_i - \sum_{i=1}^\eta b_i, \quad a_i, b_i \leftarrow U(\{0, 1\})$$
La PMF teórica de $e \in [-\eta, \eta]$ satisface $P(e = k) = \frac{1}{4^\eta} \binom{2\eta}{\eta + k}$.
Al reducir $e \bmod m$, si $m > 2\eta + 1$, el soporte no envuelve y la distribución conserva su asimetría estadística.
