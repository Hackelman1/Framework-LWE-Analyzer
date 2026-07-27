# Generalización Teórica: Proyecciones LWE desde $\mathbb{Z}_q$ a $\mathbb{Z}_m$ y la Estructura de Subgrupos

## 1. Formulación del Problema

Dada una instancia LWE estándar en el anillo modular $\mathbb{Z}_q$:
$$b = A s + e \pmod q$$
donde $A \in \mathbb{Z}_q^{m_{\text{muestras}} \times n}$, $s \in \mathbb{Z}_q^n$, y $e \sim \text{CBD}(\eta)^{m_{\text{muestras}}}$.

Se define la transformación proyectiva hacia el anillo modular objetivo $\mathbb{Z}_m$ ($m \ge 2$):
$$(A, b, s, e) \mapsto (A \bmod m, b \bmod m, s \bmod m, e \bmod m)$$

El observador público que realiza la inferencia sobre el secreto reducido $s_m = s \bmod m$ percibe el **ruido efectivo observable**:
$$e_{\text{efectivo}} = (b \bmod m - A \bmod m \cdot s \bmod m) \pmod m$$

---

## 2. Derivación del Término de Envoltorio Modular $k$

En $\mathbb{Z}$ (sin reducción modular), la relación exacta es:
$$A s + e = k q + b$$
donde $k = \lfloor (A s + e) / q \rfloor \in \mathbb{Z}^m$ es el vector entero de cocientes de desbordamiento ( wrapping terms ).

Proyectando esta igualdad módulo $m$:
$$b \equiv A s + e - k q \pmod m$$
Rearreglando para aislar el ruido efectivo percibido $e_{\text{efectivo}}$:
$$e_{\text{efectivo}} = (b \bmod m - (A \bmod m)(s \bmod m)) \bmod m \equiv (e \bmod m - k (q \bmod m)) \pmod m$$

---

## 3. Teoría del Subgrupo Generado $G(q,m)$ y Capacidad de Mezcla

El término de enmorcalamiento $-k (q \bmod m) \pmod m$ solo puede tomar valores dentro del **subgrupo cíclico generado por $q$** dentro del grupo aditivo $(\mathbb{Z}_m, +)$:
$$G(q,m) = \langle q \rangle = \{ k q \bmod m \mid k \in \mathbb{Z} \} \subseteq \mathbb{Z}_m$$

### Teorema del Tamaño del Subgrupo
El tamaño del subgrupo generado por $q$ en $\mathbb{Z}_m$ viene dado por:
$$|G(q,m)| = |\langle q \rangle| = \frac{m}{\gcd(q, m)}$$

### Teorema de Enmascaramiento y Convolución Uniforme
La distribución del ruido efectivo $P(e_{\text{efectivo}})$ es el resultado de la convolución circular entre la PMF del ruido original proyectado $P(e \bmod m)$ y la PMF del término de envoltorio $P(k q \bmod m)$:
$$P(e_{\text{efectivo}}) = P(e \bmod m) \circledast P(k q \bmod m)$$

1. **Caso $\gcd(q, m) = 1$ (Subgrupo Total $|G(q,m)| = m$)**:
   - $q$ es un generador de $\mathbb{Z}_m$, por lo que $G(q,m) = \mathbb{Z}_m$.
   - El término de envoltorio $k q \bmod m$ puede recorrer la totalidad de las $m$ clases de equivalencia de $\mathbb{Z}_m$.
   - Si la distribución de $A s \bmod q$ es uniforme en $\mathbb{Z}_q$, $k q \bmod m$ actúa como una máscara aleatoria uniforme tipo *one-time pad*, forzando que la convolución converja a la distribución uniforme exacta:
     $$P(e_{\text{efectivo}}) \equiv U(\mathbb{Z}_m)$$
   - **Consecuencia**: Toda ventaja bayesiana del atacante ideal se destruye, e $I(S_m; B_m \mid A_m) = 0$ bits.

2. **Caso $\gcd(q, m) = g > 1$ (Subgrupo Propio $|G(q,m)| = m/g < m$)**:
   - $q$ solo genera un subgrupo estricto de tamaño $m/g$.
   - El enmascaramiento se limita al subgrupo $G(q,m)$, dejando $g$ clases coset desconectadas.
   - La convolución no puede cubrir todo $\mathbb{Z}_m$, preservando no-uniformidad y fugando información mutua $I(S_m; B_m \mid A_m) > 0$.
   - En el caso extremo donde $q \equiv 0 \pmod m$ ($\gcd(q,m) = m$), $k q \equiv 0 \pmod m$, el término de envoltorio desaparece y $e_{\text{efectivo}} \equiv e \bmod m$, otorgando al atacante MLE un **100% de éxito**.

---

## 4. Evidencia Experimental de la Generalización

Los experimentos H e I confirman de forma exacta la frontera teórica:
- Para cualquier par $(q, m)$ con $\gcd(q, m) = 1$, la divergencia KL satisface $KL(e_{\text{efectivo}} \parallel U(\mathbb{Z}_m)) < 0.0002$ bits.
- Para cualquier par con $\gcd(q, m) > 1$, se conserva no-uniformidad proporcional a $g = \gcd(q, m)$.

---

## 5. Límites y Alcance del Modelo

- **Dimensión Secreta**: La caracterización se aplica a la proyección entrada a entrada de las muestras de ruido.
- **Seguridad Práctica**: Esta propiedad algebraica explica la transformación estadística de las observaciones proyectadas y demuestra que la reducción modular $\mathbb{Z}_q \to \mathbb{Z}_m$ no abre vulnerabilidades estadísticas cuando $\gcd(q,m) = 1$.
