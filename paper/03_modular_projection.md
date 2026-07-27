# 03. La Proyección Modular LWE Z_q -> Z_m

## Definición de la Proyección
Consideremos la proyección proyectiva homomórfica $\pi_m: \mathbb{Z}_q \to \mathbb{Z}_m$ definida por el operador módulo $m$:
$$A_m = A \bmod m, \quad b_m = b \bmod m, \quad s_m = s \bmod m$$

## Ruido Efectivo Observable
Un observador público calcula la combinación residual proyectada:
$$e_{\text{efectivo}} = (b_m - A_m s_m) \bmod m$$

En el cuerpo entero $\mathbb{Z}$, la combinación satisface la relación exacta:
$$A s + e = k q + b$$
donde $k = \lfloor (A s + e)/q \rfloor \in \mathbb{Z}^{m_{\text{muestras}}}$ es el cociente de envoltorio.

Proyectando módulo $m$:
$$e_{\text{efectivo}} \equiv (e \bmod m - k (q \bmod m)) \pmod m$$
Demostrando que el ruido observable es la combinación del ruido reducido $e \bmod m$ y la variable de envoltorio modulada $-k (q \bmod m) \pmod m$.
