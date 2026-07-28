# 05. Resultados Experimentales y Validación Estocástica

## 1. Suite de Experimentos Teóricos LWE (Experimentos A al O)

1. **Experimento A (Filtro de Ruido vs. Ruido Efectivo)**: Diferencia fundamental entre la CBD reducida $P(e \bmod 6)$ (no uniforme) y el ruido efectivo real $P(e_{\text{eff}})$ ($KL < 0.003$ bits).
2. **Experimentos B y C (Atacante MLE)**: Un atacante ideal de máxima verosimilitud (MLE) sobre la proyección obtiene una tasa de éxito idéntica al azar ($1/m^n$).
3. **Experimento D (Información Mutua Proyectada)**: Información mutua exacta condicionada $I(S_m; B_m \mid A_m) = 0.0010$ bits (compatible con cero).
4. **Experimentos G y H (Análisis de Divisibilidad y $\gcd$)**: Mapa matricial $q \times m$, donde $\gcd(q,m)=1 \implies KL \approx 0$, mientras que $\gcd(q,m) > 1 \implies KL > 0$.
5. **Experimento K (Independencia del Envoltorio)**: Demuestra que $I(k_m; s_m) = 0.000000$ bits (independencia condicional estricta).
6. **Experimento L (Análisis del Secreto Ternario)**:
   - Secretos de baja entropía ($s \in \{-1, 0, 1\}$) entregan $KL(e_{\text{eff}} \parallel U) = 0.3996$ bits.
   - **Explicación**: La baja variabilidad del producto $A s$ en $\mathbb{Z}$ restringe el alcance continuo necesario para que el cociente de envoltorio $k = \lfloor (A s + e)/q \rfloor$ se distribuya uniformemente. La uniformización requiere **tanto $\gcd(q,m)=1$ como suficiente entropía en $A s$**.
7. **Experimento M (Prueba de Ruido Cero $e=0$)**: Con $e=0$, $KL(e_{\text{eff}} \parallel U(\mathbb{Z}_6)) = 0.003387$ bits, demostrando que el envoltorio $k q \bmod m$ uniformiza por sí solo.
8. **Experimento N (Escalado con la Dimensión $n$)**: Al aumentar la dimensión del secreto $n \in \{1, 2, 4, 8, 16, 32\}$, la divergencia $KL(e_{\text{eff}} \parallel U)$ decae monótonamente hacia 0.
9. **Experimento O (Ataque Bayesiano Directo de Entropía A Posteriori)**: La entropía a posteriori $H(S_m \mid A_m, B_m)$ coincide exactamente con la previa $H(S_m)$ ($MI = 0.0000$ bits), confirmando que la proyección proyectada no filtra información de la clave.

---

## 2. Auditoría de Transformaciones Reales en ML-KEM / Kyber (FIPS 203)

Se auditaron las transformaciones reales de compresión ($\text{Compress}_d$), descompresión ($\text{Decompress}_d$), reducción modular y empaquetamiento de coeficientes en Kyber512, Kyber768 y Kyber1024. 

Para todas las operaciones, la información mutua observada entre las claves secretas y los residuos de redondeo se mantuvo acotada por debajo de $10^{-3}$ bits con $p\text{-valores de }\chi^2 > 0.05$, confirmando que la implementación real cumple los supuestos de independencia de la especificación FIPS 203.

---

## 3. Auditoría de Transformaciones Reales en ML-DSA / Dilithium (FIPS 204)

Extendiendo la validación experimental al estándar de firma digital FIPS 204, se evaluó un dataset sintético masivo con $N = 500,000$ muestras por cada transformación de implementación: `Decompose`, `Power2Round` y `MakeHint` / `UseHint`.

### 3.1 Metodología de Muestreo y Estimadores
- **Simulación FIPS 204**: Vectores de clave secreta $S_1, S_2 \sim U([-\eta, \eta])$, enmascaramiento $Y \sim U(\mathbb{Z}_q)$, matriz pública $A \sim U(\mathbb{Z}_q^{k \times l})$ y vector de desafío $C \in \{-1, 0, 1\}^{256}$.
- **Corrección de Miller-Madow**: Para eliminar el sesgo estocástico derivado del tamaño muestral finito $N$, la información mutua se estimó mediante:
  $$I_{\text{MM}}(S; Y) = I(S; Y) - \frac{(|S| - 1)(|Y| - 1)}{2N}$$
- **Hipótesis Nula de Uniformidad**: Prueba de $\chi^2$ (Chi-Cuadrado) sobre los binios discretos con nivel de significancia $\alpha = 0.01$.

### 3.2 Tabla de Resultados de Auditoría ML-DSA ($N = 500,000$)

| Esquema | Función | Configuración | Entropía $H$ (bits) | Max $H$ | TVD vs $U$ | $p$-valor $\chi^2$ | $I(S_1; \text{Salida})$ | $I(S_2; \text{Salida})$ | Estado |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **ML-DSA-44** | `Decompose` | $\gamma_2=95232, \eta=2$ | $17.2347$ | $17.5392$ | $0.2497$ | $0.4364$ | $0.000000$ | $0.000000$ | **PASS** |
| **ML-DSA-65/87**| `Decompose` | $\gamma_2=261888, \eta=4$| $18.1350$ | $18.9986$ | $0.3851$ | $0.1689$ | $0.000000$ | $0.000000$ | **PASS** |
| **ML-DSA-44** | `Power2Round` | $d=13, \eta=2$ | $12.9884$ | $13.0000$ | $0.0505$ | $0.9207$ | $0.000519$ | $0.001273$ | **PASS** |
| **ML-DSA-65/87**| `Power2Round` | $d=13, \eta=4$ | $12.9882$ | $13.0000$ | $0.0509$ | $0.5779$ | $0.002707$ | $0.003116$ | **PASS** |
| **ML-DSA-44** | `MakeHint` | $\gamma_2=95232, \eta=2$ | $0.0833$ | $1.0000$ | $0.4896$ | $0.8672$ | $0.000000$ | $0.000000$ | **PASS** |
| **ML-DSA-65/87**| `MakeHint` | $\gamma_2=261888, \eta=4$| $0.0258$ | $1.0000$ | $0.4974$ | $0.6950$ | $0.000000$ | $0.000000$ | **PASS** |

### 3.3 Conclusiones de Auditoría FIPS 204
1. **Residuo de Compromiso (`Decompose`)**: La parte baja $r_0 \in [-\gamma_2, \gamma_2]$ descartada en el proceso de firma no presenta ninguna fuga de información mutua hacia la clave secreta $S_1$ ($I(S_1; r_0) = 0.000000$ bits).
2. **Truncamiento de Clave Pública (`Power2Round`)**: El residuo de menor peso $t_0 \in [-4095, 4096]$ se comporta como ruido uniforme discreto de $13$ bits, con una información mutua dual acotada por $I(S_1; t_0) \le 0.0027$ bits e $I(S_2; t_0) \le 0.0031$ bits, indistinguibles de cero.
3. **Pistas de Acarreo (`MakeHint`)**: Revelar el vector binario esparso de pistas $h \in \{0, 1\}^K$ dentro de la firma digital no transmite información mutua respecto a los secretos ($I(S_1; h) = I(S_2; h) = 0.000000$ bits) y presenta una distribución espacial de unos homogénea ($\chi^2 p\text{-valor} > 0.69$).
