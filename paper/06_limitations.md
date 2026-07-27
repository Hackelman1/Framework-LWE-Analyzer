# 06. Limitaciones Explícitas y Alcance Criptográfico

## Alcance del Estudio
- Los resultados describen la transformación de distribuciones de probabilidad bajo proyecciones homomórficas explícitas.
- No constituyen un ataque a la seguridad ni una vulnerabilidad en esquemas estandarizados como Kyber (ML-KEM) o Falcon.
- Al contrario, confirman que las proyecciones con $\gcd(q,m)=1$ destruyen la información observable del error, preservando la dureza del secreto subyacente.

## Acotaciones de Evaluación
- Pruebas computacionales de enumeración Bayesiana realizadas en dimensiones reducidas ($n \le 5$).
- Supuesto de independencia a priori de muestras LWE.
