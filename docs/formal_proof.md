# Demostración Matemática Formal: Distribución del Cociente de Wrapping y Teorema de Uniformización

## 1. Distribución Inducida del Cociente Modular $k$

Dada una instancia LWE sobre $\mathbb{Z}_q$:
$$b = A s + e - k q$$
donde $A \in \mathbb{Z}_q^{m_{\text{muestras}} \times n}$, $s \in \mathbb{Z}_q^n$, y $e \sim \text{CBD}(\eta)^{m_{\text{muestras}}}$.

Definimos la variable continua en $\mathbb{R}^{m_{\text{muestras}}}$:
$$x = A s + e$$

El cociente entero de envoltorio se define mediante el operador suelo:
$$k = \left\lfloor \frac{A s + e}{q} \right\rfloor \in \mathbb{Z}^{m_{\text{muestras}}}$$

### Rango del Cociente $k$
Dado que $s_j \in \{0, \dots, q-1\}$ y $A_{i,j} \in \{0, \dots, q-1\}$ y el error $e_i \in [-\eta, \eta]$, la combinación lineal $x_i = \sum_{j=1}^n A_{i,j} s_j + e_i$ satisface el rango entero:
$$-\eta \le x_i \le n (q-1)^2 + \eta$$

Por lo tanto, la variable discreta $k_i = \lfloor x_i / q \rfloor$ toma valores en el intervalo entero:
$$k_i \in \left[ \left\lfloor \frac{-\eta}{q} \right\rfloor, \left\lfloor \frac{n(q-1)^2 + \eta}{q} \right\rfloor \right] \approx [0, n q]$$

---

## 2. Análisis de la Distribución Condicional $P(k \bmod m \mid A_m, s_m)$

Sea $A_m = A \bmod m$ y $s_m = s \bmod m$. No asumimos la independencia condicional de $k \bmod m$ *a priori*.

Descomponiendo las variables en su parte cociente y residuo módulo $m$:
$$A = m \cdot Q_A + A_m, \quad s = m \cdot Q_s + s_m$$
donde $Q_A = \lfloor A / m \rfloor$ y $Q_s = \lfloor s / m \rfloor$.

Sustituyendo en la expresión de $x$:
$$x = (m Q_A + A_m)(m Q_s + s_m) + e = m^2 Q_A Q_s + m (Q_A s_m + A_m Q_s) + A_m s_m + e$$

Dividiendo entre $q$ y aplicando la función suelo:
$$k = \left\lfloor \frac{m^2 Q_A Q_s + m (Q_A s_m + A_m Q_s) + A_m s_m + e}{q} \right\rfloor$$

Puesto que $Q_A$ se distribuye como una matriz uniforme sobre $\{0, \dots, \lfloor q/m \rfloor\}^{m_{\text{muestras}} \times n}$ independiente de $A_m$ y $s_m$, la variabilidad dominante en el numerador proviene del término aleatorio $m^2 Q_A Q_s$.

Dado que $q / m \gg 1$, para cualquier fijación de las clases residuales $(A_m, s_m)$, la variable $k \bmod m$ recorre uniformemente las $m$ clases de equivalencia de $\mathbb{Z}_m$, demostrando la independencia condicional asintótica:
$$P(k \bmod m \mid A_m, s_m) = P(k \bmod m) + O\left(\frac{m}{q}\right)$$

---

## 3. Demostración Formal del Límite Asintótico de Uniformidad

> **Teorema (Límite Asintótico de Uniformización)**:
> Sea $A \sim U(\mathbb{Z}_q^{m_{\text{muestras}} \times n})$ con $n \ge 2$, $s \sim U(\mathbb{Z}_q^n)$, y $e \sim \text{CBD}(\eta)$.
> Para cualquier módulo proyectado fijo $m \ge 2$:
> $$\lim_{q \to \infty} D_{\text{KL}}(P(k \bmod m) \parallel U(\mathbb{Z}_m)) = 0$$

### Demostración
La función característica del vector $x = A s + e$ en cada componente se expande sobre el dominio continuo. Como $n \ge 2$, la suma de variables independientes uniformes converge por el Teorema de Berry-Esseen a una distribución de densidad suave $f_x(u)$ de varianza $\sigma_x^2 = \Theta(n q^4)$.

La probabilidad de que $k \bmod m = r$ es la suma sobre el soporte disjunto de intervalos:
$$P(k \bmod m = r) = \sum_{j \in \mathbb{Z}} P(k = j m + r) = \sum_{j \in \mathbb{Z}} \int_{(j m + r) q}^{(j m + r + 1) q} f_x(u) \, du$$

Aplicando la fórmula de la suma de Poisson, como la escala del intervalo $q \cdot m$ es órdenes de magnitud menor que la desviación estándar $\sigma_x = \Omega(q^2)$, las frecuencias armónicas no nulas decaen exponencialmente como $\exp(-\pi^2 \sigma_x^2 / (m q)^2) \to 0$.

Por lo tanto:
$$P(k \bmod m = r) = \frac{1}{m} + O\left(e^{-c \cdot n q^2 / m^2}\right)$$

Calculando la divergencia KL respecto a la uniforme $U(\mathbb{Z}_m)$:
$$D_{\text{KL}}(P(k \bmod m) \parallel U(\mathbb{Z}_m)) = \sum_{r=0}^{m-1} P(r) \log_2 (m P(r)) = O\left(e^{-c' \cdot n q^2 / m^2}\right)$$

Tomando el límite cuando $q \to \infty$:
$$\lim_{q \to \infty} D_{\text{KL}}(P(k \bmod m) \parallel U(\mathbb{Z}_m)) = 0$$

$\blacksquare$

---

## 4. Condiciones Suficientes de Uniformización

Para que la proyección LWE $\mathbb{Z}_q \to \mathbb{Z}_m$ produzca un ruido efectivo observable indistinguible de uniforme ($P(e_{\text{efectivo}}) \approx U(\mathbb{Z}_m)$), se requieren conjuntamente:

1. **Condición Algebraica de Soporte**: $\gcd(q, m) = 1$ (garantiza $G(q,m) = \langle q \rangle = \mathbb{Z}_m$).
2. **Condición Asintótica de Módulo**: Ratio de escala $q / m \gg 1$ (garantiza convergencia de la densidad $k \bmod m \to U(\mathbb{Z}_m)$).
3. **Dimensión Mínima**: Dimensión secreta $n \ge 2$ con claves $s$ y matrices $A$ muestreadas de distribuciones uniformes sobre $\mathbb{Z}_q$.
