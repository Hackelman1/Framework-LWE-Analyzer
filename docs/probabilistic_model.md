# Modelo Probabilístico Completo de Proyecciones LWE

Este documento formaliza el espacio de probabilidad $(\Omega, \mathcal{F}, P)$ y el grafo acíclico dirigido (DAG) de dependencias estocásticas para la proyección de instancias LWE desde un anillo modular $\mathbb{Z}_q$ hacia un anillo residual $\mathbb{Z}_m$.

---

## 1. Definición del Espacio de Probabilidad

Definimos el espacio muestral del sistema LWE como el producto cartesiano:
$$\Omega = \mathbb{Z}_q^{m_{\text{muestras}} \times n} \times \mathbb{Z}_q^n \times [-\eta, \eta]^{m_{\text{muestras}}}$$

Donde los eventos elementales son las tuplas de la forma:
$$\omega = (A, s, e) \in \Omega$$

Asumimos la medida de probabilidad producto $P = P_A \otimes P_s \otimes P_e$, lo que garantiza la **independencia estocástica a priori** de las variables fundamentales:
$$A \perp s \perp e$$

---

## 2. Clasificación de las Variables Aleatorias del Sistema

| Variable Aleatoria | Dominio / Espacio de Estados | Tipo de Variable | Distribución de Probabilidad | Naturaleza de la Variable |
|:------------------|:----------------------------|:-----------------|:-----------------------------|:--------------------------|
| **$A$** | $\mathbb{Z}_q^{m_{\text{muestras}} \times n}$ | Fundamental | Uniforme $U(\mathbb{Z}_q^{m_{\text{muestras}} \times n})$ | Independiente |
| **$s$** | $\mathbb{Z}_q^n$ | Fundamental | Uniforme $U(\mathbb{Z}_q^n)$ (o $\text{CBD}(\eta_s)$ / Ternario) | Independiente |
| **$e$** | $[-\eta, \eta]^{m_{\text{muestras}}}$ | Fundamental | Centrada $\text{CBD}(\eta)$ | Independiente |
| **$y = A s + e$** | $\mathbb{Z}^{m_{\text{muestras}}}$ | Derivada | Convolución $A s + e$ en $\mathbb{R}$ | Dependiente de $(A, s, e)$ |
| **$b = y \bmod q$** | $\mathbb{Z}_q^{m_{\text{muestras}}}$ | Derivada | Casi-uniforme en $\mathbb{Z}_q$ | Dependiente de $(A, s, e)$ |
| **$k = \lfloor y / q \rfloor$** | $\mathbb{Z}^{m_{\text{muestras}}}$ | Derivada | Cociente de envoltorio discreto | Dependiente de $(A, s, e)$ |
| **$s_m = s \bmod m$** | $\mathbb{Z}_m^n$ | Proyectada | Uniforme en $\mathbb{Z}_m^n$ (si $\gcd(q,m)=1$) | Proyección determinista de $s$ |
| **$A_m = A \bmod m$** | $\mathbb{Z}_m^{m_{\text{muestras}} \times n}$ | Proyectada | Uniforme en $\mathbb{Z}_m^{m_{\text{muestras}} \times n}$ | Proyección determinista de $A$ |
| **$e_{\text{efectivo}}$** | $\mathbb{Z}_m^{m_{\text{muestras}}}$ | Observable | $P(e_{\text{efectivo}}) = P(e_m) \circledast P(k q \bmod m)$ | Dependiente de $(e_m, k)$ |

---

## 3. Grafo Causal y Factorización de la Densidad Conjunta

```
       ┌───┐            ┌───┐           ┌───┐
       │ A │            │ s │           │ e │
       └───┘            └───┘           └───┘
         │                │               │
         └───────┬────────┘               │
                 ▼                        │
          y = A * s + e ◄─────────────────┘
                 │
         ┌───────┴───────┐
         ▼               ▼
   b = y mod q     k = floor(y / q)
         │               │
         ▼               ▼
      b mod m        k mod m
         │               │
         └───────┬───────┘
                 ▼
     e_eff = (b_m - A_m * s_m) mod m
```

La densidad conjunta del sistema proyectado se factoriza exactamente como:
$$P(A_m, s_m, e_m, k_m) = P(A_m) \cdot P(s_m) \cdot P(e_m) \cdot P(k_m \mid A_m, s_m, e_m)$$

Cuando el módulo $q$ es sustancialmente mayor que $m$ ($q / m \gg 1$), las fluctuaciones del envoltorio $k_m = k \bmod m$ son asintóticamente independientes de las clases residuales $(A_m, s_m)$, lo que permite simplificar la densidad marginal del ruido efectivo observable:
$$P(e_{\text{efectivo}} \bmod m) = P(e \bmod m) \circledast P(k q \bmod m)$$

---

## 4. Rigor Terminológico

Para mantener la máxima precisión matemática y evitar saltos lógicos:
1. **Resultados Demostrados**: Exclusivamente las deducciones algebraicas derivadas de la teoría de subgrupos cíclicos $G(q,m) = \langle q \rangle \subseteq \mathbb{Z}_m$ y el Teorema de Convolución Circular.
2. **Resultados Asintóticos**: El límite $\lim_{q \to \infty} KL(P(k \bmod m) \parallel U) = 0$ bajo la hipótesis de variables continuas continuadas.
3. **Evidencia Empírica**: Las estimaciones de Información Mutua $I(k_m ; s_m)$ y tasas de éxito MLE obtenidas mediante muestreo estocástico Monte Carlo.
