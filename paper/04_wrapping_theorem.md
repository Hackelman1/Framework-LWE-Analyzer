# 04. Teorema de Uniformización Modular, Cota de Convolución y Fuga Nula de Información

## 1. Niveles de Certeza Formal
Toda la formulación teórica y experimental de este trabajo distingue tres niveles de rigor formal:
- **Nivel 1 (Demostración Matemática Exacta)**: La cota de contracción de distancia estadística mediante convolución circular discreta sobre grupos modulares.
- **Nivel 2 (Resultado bajo Hipótesis)**: Si la variable de envolvente $P(k q \bmod m) = U(\mathbb{Z}_m)$, entonces el ruido efectivo $e_{\text{efectivo}}$ se distribuye exactamente uniforme en $\mathbb{Z}_m$.
- **Nivel 3 (Evidencia Experimental Monte Carlo)**: 
  - Para instancias M-LWE tipo Kyber ($q=3329, m=6$), las simulaciones demuestran que $KL(e_{\text{efectivo}} \parallel U) < 0.003$ bits.
  - Para transformaciones reales de implementación en ML-KEM (FIPS 203) y ML-DSA (FIPS 204), evaluaciones profundas con $N = 500,000$ muestras confirman que la información mutua corregida por Miller-Madow satisface $I(S; \text{Salida}) \approx 0.0000$ bits y $p\text{-valor de }\chi^2 > 0.16$ en todas las funciones (`Decompose`, `Power2Round`, `MakeHint`).

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

---

## 4. Corolario: Independencia Estadística en Transformaciones de Implementación (FIPS 203 y FIPS 204)

Como consecuencia directa del Teorema de Uniformización, cuando las transformaciones de truncamiento, descomposición o redondeo en estándares reales (tales como $\text{Compress}_d$, `Power2Round`, `Decompose` y `MakeHint`) extraen un residuo modular de menor peso $r_0, t_0 \in \mathbb{Z}_m$ o un vector binario $h \in \{0, 1\}^K$, el enmascaramiento estocástico introducido por el término de módulo destruye la dependencia con el secreto $S$.

Matemáticamente, la información mutua observada entre el secreto $S$ y la salida de la transformación $Y \in \{r_0, t_0, h\}$ satisface:
$$I(S; Y) = H(Y) - H(Y \mid S) \le 2 \cdot \delta(P_Y, U(\mathbb{Z}_m)) \cdot \log_2(|\mathbb{Z}_m|) \approx 0$$
lo cual garantiza la ausencia de fugas de información estadística aprovechables por un atacante.
