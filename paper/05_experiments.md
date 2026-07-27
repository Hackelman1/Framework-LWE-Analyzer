# 05. Resultados Experimentales y Validación Estocástica

## Suite de Experimentos (Experimentos A al O)

1. **Experimento A**: Diferencia entre la CBD reducida $P(e \bmod 6)$ (no uniforme) y el ruido efectivo real $P(e_{\text{eff}})$ ($KL < 0.003$ bits).
2. **Experimento B y C**: Atacante ideal MLE sobre la proyección obtiene tasa de éxito idéntica al azar ($1/m^n$).
3. **Experimento D**: Información mutua exacta condicionada $I(S_m; B_m \mid A_m) = 0.0010$ bits (compatible con cero).
4. **Experimento G y H**: Mapa matricial $q \times m$, donde $\gcd(q,m)=1 \implies KL \approx 0$, mientras que $\gcd(q,m) > 1 \implies KL > 0$.
5. **Experimento K**: Demuestra que $I(k_m; s_m) = 0.000000$ bits (independencia condicional).
6. **Experimento L (Análisis del Secreto Ternario)**:
   - Secretos de baja entropía ($s \in \{-1, 0, 1\}$) entregan $KL(e_{\text{eff}} \parallel U) = 0.3996$ bits.
   - **Explicación**: La baja variabilidad del producto $A s$ en $\mathbb{Z}$ restringe el alcance continuo necesario para que el cociente de envoltorio $k = \lfloor (A s + e)/q \rfloor$ se distribuya uniformemente. La uniformización requiere **tanto $\gcd(q,m)=1$ como suficiente entropía en $A s$**.
7. **Experimento M (Prueba de Ruido Cero $e=0$)**: Con $e=0$, $KL(e_{\text{eff}} \parallel U(\mathbb{Z}_6)) = 0.003387$ bits, demostrando que el envoltorio $k q \bmod m$ uniformiza por sí solo.
8. **Experimento N (Escalado con la Dimensión $n$)**: Al aumentar la dimensión del secreto $n \in \{1, 2, 4, 8, 16, 32\}$, la divergencia $KL(e_{\text{eff}} \parallel U)$ decae monótonamente hacia 0.
9. **Experimento O (Ataque Bayesiano Directo de Entropía A Posteriori)**: La entropía a posteriori $H(S_m \mid A_m, B_m)$ coincide exactamente con la previa $H(S_m)$ ($MI = 0.0000$ bits), confirmando que la proyección proyectada no filtra información de la clave.
