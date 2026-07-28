# 03. La Proyección Modular LWE $\mathbb{Z}_q \to \mathbb{Z}_m$ y Descomposiciones Generalizadas

## Definición de la Proyección Modular Lineal
Consideremos la proyección homomórfica $\pi_m: \mathbb{Z}_q \to \mathbb{Z}_m$ definida por el operador módulo $m$:
$$A_m = A \bmod m, \quad b_m = b \bmod m, \quad s_m = s \bmod m$$

## Ruido Efectivo Observable
Un observador público calcula la combinación residual proyectada:
$$e_{\text{efectivo}} = (b_m - A_m s_m) \bmod m$$

En los enteros $\mathbb{Z}$, la combinación de la muestra M-LWE satisface la relación exacta:
$$A s + e = k q + b$$
donde $k = \lfloor (A s + e)/q \rfloor \in \mathbb{Z}^{m_{\text{muestras}}}$ es el término de envolvente modular (cociente entero).

Proyectando módulo $m$:
$$e_{\text{efectivo}} \equiv (e \bmod m - k (q \bmod m)) \pmod m$$
Esto demuestra que el ruido observable en proyecciones modulares lineales es la combinación (vía convolución discreta) del ruido original reducido $e \bmod m$ y la variable de envolvente modulada $-k (q \bmod m) \pmod m$.

## Generalización a Transformaciones de Implementación (ML-KEM / ML-DSA)
En los estándares reales FIPS 203 y FIPS 204, las proyecciones no solo ocurren mediante reducciones lineales modulares $m$, sino a través de operadores de descomposición no lineal y truncamiento de bits:
1. **Truncamiento de Clave Pública (`Power2Round`)**: Mapea $t \in \mathbb{Z}_q$ a $(t_1, t_0)$ donde el residuo proyectado $t_0 = t \bmod 2^d \in [-2^{d-1}+1, 2^{d-1}]$ actúa como el ruido efectivo de compresión.
2. **Descomposición de Compromiso (`Decompose`)**: Mapea $r \in \mathbb{Z}_q$ a $(r_1, r_0)$ con $r_0 \in [-\gamma_2, \gamma_2]$, aislando la parte baja proyectada.
3. **Pistas de Acarreo (`MakeHint`)**: Modula la discrepancia entre las proyecciones de partes altas $\text{HighBits}(z_0 + z_1)$ y $\text{HighBits}(z_1)$, representando una proyección booleana discreta del acarreo modular.
