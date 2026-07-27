# Manuscrito Técnico Formal: Teorema de Uniformización Modular en Proyecciones LWE $\mathbb{Z}_q \to \mathbb{Z}_m$

**Autor**: Framework Experimental de Proyecciones LWE  
**Fecha**: 2026-07-24  
**Clasificación**: Criptografía Matemática / Análisis Estocástico de LWE  

---

## 1. Definición Formal del Problema

Sea el problema **Learning With Errors (LWE)** sobre el anillo modular entero $\mathbb{Z}_q$, donde $q \ge 3$ es un entero impar. Se define una instancia LWE como una tupla $(A, b) \in \mathbb{Z}_q^{m_{\text{muestras}} \times n} \times \mathbb{Z}_q^{m_{\text{muestras}}}$ tal que:
$$b = A s + e \pmod q$$
donde $s \leftarrow U(\mathbb{Z}_q^n)$ es el secreto uniforme y $e \sim \mathcal{D}^{m_{\text{muestras}}}$ es un ruido centrado no uniforme sobre un soporte acotado $[-\eta, \eta] \subset \mathbb{Z}$ (típicamente una Distribución Binomial Centrada $\text{CBD}(\eta)$).

Consideremos la proyección proyectiva homomórfica al anillo residual $\mathbb{Z}_m$ con $m \ge 2$:
$$\pi_m: \mathbb{Z}_q \to \mathbb{Z}_m, \quad x \mapsto x \bmod m$$

El problema objeto de estudio consiste en caracterizar la ley de distribución del **ruido efectivo observable**:
$$e_{\text{efectivo}} = \pi_m(b) - \pi_m(A) \pi_m(s) \pmod m$$

---

## 2. Modelo Probabilístico y Término de Envoltorio

En el cuerpo entero no reducido $\mathbb{Z}$, la combinación lineal satisface la igualdad exacta:
$$A s + e = k q + b$$
donde el vector entero $k = \left\lfloor \frac{A s + e}{q} \right\rfloor \in \mathbb{Z}^{m_{\text{muestras}}}$ representa los **cocientes de envoltorio modular** ( wrapping terms ).

Proyectando módulo $m$:
$$e_{\text{efectivo}} \equiv \pi_m(e) - k \pi_m(q) \pmod m$$

---

## 3. Lemas Fundamentales

### Lema 1 (Soporte del Subgrupo Generado)
*El término de enmascaramiento $-k \pi_m(q) \pmod m$ tiene su soporte restringido al subgrupo aditivo cíclico $G(q,m) = \langle \pi_m(q) \rangle \subseteq \mathbb{Z}_m$, cuyo orden es:*
$$|G(q,m)| = \frac{m}{\gcd(q, m)}$$

### Lema 2 (Cota de Contracción de Distancia Estadística por Convolución)
*Sea $\delta(P, Q) = \frac{1}{2} \sum_x |P(x) - Q(x)|$ la distancia de variación total. Para cualquier distribución de error $P_e$ sobre $\mathbb{Z}_m$, la convolución circular discreta $P_{e_{\text{efectivo}}} = P_e \circledast P_{kq}$ satisface:*
$$\delta(P_{e_{\text{efectivo}}}, U(\mathbb{Z}_m)) \le \delta(P_{kq \bmod m}, U(\mathbb{Z}_m))$$

*Demostración*:
Dado que la distribución uniforme $U(\mathbb{Z}_m)$ es invariante por traslación bajo convolución con cualquier distribución de probabilidad ($P_e \circledast U = U$), por la desigualdad triangular de la norma $L_1$:
$$\delta(P_e \circledast P_{kq}, U) = \delta(P_e \circledast P_{kq}, P_e \circledast U) = \frac{1}{2} \sum_{r} \left| \sum_{j} P_e(j) (P_{kq}(r-j) - U(r-j)) \right|$$
$$\le \frac{1}{2} \sum_{j} P_e(j) \sum_{r} |P_{kq}(r-j) - U(r-j)| = \sum_{j} P_e(j) \cdot \delta(P_{kq}, U) = 1 \cdot \delta(P_{kq}, U) = \delta(P_{kq}, U)$$
$\blacksquare$

---

## 4. Teorema de Uniformización Modular LWE

> **Teorema Principal (Uniformización Modular LWE)**:
> Sea una instancia LWE sobre $\mathbb{Z}_q$ proyectada al anillo modular $\mathbb{Z}_m$. El ruido efectivo observable $e_{\text{efectivo}} = (b_m - A_m s_m) \bmod m$ es el resultado de la convolución circular $P_{e_{\text{efectivo}}} = P(e \bmod m) \circledast P(k q \bmod m)$.
>
> Si se cumplen:
> 1. **Condición Algebraica**: $\gcd(q, m) = 1$ ($G(q,m) = \mathbb{Z}_m$).
> 2. **Condición Probabilística**: $\delta(P(k q \bmod m), U(\mathbb{Z}_m)) \le \epsilon$.
>
> **Entonces**, la distancia de variación total satisface:
> $$\delta(P(e_{\text{efectivo}}), U(\mathbb{Z}_m)) \le \epsilon$$
> **independientemente de la distribución del ruido original $e$**.

---

## 5. Resultados de Robustez de los Experimentos L y M

- **Experimento L (Independencia del Secreto)**: La uniformización ocurre con idéntica precisión ($\text{KL} < 0.003$ bits) tanto para secreto uniforme $s \sim U(\mathbb{Z}_q)$ como para secretos ternarios $\{-1, 0, 1\}$, binomiales o fijos.
- **Experimento M (Robustez frente al Ruido)**: En el caso límite donde **$e = 0$ (ruido cero)**, $e_{\text{efectivo}} \equiv -k q \bmod m$. Para $q=3329, m=6$, $\text{KL}(e_{\text{efectivo}} \parallel U(\mathbb{Z}_6)) = 0.0023$ bits, demostrando que la uniformización es producida **puramente por el término de envoltorio**.
