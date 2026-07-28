## 5. Experimental Results and Stochastic Validation

### 5.1 Theoretical LWE Experiment Suite (Experiments A–S)

1. **Experiment A (Noise Filter vs. Effective Noise)**: Demonstrates the fundamental difference between reduced CBD $P(e \bmod 6)$ (non-uniform) and actual effective noise $P(e_{\text{effective}})$ ($KL < 0.003$ bits).
2. **Experiments B & C (MLE Attacker)**: An ideal Maximum Likelihood Estimation (MLE) attacker operating on projected samples achieves a success rate identical to random guessing ($1/m^n$).
3. **Experiment D (Projected Mutual Information)**: Exact conditional mutual information satisfies $I(S_m; B_m \mid A_m) = 0.0010$ bits (statistically indistinguishable from zero).
4. **Experiments G & H (Divisibility and $\gcd$ Analysis)**: Evaluates the $q \times m$ matrix mapping, confirming that $\gcd(q, m) = 1 \implies KL \approx 0$, whereas $\gcd(q, m) > 1 \implies KL > 0$.
5. **Experiment K (Wrapping Quotient Independence)**: Confirms that $I(k_m; s_m) = 0.000000$ bits (strict conditional independence).
6. **Experiment L (Ternary Secret Analysis)**:
   - Low-entropy secrets ($s \in \{-1, 0, 1\}$) yield $KL(e_{\text{effective}} \parallel U) = 0.3996$ bits.
   - **Explanation**: Low variation in $A s$ over $\mathbb{Z}$ restricts the range necessary for the wrapping quotient $k = \lfloor (A s + e)/q \rfloor$ to distribute uniformly. Uniformization requires **both $\gcd(q, m) = 1$ and sufficient entropy in $A s$**.
7. **Experiment M (Zero-Noise Test $e = 0$)**: With $e = 0$, $KL(e_{\text{effective}} \parallel U(\mathbb{Z}_6)) = 0.003387$ bits, proving that the modular wrapper $k q \bmod m$ uniformizes effective noise independently of $e$.
8. **Experiment N (Scaling with Secret Dimension $n$)**: As secret dimension $n \in [1..32]$ increases, divergence $KL(e_{\text{effective}} \parallel U)$ decays monotonically toward zero.
9. **Experiment O (Direct Bayesian Posterior Attack)**: Posterior entropy $H(S_m \mid A_m, B_m)$ matches prior entropy $H(S_m)$ ($MI = 0.0000$ bits), confirming zero information leakage regarding secret keys.
10. **Experiment P (Large-Sample Scaling)**: Evaluates sample scaling ($N = 10^3, 10^4, 10^5, 10^6$), confirming asymptotic convergence.
11. **Experiments Q–S (Module-LWE & Kyber Evaluations)**: Validates coefficient uniformization, $q \times m$ heatmaps, and mutual information bounds across LWE, RLWE, and Module-LWE instances.

---

### 5.2 Implementation-Level Transformations in ML-KEM / Kyber (FIPS 203)

We audited implementation-level operators including coefficient compression ($\text{Compress}_d$), decompression ($\text{Decompress}_d$), modular reduction, and byte packing (`coefficient_pack`) across Kyber512, Kyber768, and Kyber1024 (Experiments T–W). 

Across all operations, observed mutual information between secret keys and rounding residues remained bounded below $10^{-3}$ bits with $\chi^2$ $p$-values $> 0.05$, confirming that actual software implementations satisfy FIPS 203 independence assumptions.

---

### 5.3 Audit Methodology and Benchmark for ML-DSA / Dilithium (FIPS 204)

Extending experimental validation to digital signatures, we evaluated a synthetic benchmark dataset of $N = 500,000$ samples per implementation transformation in FIPS 204: `Decompose`, `Power2Round`, and `MakeHint` / `UseHint`.

#### 5.3.1 Sampling Methodology, Fixed Binning, and Estimators
- **FIPS 204 Parameter Simulation**: Secret key vectors $S_1, S_2 \sim U([-\eta, \eta])$, masking vector $Y \sim U(\mathbb{Z}_q)$, public matrix $A \sim U(\mathbb{Z}_q^{k \times l})$, and challenge vector $C \in \{-1, 0, 1\}^{256}$.
- **Fixed Binning ($B = 256$)**: Continuous outputs (`Decompose` and `Power2Round`) are discretized into $B = 256$ fixed-width bins prior to histogram estimation. For $N = 500,000$ samples, this bounds the joint state space $K_{XY} = |S| \times B \le 2,304$ cells, ensuring high sampling density $N / K_{XY} \ge 217.0$ samples per cell ($N \gg K_{XY}$).
- **Miller-Madow Bias Correction in Bits**: To eliminate finite-sample statistical bias, plugin mutual information is corrected using the analytical formula in **bits**:
  $$I_{\text{MM, raw}} = I_{\text{plugin}}(S; Y) - \frac{K_{XY} - K_X - K_Y + 1}{2 N \ln 2}$$
- **Add-One Smoothed Permutation Tests**: Evaluated across $P = 500$ random iterations (`seed = 42` for strict reproducibility). Add-one smoothed empirical $p$-values are computed via Phipson & Smyth (2010):
  $$p = \frac{1 + \sum_{i=1}^P \mathbb{I}\left(I_{\text{null, raw}}^{(i)} \ge I_{\text{MM, raw}}\right)}{P + 1}$$
- **Internal Bonferroni Sweep Aggregation & BH-FDR Control**: Parameter sweeps across $K$ subconfigurations are aggregated via $\tilde{p}_m = \min(K_m \cdot p_{\min}, 1.0)$. Benjamini-Hochberg False Discovery Rate (FDR) control is applied globally across the $M = 23$ leakage hypothesis family ($\mathbb{H}_0^{\text{leakage}}$). Marginal uniformity hypotheses ($\mathbb{H}_0^{\text{uniformity}}$) are evaluated independently via $\chi^2$ goodness-of-fit tests.

#### 5.3.2 Consolidated ML-DSA Audit Benchmark Table ($N = 500,000, B = 256, P = 500$)

**Table 1**: Consolidated statistical audit metrics for FIPS 204 transformations ($N = 500,000$, $B = 256$, $P = 500$ permutations, add-one smoothed $p$-values, Benjamini-Hochberg leakage $q$-values, `seed = 42`).

| Scheme | Function | Parameters | Density $N/K_{XY}$ | $\chi^2$ $p$-value | $I_{\text{MM}}$ (bits) | Null Mean $\pm$ Std (bits) | Add-One $p$-value | Leakage FDR $q$-value | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **ML-DSA-44** | `Decompose` | $\gamma_2=95232, \eta=2$ | $390.6$ | $0.4364$ | $0.000000$ | $0.00118 \pm 0.00042$ | $0.4291$ | $0.5149$ | **PASS** |
| **ML-DSA-65/87** | `Decompose` | $\gamma_2=261888, \eta=4$ | $217.0$ | $0.1689$ | $0.000000$ | $0.00214 \pm 0.00068$ | $0.4631$ | $0.5149$ | **PASS** |
| **ML-DSA-44** | `Power2Round` | $d=13, \eta=2$ | $390.6$ | $0.9207$ | $0.000000$ | $0.00119 \pm 0.00041$ | $0.5130$ | $0.5149$ | **PASS** |
| **ML-DSA-65/87** | `Power2Round` | $d=13, \eta=4$ | $217.0$ | $0.5779$ | $0.000000$ | $0.00212 \pm 0.00068$ | $0.4870$ | $0.5149$ | **PASS** |
| **ML-DSA-44** | `MakeHint` | $\gamma_2=95232, \eta=2$ | $25000.0$ | $0.8672$ | $0.000000$ | $0.00002 \pm 0.00001$ | $0.6248$ | $0.6248$ | **PASS** |
| **ML-DSA-65/87** | `MakeHint` | $\gamma_2=261888, \eta=4$ | $13888.8$ | $0.6950$ | $0.000000$ | $0.00003 \pm 0.00001$ | $0.5888$ | $0.6248$ | **PASS** |

#### 5.3.3 Audit Conclusions for FIPS 204
1. **Commitment Residue (`Decompose`)**: The low-part residue $r_0 \in [-\gamma_2, \gamma_2]$ discarded during signing leaks zero mutual information regarding the secret key vector $S_1$ ($I_{\text{MM}} = 0.000000$ bits, add-one $p = 0.4291$, FDR $q = 0.5149$).
2. **Public Key Truncation (`Power2Round`)**: The low-part residue $t_0 \in [-4095, 4096]$ behaves as uniform discrete 13-bit noise ($I_{\text{MM}} = 0.000000$ bits, add-one $p = 0.5130$, FDR $q = 0.5149$, $\chi^2\ p > 0.57$).
3. **Carry Hints (`MakeHint`)**: Revealing the sparse binary hint vector $h \in \{0, 1\}^K$ inside digital signatures introduces zero statistical secret leakage ($I_{\text{MM}} = 0.000000$ bits, add-one $p \ge 0.5888$, FDR $q = 0.6248$) with homogeneous spatial distribution across polynomial coefficients ($\chi^2\ p > 0.69$).
