# Modeler de Transformaciones Reales en ML-KEM / Kyber (`transformations/kyber_transformations.py`)

## 1. Introducción y Contexto Criptográfico

En esquemas de criptografía basada en retículos sobre módulos (Module-LWE) como **ML-KEM (FIPS 203 / Kyber)**, el intercambio de claves y el cifrado no se realizan sobre coeficientes algebraicos puros en $\mathbb{Z}_q$, sino a través de representaciones serializadas, comprimidas y cuantizadas.

El módulo `transformations/kyber_transformations.py` implementa el modelo exacto de las operaciones a nivel de coeficientes y bytes especificadas en la norma FIPS 203.

---

## 2. Operaciones Modeladas

### 2.1 Compresión ($\text{Compress}_d$)
La función de compresión mapea un elemento $x \in \mathbb{Z}_q$ a $\mathbb{Z}_{2^d}$ reduciendo la precisión de los bits menos significativos:
$$\text{Compress}_d(x) = \left\lceil \frac{2^d}{q} \cdot (x \bmod q) \right\rfloor \bmod 2^d$$

En Python:
```python
def compress_q(x, q=3329, d=10):
    scale = (1 << d) / float(q)
    return np.round(scale * (x % q)).astype(int) % (1 << d)
```

### 2.2 Descompresión ($\text{Decompress}_d$)
La operación inversa aproxima el valor original en $\mathbb{Z}_q$ desde la representación comprimida de $d$ bits:
$$\text{Decompress}_d(y) = \left\lceil \frac{q}{2^d} \cdot y \right\rfloor \bmod q$$

```python
def decompress_q(y, q=3329, d=10):
    scale = float(q) / (1 << d)
    return np.round(scale * y).astype(int) % q
```

### 2.3 Reducción Modular Reales e Imprecisas
Evalúa la diferencia entre reducción modular matemáticamente exacta $x \bmod q$ e implementaciones con posibles desbordamientos o sesgos condicionales (ej. algoritmos imprecisos de Barrett o Montgomery):
- `mode="exact"`: $x \bmod q \in [0, q-1]$
- `mode="centered"`: $x \bmod q \in [-\lfloor q/2 \rfloor, \lfloor q/2 \rfloor]$
- `mode="biased"`: Simulación de asimetría por reducción imperfecta.

### 2.4 Serialización de Coeficientes (`coefficient_pack` / `coefficient_unpack`)
Los coeficientes de $d$ bits se empaquetan en flujos de bytes little-endian manteniendo alineación continua sin delimitadores.

### 2.5 Simulación de Redondeo Round-Trip (`simulate_kyber_rounding`)
Analiza el error intrínseco de redondeo introducido por la compresión y descompresión consecutivas:
$$\Delta = (\text{Decompress}_d(\text{Compress}_d(x)) - x) \bmod q$$

---

## 3. Métricas Estadísticas del Módulo

El módulo expone funciones de auditoría estadística:
- **Entropía de Shannon**: $H(X) = -\sum P(x) \log_2 P(x)$
- **Distancia Estadística (TVD)**: $\text{SD}(P, Q) = \frac{1}{2} \sum |P(x) - Q(x)|$
- **Divergencia KL**: $D_{\text{KL}}(P || Q) = \sum P(x) \log_2 \frac{P(x)}{Q(x)}$
- **Información Mutua**: $I(X; Y) = H(X) + H(Y) - H(X, Y)$
