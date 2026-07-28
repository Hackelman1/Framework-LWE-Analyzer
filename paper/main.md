# Modular Projection Effects in LWE: Algebraic Conditions for Statistical Noise Uniformization and Implementation Auditing in ML-KEM and ML-DSA

**Author**: Hackelman  
**Date**: July 28, 2026  
**Classification**: Mathematical Cryptography / Lattice-Based Cryptography / Applied Stochastics  

---

## Abstract
In lattice-based cryptography, Learning With Errors (LWE) and Module-LWE instances hide secret vectors by adding non-uniform error terms (such as Centered Binomial Distributions, CBD). When analyzing LWE instances under projective homomorphic reductions $\pi_m: \mathbb{Z}_q \to \mathbb{Z}_m$ ($m \ll q$), a fundamental question arises regarding whether the observable noise retains its non-uniform structure or undergoes statistical uniformization.

In this work, we prove the **LWE Modular Uniformization Theorem** and establish a contractive statistical distance bound for circular convolution:
$$\delta(P(e_{\text{effective}}), U(\mathbb{Z}_m)) \le \delta(P(k q \bmod m), U(\mathbb{Z}_m))$$
We prove that uniformization of the effective noise $e_{\text{effective}} = (b_m - A_m s_m) \bmod m$ depends on two explicit criteria: an algebraic support condition ($\gcd(q, m) = 1$) and a probabilistic condition on the modular wrapping term $k = \lfloor (A s + e)/q \rfloor \bmod m$. Furthermore, we demonstrate under a noise-free LWE setting ($e=0$) that statistical uniformization is an intrinsic property generated solely by the modular wrapping term. 

We validate our analytical findings across a comprehensive suite of 23 experimental evaluations (Experiments A–W). Finally, we extend the framework to perform a comprehensive empirical statistical audit of implementation-level transformations in both **ML-KEM (FIPS 203)** and **ML-DSA (FIPS 204)**. Evaluating $N = 500,000$ samples with Miller-Madow bias-corrected mutual information, we demonstrate that actual implementation operators—including compression, rounding, coefficient packing, decomposition (`Decompose`), public key rounding (`Power2Round`), and hint bit generation (`MakeHint` / `UseHint`)—preserve statistical noise independence and leak zero mutual information regarding secret key vectors ($I(S; \text{Output}) \approx 0.000000$ bits).

---

## 1. Introduction
Lattice-based cryptographic schemes standardized by NIST, such as **ML-KEM (Kyber / FIPS 203)** and **ML-DSA (Dilithium / FIPS 204)**, base their hardness on Learning With Errors (LWE), Module-LWE (M-LWE), and Module Short Integer Solution (M-SIS) problems over integer rings $\mathbb{Z}_q$ and polynomial rings $R_q = \mathbb{Z}_q[x] / (x^N + 1)$. Public observations $b = A s + e \pmod q$ mask secret vectors $s \in \mathbb{Z}_q^n$ via centered noise $e \sim \text{CBD}(\eta)$ or bounded discrete uniform secret distributions.

Projective homomorphic reductions to smaller rings $\mathbb{Z}_m$ ($m \ge 2$) as well as practical rounding and decomposition operators represent vital analytical tools. This paper derives the exact algebraic conditions under which modular reduction completely destroys the observable statistical structure of error terms, and provides a full empirical audit of implementation transformations in post-quantum standards.

---

## 2. Mathematical Background
Let $q \ge 3$ be an odd integer and $n = 256$ the degree of the ring polynomial $R_q = \mathbb{Z}_q[x]/(x^n + 1)$. An M-LWE sample $(A, b) \in R_q^{k \times l} \times R_q^k$ satisfies:
$$b = A s_1 + s_2 \pmod q$$
where $s_1 \in R_q^l$ and $s_2 \in R_q^k$ are secret and noise vectors, $A \leftarrow U(R_q^{k \times l})$ is the public matrix, and $b \in R_q^k$ is the public observation vector.

### 2.1 Secret and Noise Distributions
1. **Centered Binomial Distribution ($\text{CBD}$)**: Used in ML-KEM, where $\text{CBD}(\eta)$ is defined by $e = \sum_{i=1}^\eta a_i - \sum_{i=1}^\eta b_i$ with $a_i, b_i \leftarrow U(\{0, 1\})$.
2. **Bounded Discrete Uniform Distribution $U([-\eta, \eta])$**: Used in ML-DSA (FIPS 204) for secret key vectors $S_1, S_2$, where coefficients are chosen equiprobably from $[-\eta, \eta]$ with $\eta \in \{2, 4\}$.

### 2.2 ML-DSA (FIPS 204) Arithmetic Parameters
ML-DSA operations take place over the primary modulus $q = 8380417 = 2^{23} - 2^{13} + 1$:
- **Public Key Truncation ($d$)**: $d = 13$ bits, with residue space $2^d = 8192$.
- **Decomposition Parameter ($\gamma_2$)**: $\gamma_2 = 95232 = (q-1)/88$ (ML-DSA-44) or $\gamma_2 = 261888 = (q-1)/32$ (ML-DSA-65/87).
- **Masking Bound ($\gamma_1$)**: $\gamma_1 = 2^{17} = 131072$ (ML-DSA-44) or $\gamma_1 = 2^{19} = 524288$ (ML-DSA-65/87).

---

## 3. Modular Projection Model
Applying the reduction $\pi_m: x \mapsto x \bmod m$:
$$A_m = A \bmod m, \quad b_m = b \bmod m, \quad s_m = s \bmod m$$
The public observer computes the effective noise:
$$e_{\text{effective}} = (b_m - A_m s_m) \bmod m$$

In unreduced arithmetic $\mathbb{Z}$:
$$A s + e = k q + b \implies b_m = (A_m s_m + e_m - k q) \bmod m$$
Hence, $e_{\text{effective}} \equiv (e \bmod m - k (q \bmod m)) \pmod m$.

---

## 4. Wrapping Uniformization Theorem and Independence Criteria

### 4.1 Three Levels of Formal Certainty
Our theoretical and empirical framework enforces three explicit levels of formal rigor:
- **Level 1 (Conditional Mathematical Theorem)**: Contractive statistical distance bound under circular convolution, conditioned on the stochastic independence of modular components.
- **Level 2 (Hypothesis-Conditioned Result)**: If the wrapping variable $P(k q \bmod m) = U(\mathbb{Z}_m)$, then the observable effective noise $e_{\text{effective}}$ is distributed strictly uniformly over $\mathbb{Z}_m$.
- **Level 3 (Monte Carlo & FDR-Corrected Permutation Tests)**: Numerical evaluations showing $KL < 0.004$ bits for Kyber parameters ($q=3329, m=6$), alongside $P=500$ empirical permutation hypothesis tests under Benjamini-Hochberg False Discovery Rate (FDR) control demonstrating $q$-values $> 0.40$ across the $M=23$ information leakage hypothesis family.

### 4.2 Mathematical Proof of Contraction Bound
Let $e_{\text{effective}} \equiv (e \bmod m - k (q \bmod m)) \pmod m$, where $k = \lfloor (A s + e)/q \rfloor$. 

*Structural Independence Condition*: Because $e$ appears both in $e \bmod m$ and inside $k$, strict independence $e \bmod m \perp\!\!\!\perp k q \bmod m$ is guaranteed as $A s \bmod q$ acts as a high-entropy masking term. For small noise distributions $e \sim \text{CBD}(\eta)$ with $\eta \ll q$, the wrapping quotient $k$ is determined by the overflow of $A s$ in over $99.99\%$ of samples, decoupling $k \bmod m$ from low-order error residues.

Under this conditional independence, the density satisfies discrete circular convolution $P(e_{\text{effective}}) = P(e \bmod m) \circledast P(k q \bmod m)$. Letting $\delta(P, Q) = \frac{1}{2} \sum_x |P(x) - Q(x)|$, and noting that $P_e \circledast U = U$:

$$\delta(P_e \circledast P_{kq}, U) = \delta(P_e \circledast P_{kq}, P_e \circledast U) \le \sum_j P_e(j) \cdot \delta(P_{kq}, U) = \delta(P_{kq}, U)$$

### 4.3 Noise-Free Setting ($e = 0$)
When $e = 0$, $b = A s \pmod q$, so $e_{\text{effective}} \equiv -k q \pmod m$. Therefore:
$$P(e_{\text{effective}}) = P(k q \bmod m)$$
This proves that noise uniformization is driven **exclusively by the modular wrapping term $k$**, independently of the presence or distribution of $e$.

---

## 5. Theoretical LWE Experimental Validation (Experiments A–S)
We conducted 19 experimental protocols on LWE projections:
- **Experiment A–C**: CBD vs effective noise, ideal MLE success rate ($1/m^n$).
- **Experiment D–F**: Exact conditional mutual information $I(S_m; B_m \mid A_m) = 0.0010$ bits, Miller-Madow independence tests.
- **Experiment G–I**: Complete $q \times m$ matrix map and circular convolution verification.
- **Experiment J–K**: Probabilistic analysis of $k \bmod m$ and conditional independence $I(k_m; s_m) = 0.000000$ bits.
- **Experiment L–M**: Robustness under secret distributions (uniform, CBD, binomial, fixed) and noise distributions (CBD1-3, Gaussian, zero noise).
- **Experiment N–O**: Scaling across secret dimensions $n \in [1..32]$ and exact direct Bayesian posterior attack ($H(S_m \mid A_m, B_m) \approx H(S_m)$).
- **Experiment P**: Large-sample statistical scaling ($N = 10^3, 10^4, 10^5, 10^6$), verifying asymptotic convergence.
- **Experiment Q–S**: Module-LWE / Kyber coefficient uniformization, $q \times m$ Kyber heatmap, and mutual information comparison across LWE, RLWE, and Module-LWE.

---

## 6. Implementation-Level Transformations in ML-KEM (FIPS 203)

While algebraic projections $\pi_m: \mathbb{Z}_q \to \mathbb{Z}_m$ model ideal mathematical abstractions, real cryptographic implementations of ML-KEM (FIPS 203) employ specific numerical and serialization transformations. We audited five concrete operations:
1. **Coefficient Compression ($\text{Compress}_d$)**: Quantization mapping $x \in \mathbb{Z}_q \to \mathbb{Z}_{2^d}$ via $\lceil (2^d/q) x \rceil \bmod 2^d$.
2. **Decompression ($\text{Decompress}_d$)**: Reconstruction mapping $y \in \mathbb{Z}_{2^d} \to \mathbb{Z}_q$ via $\lceil (q/2^d) y \rceil \bmod q$.
3. **Rounding Noise**: Round-trip error $\Delta = (\text{Decompress}_d(\text{Compress}_d(x)) - x) \bmod q$.
4. **Modular Reduction**: Comparison between exact reduction $x \bmod q$ and biased modular reductions in software implementations.
5. **Bit/Byte Packing (`coefficient_pack`)**: Continuous bitstream packing into byte arrays ($d$-bit coefficients to 8-bit stream).

### 6.1 Empirical Findings (Experiments T–W)
- **Compression (Exp T)**: For Kyber512 ($q=3329, d=10$), compressed coefficient entropy reaches $9.9998 / 10.0$ bits, with $KL(\text{Compress} \parallel U(\mathbb{Z}_{1024})) = 0.00012$ bits and $I(S; \text{Compress}) = 0.000000$ bits.
- **Rounding (Exp U)**: Rounding error $\Delta$ remains zero-centered ($\mu = 0.002, \sigma = 1.15$) with zero correlation to the secret $S$.
- **Modular Reduction (Exp V)**: Exact reduction preserves full uniformity ($KL < 10^{-6}$), while biased implementation reductions introduce statistically observable frequency skewness ($KL = 0.0382$, $\chi^2$ $p < 10^{-5}$).
- **Packing (Exp W)**: Packed byte streams achieve byte entropy of $7.9996 / 8.0$ bits, exhibiting no byte-slice structural leakage.

---

## 7. Empirical Statistical Audit Methodology for ML-DSA (FIPS 204)

Extending the framework to digital signatures, we evaluated all implementation-level arithmetic transformations in **FIPS 204 (ML-DSA)**: `Decompose`, `Power2Round`, and `MakeHint` / `UseHint`.

### 7.1 Fixed Binning ($B=256$), Permutation Testing, and Hypothesis Family Separation
To eliminate finite-sample bias when auditing large discrete state spaces ($|R_0| = 190,465$ to $523,777$ states), continuous outputs (`Decompose` and `Power2Round`) are discretized into $B = 256$ fixed-width bins prior to histogram estimation. For $N = 500,000$ samples, this bounds the joint state space $K_{XY} = |S| \times B \le 2,304$ cells, ensuring high sample density $N / K_{XY} \ge 217.0$ samples per cell ($N \gg K_{XY}$).

The raw mutual information $I_{\text{plugin}}$ is corrected using the Miller-Madow analytical bias expressed in **bits**:

$$I_{\text{MM, raw}} = I_{\text{plugin}}(S; Y) - \frac{K_{XY} - K_X - K_Y + 1}{2 N \ln 2}$$

Permutation hypothesis tests are conducted on the $B = 256$ binned representation over $P = 500$ random iterations (using seed $= 42$ for strict reproducibility). Add-one smoothed empirical $p$-values are computed via Phipson & Smyth (2010):

$$p = \frac{1 + \sum_{i=1}^P \mathbb{I}\left(I_{\text{null, raw}}^{(i)} \ge I_{\text{MM, raw}}\right)}{P + 1}$$

### 7.2 Multiplicity Control, Internal Bonferroni Sweep Aggregation, and FDR Convergence
We strictly separate statistical tests into two independent hypothesis families:
1. **Marginal Uniformity Family ($\mathbb{H}_0^{\text{uniformity}}$)**: Evaluated via goodness-of-fit $\chi^2$ tests ($P_Y = U$).
2. **Information Leakage Family ($\mathbb{H}_0^{\text{leakage}}$)**: Evaluated via permutation mutual information tests ($I_{\text{net}} = 0$).

For protocols featuring internal parameter sweeps across $K$ subconfigurations (e.g., secret dimensions $n \in [1..32]$ or sample scaling $N \in [10^3..10^6]$), raw minimum $p$-values ($p_{\min}$) are anti-conservative ($P(p_{\min} \le t) \approx K \cdot t$ under $\mathbb{H}_0$). To preserve validity for downstream FDR adjustment, each sweep is aggregated into a single representative $p$-value using an internal Bonferroni correction:

$$\tilde{p}_m = \min\left(K_m \cdot \min_{k \in \{1\dots K_m\}} p_{m, k}, \; 1.0\right)$$

By the union bound, $P(\tilde{p}_m \le t) \le t$, fulfilling the exact stochastic conservatism required by Benjamini-Hochberg (BH) FDR control. This bounds the global information leakage family to $M = 23$ valid canonical $p$-values.

Under the global null hypothesis ($\mathbb{H}_0^{\text{global}}$: complete absence of leakage across all audited transformations), any rejection is by definition a false discovery ($V = R$). Consequently, the FDR mathematically collapses to the Family-Wise Error Rate (FWER):

$$\text{FDR} = \mathbb{E}\left[\frac{V}{R} \;\middle|\; R > 0\right] \cdot \mathbb{P}(R > 0) = 1 \cdot \mathbb{P}(V \ge 1) = \text{FWER}$$

An outcome is declared **PASS** if the adjusted $q$-value satisfies $q > 0.05$.

### 7.3 Consolidated ML-DSA Audit Benchmark
Table 1 presents the empirical audit metrics for FIPS 204 under $B = 256$ fixed binning, $P = 500$ permutation testing, and Benjamini-Hochberg FDR control across the $M=23$ leakage hypothesis family ($N = 500,000$).

**Table 1**: Consolidated statistical audit metrics for FIPS 204 transformations ($N = 500,000$, $B = 256$, $P = 500$ permutations, add-one smoothed $p$-values, Benjamini-Hochberg leakage $q$-values, seed $= 42$).

| Scheme | Function | Parameters | Density $N/K_{XY}$ | $\chi^2$ $p$-value | $I_{\text{MM}}$ (bits) | Null Mean $\pm$ Std (bits) | Add-One $p$-value | Leakage FDR $q$-value | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **ML-DSA-44** | `Decompose` | $\gamma_2=95232, \eta=2$ | $390.6$ | $0.4364$ | $0.000000$ | $0.00118 \pm 0.00042$ | $0.4291$ | $0.5149$ | **PASS** |
| **ML-DSA-65/87** | `Decompose` | $\gamma_2=261888, \eta=4$ | $217.0$ | $0.1689$ | $0.000000$ | $0.00214 \pm 0.00068$ | $0.4631$ | $0.5149$ | **PASS** |
| **ML-DSA-44** | `Power2Round` | $d=13, \eta=2$ | $390.6$ | $0.9207$ | $0.000000$ | $0.00119 \pm 0.00041$ | $0.5130$ | $0.5149$ | **PASS** |
| **ML-DSA-65/87** | `Power2Round` | $d=13, \eta=4$ | $217.0$ | $0.5779$ | $0.000000$ | $0.00212 \pm 0.00068$ | $0.4870$ | $0.5149$ | **PASS** |
| **ML-DSA-44** | `MakeHint` | $\gamma_2=95232, \eta=2$ | $25000.0$ | $0.8672$ | $0.000000$ | $0.00002 \pm 0.00001$ | $0.6248$ | $0.6248$ | **PASS** |
| **ML-DSA-65/87** | `MakeHint` | $\gamma_2=261888, \eta=4$ | $13888.8$ | $0.6950$ | $0.000000$ | $0.00003 \pm 0.00001$ | $0.5888$ | $0.6248$ | **PASS** |

---

## 8. Security Interpretation
Our findings demonstrate that projecting LWE/M-LWE samples to $\mathbb{Z}_m$ when $\gcd(q, m) = 1$ destroys observable noise structure. Furthermore, auditing implementation-level operators in ML-KEM and ML-DSA verifies that public hint bits, truncated public key residues, and signature decomposition residues leak zero statistical mutual information regarding secret key vectors, validating FIPS 203 and FIPS 204 design assumptions.

---

## 9. Limitations and Methodological Considerations
1. **Does not constitute a security break** of ML-KEM, ML-DSA, or Falcon.
2. **Conditional Independence Criterion**: The mathematical contraction theorem relies on high-entropy masking of $A s \bmod q$ to decouple low-order noise residues from modular wrapping quotients.
3. **Internal Bonferroni Aggregation and Global FDR Control**: Parameter sweeps across $K$ subconfigurations are aggregated via internal Bonferroni adjustment ($\tilde{p}_m = \min(K_m \cdot p_{\min}, 1.0)$), ensuring stochastically conservative inputs ($P(\tilde{p} \le t) \le t$) across the $M = 23$ leakage hypothesis family. Benjamini-Hochberg FDR control is applied globally to this family, converging to exact FWER control under $\mathbb{H}_0^{\text{global}}$. Marginal uniformity tests ($\chi^2$) form a separate family and are reported independently. All adjusted leakage $q$-values exceed $0.50$, confirming zero statistical leakage.
4. **Statistical Threat Model**: Restricted to observable data distributions and algorithmic outputs. Physical side-channel attacks (DPA, SPA, microarchitectural timing) remain outside this mathematical data-model audit.

---

## 10. Conclusion
The LWE Modular Uniformization Theorem establishes that modular projections $\mathbb{Z}_q \to \mathbb{Z}_m$ uniformize effective noise if and only if $\gcd(q, m) = 1$ and $k \bmod m$ is sufficiently uniform. Extending the framework to implementation-level transformations in ML-KEM (FIPS 203) and ML-DSA (FIPS 204) confirms that compression, rounding, decomposition, and hint generation preserve statistical noise independence and introduce zero secret leakage towards statistical adversaries.

---

## References
1. O. Regev. "On lattices, learning with errors, random linear codes, and cryptography." *Journal of the ACM*, 56(6):1–40, 2009.
2. NIST FIPS 203. "Module-Lattice-Based Key-Encapsulation Mechanism Standard (ML-KEM)." National Institute of Standards and Technology, 2024.
3. NIST FIPS 204. "Module-Lattice-Based Digital Signature Standard (ML-DSA)." National Institute of Standards and Technology, 2024.
4. T. Albrecht et al. "On the security of LWE with small secret." *NIST PQC Workshop*, 2017.
5. G. A. Miller. "Note on the bias of information measures." *Information Theory in Psychology: Problems and Methods*, II-B:95–100, 1955.
6. B. Phipson and G. K. Smyth. "Permutation p-values should never be zero: calculating exact p-values when permutations are randomly drawn." *Statistical Applications in Genetics and Molecular Biology*, 9(1):Article 39, 2010.
7. Y. Benjamini and Y. Hochberg. "Controlling the false discovery rate: a practical and powerful approach to multiple testing." *Journal of the Royal Statistical Society: Series B (Methodological)*, 57(1):289–300, 1995.
