# 02. Preliminares Matemáticos de LWE y M-LWE

## Definición de LWE, M-LWE y Notación
Sea $q \ge 3$ un entero y $n = 256$ el grado del polinomio definitorio del anillo $R_q = \mathbb{Z}_q[X]/(X^n + 1)$. 
Una instancia LWE o M-LWE genera muestras sobre $\mathbb{Z}_q$ o $R_q^k$ de la forma:
$$b = A s_1 + s_2 \pmod q$$
donde:
- $s_1 \in R_q^l$ y $s_2 \in R_q^k$ son vectores de clave secreta o ruido.
- $A \in R_q^{k \times l}$ es la matriz pública uniforme $U(R_q^{k \times l})$.
- $b \in R_q^k$ es el vector público de observaciones.

En ML-KEM (FIPS 203), $q = 3329$ y el ruido sigue una distribución binomial centrada. En ML-DSA (FIPS 204), $q = 8380417$ y los vectores secretos se muestrean de una distribución discreta acotada.

## Distribuciones de Secreto y Ruido

### 1. Distribución Binomial Centrada ($\text{CBD}$)
Utilizada en ML-KEM, la distribución $\text{CBD}(\eta)$ se define como la diferencia de dos variables aleatorias binomiales independientes:
$$e = \sum_{i=1}^\eta a_i - \sum_{i=1}^\eta b_i, \quad a_i, b_i \leftarrow U(\{0, 1\})$$
La PMF teórica de $e \in [-\eta, \eta]$ satisface $P(e = k) = \frac{1}{4^\eta} \binom{2\eta}{\eta + k}$. Al reducir $e \bmod m$, si $m > 2\eta + 1$, el soporte no envuelve y la distribución conserva su asimetría estadística.

### 2. Distribución Uniforme Discreta Acotada $U([-\eta, \eta])$
Utilizada en ML-DSA (FIPS 204) para los vectores de clave secreta $S_1$ y $S_2$, donde los coeficientes se eligen equiprobablemente de un intervalo entero pequeño:
$$S_{1,i}, S_{2,i} \sim U([-\eta, \eta]), \quad \text{con } \eta \in \{2, 4\}$$
La PMF teórica para cada coeficiente es $P(S = k) = \frac{1}{2\eta + 1}$ para toda $k \in [-\eta, \eta]$.

## Parámetros Aritméticos de ML-DSA (FIPS 204)
Las transformaciones de implementación de ML-DSA operan sobre el módulo primario $q = 8380417 = 2^{23} - 2^{13} + 1$ y emplean las siguientes constantes según el nivel de seguridad:
- **Truncamiento de Clave Pública ($d$)**: $d = 13$ bits, con espacio de residuos $2^d = 8192$.
- **Parámetros de Descomposición ($\gamma_2$)**: $\gamma_2 = 95232 = (q-1)/88$ (ML-DSA-44) o $\gamma_2 = 261888 = (q-1)/32$ (ML-DSA-65/87).
- **Límites de Enmascaramiento ($\gamma_1$)**: $\gamma_1 = 2^{17} = 131072$ (ML-DSA-44) o $\gamma_1 = 2^{19} = 524288$ (ML-DSA-65/87).
