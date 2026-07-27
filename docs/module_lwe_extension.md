# Extensión Teórica a Module-LWE y Anillos de Polinomios

## 1. De LWE a Module-LWE

En el problema LWE escalar clásico, las muestras son vectores $(A, b) \in \mathbb{Z}_q^{m \times n} \times \mathbb{Z}_q^m$.

En **Module-LWE**, el álgebra escalar sobre $\mathbb{Z}_q$ se sustituye por el anillo de polinomios cociente:
$$R_q = \frac{\mathbb{Z}_q[x]}{\langle x^N + 1 \rangle}$$

Donde $N = 256$ es una potencia de dos. Las observaciones adoptan la estructura matricial polinómica:
$$b(x) = A(x) \cdot s(x) + e(x) \pmod q$$
donde $A(x) \in R_q^{k \times k}$, $s(x) \in R_q^k$, y $e(x) \in R_q^k$ son vectores de polinomios de grado a lo sumo $N-1$.

---

## 2. Proyección de Coeficientes y Anillo Objetivo $R_m$

Definimos la proyección modular sobre el anillo proyectado $R_m = \mathbb{Z}_m[x] / \langle x^N + 1 \rangle$:
$$\pi_m: R_q \to R_m, \quad a(x) = \sum_{i=0}^{N-1} a_i x^i \mapsto \sum_{i=0}^{N-1} (a_i \bmod m) x^i$$

El ruido efectivo polinómico por componente es:
$$e_{\text{efectivo}, i}(x) = (b_{m, i}(x) - (A_m \cdot s_m)_i(x)) \bmod m$$

Como cada coeficientes $a_i$ se somete a la convolución negacíclica sobre $\mathbb{Z}_m$, el término de envoltorio actúa coeficiente a coeficiente sobre las $N \cdot k$ componentes de las muestras LWE de módulo, heredando idénticamente el Teorema de Uniformización Modular LWE.
