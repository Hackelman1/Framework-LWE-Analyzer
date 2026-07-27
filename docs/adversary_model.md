# Modelo Criptográfico de Adversario y Capacidades del Atacante

Este documento define de forma explícita las capacidades, conocimiento y restricciones del modelo de adversario considerado en el **Framework de Evaluación de Proyecciones LWE**.

---

## 1. Información Disponible para el Atacante

### Lo que el Atacante CONOCE ($\mathcal{K}$):
1. **Parámetros del Anillo**: Módulo primario $q$, módulo proyectado $m$, dimensión $n$ y parámetro de ruido $\eta$.
2. **Distribuciones Teóricas Prioris**: Distribución del secreto $s$ (ej. $U(\mathbb{Z}_q)$) y distribución del ruido original $e \sim \text{CBD}(\eta)$.
3. **Observaciones Públicas Proyectadas**: La matriz proyectada $A_m = A \bmod m$ y el vector de muestras proyectado $b_m = b \bmod m$.
4. **Distribución del Ruido Efectivo Real**: La PMF empírica o teórica del ruido efectivo $e_{\text{efectivo}} = (b_m - A_m s_m) \bmod m$.

### Lo que el Atacante NO CONOCE ($\mathcal{U}$):
1. **El Secreto Verdadero**: Ni el secreto original $s \in \mathbb{Z}_q^n$ ni su proyección $s_m = s \bmod m$.
2. **El Ruido Interno no Reducido**: El vector de error original $e \in \mathbb{Z}^{m_{\text{muestras}}}$.
3. **El Cociente de Envoltorio**: El vector entero $k = \lfloor (A s + e)/q \rfloor \in \mathbb{Z}^{m_{\text{muestras}}}$ ni su reducción $k \bmod m$.

---

## 2. Taxonomía de Atacantes Evaluados

### 1. Atacante Ingenuo (Naive Attacker)
- **Definición**: Atacante que asume erróneamente que el ruido observable en la proyección mantiene la distribución de probabilidad del ruido original reducida $P(e \bmod m)$.
- **Verosimilitud**: $L_{\text{ingenuo}}(s') = \prod_{i=1}^{m_{\text{muestras}}} P_{\text{CBD}}((b_{m,i} - A_{m,i} s') \bmod m)$.
- **Resultado**: Falla de forma sistemática con Log-Likelihood Ratio ($LLR$) fuertemente negativo, ya que la distribución real difiere de la CBD.

### 2. Atacante Ideal (Ideal Attacker)
- **Definición**: Atacante óptimo Bayesiano que conoce la distribución real del ruido efectivo $P(e_{\text{efectivo}})$.
- **Verosimilitud**: $L_{\text{ideal}}(s') = \prod_{i=1}^{m_{\text{muestras}}} P_{e_{\text{efectivo}}}((b_{m,i} - A_{m,i} s') \bmod m)$.
- **Resultado**: Cuando $\gcd(q, m) = 1$, $P(e_{\text{efectivo}}) \equiv U(\mathbb{Z}_m)$, por lo que $L_{\text{ideal}}(s') = (1/m)^{m_{\text{muestras}}}$ constante para todos los candidatos $s'$. Tasa de éxito: $1/m^n$ (idéntica a la adivinación uniforme al azar).

### 3. Atacante Bayesiano Completo de Entropía A Posteriori
- **Definición**: Atacante que evalúa la distribución posterior exacta $P(s_m \mid A_m, b_m) = \frac{P(b_m \mid A_m, s_m) P(s_m)}{\sum_{s'} P(b_m \mid A_m, s') P(s')}$.
- **Resultado**: Confirma que la entropía a posteriori $H(S_m \mid A_m, B_m)$ es igual a la previa $H(S_m)$, registrando una ganancia de información mutua de $0.0000$ bits.
