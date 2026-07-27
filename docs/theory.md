# Teorema de Uniformización Modular LWE y Caracterización del Ruido Proyectado

## 1. Introducción y Formulación General

Consideremos una instancia LWE estándar sobre el anillo modular $\mathbb{Z}_q$:
$$b = A s + e \pmod q$$
donde $A \in \mathbb{Z}_q^{m_{\text{muestras}} \times n}$, $s \in \mathbb{Z}_q^n$ es la clave secreta, y $e \sim \text{CBD}(\eta)$ representa el ruido original.

Definimos la reducción o proyección modular hacia un anillo objetivo $\mathbb{Z}_m$ ($m \ge 2$):
$$(A_m, b_m, s_m, e_m) = (A \bmod m, b \bmod m, s \bmod m, e \bmod m)$$

El observador público proyectado evalúa el **ruido efectivo observable**:
$$e_{\text{efectivo}} = (b_m - A_m s_m) \bmod m$$

---

## 2. Derivación del Cociente de Wrapping $k$

En el cuerpo numérico no reducido $\mathbb{Z}$, la combinación lineal satisface:
$$x = A s + e = k q + b$$
donde $b \in [0, q-1]^m$ es el vector residuo y $k = \lfloor (A s + e) / q \rfloor \in \mathbb{Z}^m$ representa el vector entero de cocientes de desbordamiento o wrapping.

Proyectando esta relación módulo $m$:
$$b \equiv A s + e - k q \pmod m$$
Isolando el ruido efectivo percibido por el atacante:
$$e_{\text{efectivo}} = (b \bmod m - (A \bmod m)(s \bmod m)) \bmod m \equiv (e \bmod m - k (q \bmod m)) \pmod m$$

---

## 3. Separación entre Soporte Algebraico y Distribución Probabilística

Para comprender el mecanismo de uniformización, es crítico distinguir entre dos fenómenos independientes:

### Concepto A: Soporte Algebraico ($G(q,m) = \langle q \rangle \subseteq \mathbb{Z}_m$)
El término de envoltorio $-k (q \bmod m) \pmod m$ únicamente puede tomar valores contenidos en el subgrupo aditivo generado por $q$ dentro de $\mathbb{Z}_m$:
$$G(q,m) = \langle q \rangle = \{ k q \bmod m \mid k \in \mathbb{Z} \}$$
cuyo tamaño exacto es:
$$|G(q,m)| = \frac{m}{\gcd(q, m)}$$

- **Condición Necesaria**: $\gcd(q, m) = 1$ es la condición algebraica necesaria para que el subgrupo sea completo ($|G(q,m)| = m$), permitiendo que el término de envoltorio tenga soporte total sobre todas las clases de $\mathbb{Z}_m$.

### Concepto B: Distribución Probabilística ($P(k \bmod m)$)
La condición algebraicamente necesaria de soporte completo no garantiza por sí sola la mezcla uniforme; requiere además que las probabilidades $P(k \bmod m = r)$ estén distribuidas uniformemente sobre $\mathbb{Z}_m$.

---

## 4. Distribución Aproximada del Cociente de Wrapping (Análisis Asintótico)

Dado $x = A s + e$, como $s \sim U(\mathbb{Z}_q^n)$ y $A \sim U(\mathbb{Z}_q^{m_{\text{muestras}} \times n})$, la variable $x$ se distribuye como la suma de $n$ variables aleatorias independientes uniformes en $\mathbb{Z}_q$.

Por el Teorema del Límite Central, para $n \ge 2$, $x$ abarca un rango de valores de amplitud de orden $O(q \cdot \sqrt{n})$, que es sustancialmente mayor que el módulo $q$.

Cuando $x$ se extiende sobre un intervalo continuo amplio respecto a $q \cdot m$, la función escalón $k = \lfloor x / q \rfloor$ acumula bloques periódicos de tamaño $q$. Al tomar módulo $m$, la probabilidad de caer en cada residuo $r \in \{0, \dots, m-1\}$ se aproxima asintóticamente a:
$$\lim_{q \to \infty} P(k \bmod m = r) = \frac{1}{m}$$

Esta **aproximación asintótica** demuestra que conforme el módulo $q$ crece, la entropía del cociente de envoltorio satisface $H(k \bmod m) \to \log_2 m$ y la divergencia $KL(P(k \bmod m) \parallel U(\mathbb{Z}_m)) \to 0$.

---

## 5. Teorema de Uniformización Modular LWE

> **Teorema (Uniformización Modular LWE)**:
> Sea una instancia LWE sobre $\mathbb{Z}_q$ proyectada al anillo modular $\mathbb{Z}_m$. El ruido efectivo observable $e_{\text{efectivo}} = (b_m - A_m s_m) \bmod m$ es el resultado de la convolución circular discreta:
> $$P(e_{\text{efectivo}}) = P(e \bmod m) \circledast P(k q \bmod m)$$
>
> Si se cumplen las dos condiciones siguientes:
> 1. **Soporte Algebraico Completo**: $\gcd(q, m) = 1$ (por lo que el subgrupo generado es $\langle q \rangle = \mathbb{Z}_m$).
> 2. **Uniformidad del Envoltorio**: La distribución del cociente inducido $P(k \bmod m)$ es aproximadamente uniforme en $\mathbb{Z}_m$.
>
> **Entonces**, el ruido efectivo observable $P(e_{\text{efectivo}})$ es aproximadamente uniforme en $\mathbb{Z}_m$ ($P(e_{\text{efectivo}}) \approx U(\mathbb{Z}_m)$), **independientemente de la distribución original del error $e$**.

---

## 6. Demostración por Convolución Circular

Sea $P_e = P(e \bmod m)$ y $P_{kq} = P(k q \bmod m)$.
Puesto que $\gcd(q, m) = 1$, la transformación $r \mapsto (r q) \bmod m$ es una permutación biyectiva de $\mathbb{Z}_m$.
Si $P(k \bmod m) = U(\mathbb{Z}_m)$, entonces $P_{kq} = U(\mathbb{Z}_m)$, es decir, $P_{kq}[j] = 1/m$ para todo $j \in \mathbb{Z}_m$.

Calculando la convolución circular para cualquier residuo $r \in \mathbb{Z}_m$:
$$P(e_{\text{efectivo}})[r] = \sum_{j=0}^{m-1} P_e[j] \cdot P_{kq}[(r - j) \bmod m] = \sum_{j=0}^{m-1} P_e[j] \cdot \frac{1}{m} = \frac{1}{m} \sum_{j=0}^{m-1} P_e[j] = \frac{1}{m} \cdot 1 = \frac{1}{m}$$

Por lo tanto, $P(e_{\text{efectivo}}) \equiv U(\mathbb{Z}_m)$, completando la prueba.
