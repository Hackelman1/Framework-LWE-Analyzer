# 04. Teorema de Uniformización Modular y Cota de Convolución

## 1. Niveles de Certeza Formal
Toda la formulación teórica de este trabajo distingue tres niveles de rigor:
- **Nivel 1 (Demostración Matemática Exacta)**: La cota de contracción de distancia estadística por convolución circular discreta.
- **Nivel 2 (Resultado bajo Hipótesis)**: Si la variable de envoltorio $P(k q \bmod m) = U(\mathbb{Z}_m)$, entonces el ruido efectivo $e_{\text{efectivo}}$ es uniforme en $\mathbb{Z}_m$.
- **Nivel 3 (Evidencia Experimental Monte Carlo)**: Para instancias tipo Kyber ($q=3329, m=6$), las simulaciones demuestran que $KL(e_{\text{efectivo}} \parallel U) < 0.003$ bits.

---

## 2. Teorema Principal
Sea una instancia LWE sobre $\mathbb{Z}_q$ proyectada a $\mathbb{Z}_m$. La densidad del ruido efectivo observable satisface la convolución circular discreta:
$$P(e_{\text{efectivo}}) = P(e \bmod m) \circledast P(k q \bmod m)$$

### Teorema (Cota de Contracción de Distancia Estadística)
Para cualquier distribución de error $P_e$ sobre $\mathbb{Z}_m$, la convolución circular discreta $P_{e_{\text{efectivo}}} = P_e \circledast P_{kq}$ satisface:
$$\delta(P_{e_{\text{efectivo}}}, U(\mathbb{Z}_m)) \le \delta(P_{kq \bmod m}, U(\mathbb{Z}_m))$$

*Demostración*:
Como la distribución uniforme $U(\mathbb{Z}_m)$ es invariante por traslación bajo convolución con cualquier medida de probabilidad ($P_e \circledast U = U$), por la desigualdad triangular de la norma $L_1$:
$$\delta(P_e \circledast P_{kq}, U) = \delta(P_e \circledast P_{kq}, P_e \circledast U) \le \sum_j P_e(j) \cdot \delta(P_{kq}, U) = \delta(P_{kq}, U)$$
$\blacksquare$

---

## 3. Uniformización Independiente del Ruido (Caso $e = 0$)

Consideremos el caso límite donde la instancia LWE **carece de ruido original ($e = 0$)**:
$$b = A s \pmod q$$

Proyectando módulo $m$:
$$b_m = (A_m s_m - k q) \bmod m \implies e_{\text{efectivo}} = (b_m - A_m s_m) \bmod m \equiv -k q \pmod m$$

Por lo tanto:
$$P(e_{\text{efectivo}}) = P(k q \bmod m)$$

Si $\gcd(q, m) = 1$ y $q / m \gg 1$, $P(k q \bmod m) \approx U(\mathbb{Z}_m)$, por lo que:
$$P(e_{\text{efectivo}}) \approx U(\mathbb{Z}_m)$$

**Conclusión**: La uniformización del ruido efectivo **no depende de la presencia ni de la forma de la distribución del ruido $e$**, sino que es una propiedad emergente pura de la máscara estocástica del envoltorio modular $k q \bmod m$.
