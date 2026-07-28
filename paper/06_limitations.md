## 6. Limitations, Cryptographic Scope, and Threat Model

### 6.1 Scope of the Study
- **Probability Distribution Analysis**: Mathematical and empirical findings describe the transformation of probability distributions and the preservation of statistical uniformity under explicit homomorphic projections and implementation operators.
- **No Impact on Cryptographic Security**: Our findings **do not constitute a security break, vulnerability, or weakness** in standardized schemes such as **ML-KEM (FIPS 203)**, **ML-DSA (FIPS 204)**, or **Falcon**.
- **Empirical Security Confirmation**: On the contrary, empirical audits verify that modular projections with $\gcd(q, m) = 1$ as well as truncation, decomposition, and hint generation operators (`Decompose`, `Power2Round`, `MakeHint` / `UseHint`) destroy observable noise/signal structure, maintaining mutual information regarding secret key vectors $S_1$ and $S_2$ strictly at zero ($I(S; \text{Output}) = 0.000000$ bits).

---

### 6.2 Methodological Considerations and Multiplicity Control
1. **Conditional Independence Criterion**: The mathematical contraction theorem relies on high-entropy masking of $A s \bmod q$ to decouple low-order noise residues from modular wrapping quotients.
2. **Internal Bonferroni Aggregation and Global FDR Control**: Parameter sweeps across $K$ subconfigurations are aggregated via internal Bonferroni adjustment ($\tilde{p}_m = \min(K_m \cdot p_{\min}, 1.0)$), ensuring stochastically conservative inputs ($P(\tilde{p} \le t) \le t$) across the $M = 23$ leakage hypothesis family ($\mathbb{H}_0^{\text{leakage}}$). Benjamini-Hochberg FDR control is applied globally to this family, converging to exact FWER control under the global null hypothesis ($\mathbb{H}_0^{\text{global}}$). Marginal uniformity tests ($\mathbb{H}_0^{\text{uniformity}}$ via $\chi^2$) form an independent family and are reported separately. All adjusted leakage $q$-values exceed $0.50$, confirming zero statistical leakage.
3. **Sampling Density and Analytical Bias Correction**: Implementation auditing employs $N = 500,000$ synthetic samples per function under $B = 256$ fixed binning ($K_{XY} \le 2,304$ cells, density $N / K_{XY} \ge 217.0$ samples per cell) combined with analytical Miller-Madow bias correction expressed in bits using the natural logarithm factor ($2 N \ln 2$) to eliminate finite-sample statistical artifacts.
4. **Bayesian Enumeration Bounds**: Exact Bayesian posterior entropy calculations and full state enumerations in theoretical LWE experiments are restricted to reduced dimensions ($n \le 5$) due to exponential discrete integration complexity.

---

### 6.3 Statistical Data-Model Threat Scope
- **Algorithmic Data Model**: The threat model is strictly restricted to observable data distributions, mathematical projections, and algorithmic outputs.
- **Exclusion of Physical Side Channels**: Physical side-channel attacks (Differential Power Analysis - DPA, Simple Power Analysis - SPA, electromagnetic emissions, microarchitectural timing leakage) and physical fault injection attacks remain outside the mathematical threat model of this algorithmic statistical auditor.
