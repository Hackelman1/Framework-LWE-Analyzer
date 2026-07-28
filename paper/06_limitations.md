# 06. Limitaciones Explícitas, Alcance Criptográfico y Modelo de Amenaza

## Alcance del Estudio
- Los resultados matemáticos y experimentales describen la transformación de distribuciones de probabilidad y la conservación de la uniformidad bajo proyecciones homomórficas explícitas y transformaciones de implementación.
- **Sin Impacto en la Seguridad Criptográfica de los Estándares**: Los hallazgos no constituyen un ataque a la seguridad ni revelan vulnerabilidades en esquemas estandarizados como **ML-KEM (FIPS 203)**, **ML-DSA (FIPS 204)** o **Falcon**.
- **Confirmación de Seguridad**: Al contrario, los experimentos verifican empíricamente que las proyecciones modulares con $\gcd(q,m)=1$ y las transformaciones de truncamiento, descomposición y generación de pistas (`Decompose`, `Power2Round`, `MakeHint`) destruyen la estructura estadística observable del ruido y la señal, manteniendo la información mutua respecto a las claves secretas $S_1$ y $S_2$ en cero ($I(S; \text{Salida}) \approx 0.0000$ bits).

## Acotaciones de Evaluación y Modelo de Datos
- **Pruebas Teóricas LWE**: Evaluaciones de enumeración Bayesiana exacta y cálculo de entropía a posteriori realizadas sobre dimensiones reducidas ($n \le 5$) por complejidad computacional de integración discreta.
- **Auditoría de Implementación**: Evaluaciones estocásticas masivas con muestras sintéticas ($N = 500,000$ por función) aplicando la corrección analítica de Miller-Madow para suprimir el sesgo de tamaño muestral finito.
- **Modelo de Amenaza Estadístico Exclusivo**: El análisis se limita estrictamente al modelo de datos matemático y la independencia estadística de las salidas algorítmicas. No aborda ni evalúa ataques físicos de canal lateral (*Side-Channel Attacks* como DPA, SPA o ataques por fluctuación de voltaje/tiempo microarquitectónico), ni inyección de fallos (*Fault Injection*), los cuales quedan fuera del alcance del presente modelo de auditoría matemática.
