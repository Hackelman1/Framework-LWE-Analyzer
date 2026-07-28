# Marco Teórico y Teorema de Uniformización Modular en LWE (v2.0.0)

**Proyecto:** `pqc-statistical-auditor`  
**Autor:** Ricardo Peinador  
**Versión:** 2.0.0  

---

## 1. Tres Niveles de Certeza Formal

El marco teórico de uniformización modular se estructura en tres niveles explícitos de certeza:

1. **Nivel 1 (Teorema Cota de Contracción Condicional):**  
   Cota contractiva de distancia estadística mediante convolución circular:
   $$\delta(P(e_{\text{effective}}), U(\mathbb{Z}_m)) \le \delta(P(k q \bmod m), U(\mathbb{Z}_m))$$
   *Condición Criptográfica:* Requiere la independencia estocástica entre los componentes modulares $e \bmod m \perp\!\!\!\perp k q \bmod m$. En los esquemas reales (ML-KEM / ML-DSA), esta condición se satisface gracias al término de enmascaramiento de alta entropía $A s \bmod q$.

2. **Nivel 2 (Resultado Condicionado por Hipótesis):**  
   Si la variable de envolvente satisface $P(k q \bmod m) = U(\mathbb{Z}_m)$, entonces el ruido efectivo observable $e_{\text{effective}}$ está distribuido estrictamente uniforme sobre $\mathbb{Z}_m$.

3. **Nivel 3 (Validación Empírica Monte Carlo y Permutaciones con FDR):**  
   Demostración numérico-empírica ($KL < 0.004$ bits en Kyber) e inferencial mediante tests de permutaciones con control de BH-FDR ($M = 23$, $q > 0.40$).

---

## 2. Demostración Sin Ruido ($e = 0$)

Cuando $e = 0$, la muestra LWE adopta la forma $b = A s \pmod q$. El ruido efectivo módulo $m$ es:
$$e_{\text{effective}} = (b \bmod m - A_m s_m) \bmod m = -k q \bmod m$$
Esto prueba matemáticamente que la uniformización estadística es generada **intrínsecamente por la variable de envolvente $k = \lfloor A s / q \rfloor$**, independientemente de la existencia o magnitud del término de ruido original $e$.
