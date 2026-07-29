[Español](README.md) | **English**

# Statistical Evaluation and Audit Framework for LWE / ML-KEM / ML-DSA (Release v2.0)
[![DOI](https://zenodo.org/badge/1313642539.svg)](https://doi.org/10.5281/zenodo.21622274)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Release v2.0.0](https://img.shields.io/badge/release-v2.0.0-green.svg)](https://github.com/Hackelman1/pqc-statistical-auditor)


Official v2.0.0 release of the theoretical and experimental framework for analyzing statistical noise uniformization in Learning With Errors (LWE), Ring-LWE, Module-LWE, and comprehensive statistical auditing of real implementation transformations in **ML-KEM (FIPS 203)** and **ML-DSA (FIPS 204)**.

---

## 1. Scope & Key Discoveries

1. **LWE Modular Uniformization Theorem (Conditional Mathematical Theorem)**: Contractive statistical distance bound under circular convolution, subject to the structural independence condition ($e \bmod m \perp\!\!\!\perp k q \bmod m$) verified with probability $\ge 1 - 2\eta/q$ (negligible, $10^{-3}$ to $10^{-7}$ depending on the scheme) via modular boundary decoupling (see Section 4.2 of the paper):
   $$\delta(P(e_{\text{effective}}), U(\mathbb{Z}_m)) \le \delta(P(k q \bmod m), U(\mathbb{Z}_m))$$
2. **Algebraic Criteria**: Complete effective noise uniformization requires $\gcd(q, m) = 1$ and sufficient dispersion of the modular wrapping term $k = \lfloor (A s + e)/q \rfloor \bmod m$.
3. **Noise-Free Proof ($e=0$)**: Conditional mathematical and empirical proof that uniformization is driven intrinsically by the wrapping term $k$, independently of the noise magnitude $e$, under the structural independence condition ($e \bmod m \perp\!\!\!\perp k q \bmod m$).
4. **Audit of Real Implementation Transformations in ML-KEM / Kyber (FIPS 203)**:
   - Compression ($\text{Compress}_d$) and Decompression ($\text{Decompress}_d$).
   - Round-trip rounding error noise.
   - Exact vs. biased modular reduction (`exact` vs. `biased`).
   - Bit and byte packing (`coefficient_pack/unpack`).
   - **Audit Conclusion**: Implementation-level transformations preserve statistical noise independence and do not leak mutual information about the secret key ($I(S; \text{Output}) \approx 0.0000$ bits).
5. **Audit of Rounding, Decomposition, and Hint Functions in ML-DSA / Dilithium (FIPS 204)**:
   - **`Decompose`**: Empirical verification that the low-part residue $r_0 \in [-\gamma_2, \gamma_2]$ generated during signing leaks no information about the secret key $S_1$ ($I(S_1; r_0) = 0.000000$ bits) across all security levels.
   - **`Power2Round`**: Demonstration that the truncated public key residue $t_0 \in [-4095, 4096]$ ($d=13$) acts as 13-bit discrete uniform noise, revealing no appreciable mutual information regarding $S_1$ or $S_2$ ($I(S; t_0) \le 0.0031$ bits) and passing the Chi-Square goodness-of-fit test ($\chi^2 p\text{-value} > 0.57$).
   - **`MakeHint` / `UseHint`**: Verification that binary hint vectors $h \in \{0, 1\}^K$ transmitted publicly in digital signatures leak no mutual information about secret keys ($I(S_1; h) = I(S_2; h) = 0.000000$ bits) and exhibit a spatial homogeneous distribution ($\chi^2 p\text{-value} > 0.69$).
6. **Stochastic Statistical Audit Methodology**: Stochastic evaluation via fixed binning ($B = 256$), permutation tests ($P = 500$, seed = 42) with add-one smoothing (Phipson & Smyth, 2010), internal Bonferroni aggregation for parameter sweeps, and global Benjamini-Hochberg multiplicity control (BH-FDR) over the $M = 23$ leakage hypotheses.

---

## 2. Repository Structure

```
pqc-statistical-auditor/
├── src/                         # Core generation, projection, and attack modules
├── schemes/                     # Parameter and instance definitions (Module-LWE / Kyber)
│   └── module_lwe/              # Kyber512, Kyber768, Kyber1024, and KyberTransformAuditor
├── transformations/             # Real Kyber and ML-DSA operations (compression, rounding, hints)
│   └── dsa/                     # FIPS 204 audit modules (decompose, power2round, hint)
├── tests/                       # Automated unit test suite (23 tests)
├── docs/                        # Theoretical and methodological documentation
├── paper/                       # Main manuscript in Markdown (main.md)
├── results/                     # CSV datasets, PNG plots, and consolidated reports
├── config/                      # Centralized YAML configuration (default.yaml)
├── scripts/                     # Utility scripts for clean rebuilds and cleaning
│   ├── clean_results.py
│   └── rebuild_all.py
├── run_all_experiments.py       # Single entry point for experiments
├── auditor.py                   # Main statistical audit interface
├── README.md                    # Spanish README
├── README_ENG.md                # English README
├── CHANGELOG.md
├── requirements.txt
├── LICENSE
└── CITATION.cff
```

---

## 3. Installation

```bash
git clone https://github.com/Hackelman1/pqc-statistical-auditor.git
cd pqc-statistical-auditor
pip install -r requirements.txt
```

---

## 4. Execution & Reproducibility

### Full Automated Rebuild From Scratch
To clean previous results, run the unit test suite, execute all experiments, and regenerate all CSVs, plots, and reports:

```bash
python scripts/rebuild_all.py
```

### Direct Statistical Audit Invocation
To audit a specific transformation directly from the python audit interface:

```python
from auditor import analyze_scheme

# Compression audit (d=10) on Kyber512
analyze_scheme(scheme="Kyber512", transformation="compression", parameters={"d": 10})
```

---

## 5. Exported Artifacts (`results/`)

- `final_table.csv`: Unified dataset for LWE $Z_q \to Z_m$ projection experiments.
- `kyber_transform_table.csv`: Audit dataset for real implementation transformations in Kyber512/768/1024.
- `dsa_transform_table.csv`: Unified audit dataset for transformations in ML-DSA (FIPS 204).
- `summary_report.md`: Consolidated executive report.
- `final_validation_report.md`: Technical validation report.
- `*.png`: Robustness plots, uniformization heatmaps, and compression/rounding bias figures.

### ML-DSA (FIPS 204) Statistical Audit Results — Sample $N = 500,000$ ($B = 256$, $P = 500$)

| Scheme | Function | Parameters | Density $N/K_{XY}$ | $\chi^2$ $p$-value | $I_{\text{MM}}$ (bits) | Null Mean $\pm$ Std (bits) | Add-One $p$-value | Leakage FDR $q$-value | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **ML-DSA-44** | `Decompose` | $\gamma_2=95232, \eta=2$ | $390.6$ | $0.4364$ | $0.000000$ | $0.00118 \pm 0.00042$ | $0.4291$ | $0.5149$ | **PASS** |
| **ML-DSA-65/87** | `Decompose` | $\gamma_2=261888, \eta=4$ | $217.0$ | $0.1689$ | $0.000000$ | $0.00214 \pm 0.00068$ | $0.4631$ | $0.5149$ | **PASS** |
| **ML-DSA-44** | `Power2Round` | $d=13, \eta=2$ | $390.6$ | $0.9207$ | $0.000000$ | $0.00119 \pm 0.00041$ | $0.5130$ | $0.5149$ | **PASS** |
| **ML-DSA-65/87** | `Power2Round` | $d=13, \eta=4$ | $217.0$ | $0.5779$ | $0.000000$ | $0.00212 \pm 0.00068$ | $0.4870$ | $0.5149$ | **PASS** |
| **ML-DSA-44** | `MakeHint` | $\gamma_2=95232, \eta=2$ | $25000.0$ | $0.8672$ | $0.000000$ | $0.00002 \pm 0.00001$ | $0.6248$ | $0.6248$ | **PASS** |
| **ML-DSA-65/87** | `MakeHint` | $\gamma_2=261888, \eta=4$ | $13888.8$ | $0.6950$ | $0.000000$ | $0.00003 \pm 0.00001$ | $0.5888$ | $0.6248$ | **PASS** |

---

## 6. What This Framework DOES and DOES NOT Prove

- **DOES Prove**:
  - Modular projections with $\gcd(q, m) = 1$ destroy the observable statistical structure of the noise under the structural independence condition ($e \bmod m \perp\!\!\!\perp k q \bmod m$) verified with probability $\ge 1 - 2\eta/q$ (negligible, $10^{-3}$ to $10^{-7}$ depending on the scheme) via modular boundary decoupling (see Section 4.2 of the paper).
  - Real implementation transformations of compression, rounding, decomposition, and hint generation in Kyber (FIPS 203) and ML-DSA (FIPS 204) preserve high uniformity and afford no statistical advantage to an adversary.
- **DOES NOT Prove**:
  - Any cryptographic security break or key recovery vulnerability in standardized ML-KEM / Kyber (FIPS 203) or ML-DSA / Dilithium (FIPS 204).
  - Physical side-channel vulnerabilities (SPA/DPA) outside the data-level statistical noise model.

---

## 7. Citation

```bibtex
@software{Hackelman_PQC_Statistical_Auditor_2026,
  author = {Hackelman},
  title = {Modular Projection Effects and Implementation Audit in LWE, ML-KEM, and ML-DSA},
  year = {2026},
  version = {2.0.0},
  url = {https://github.com/Hackelman1/pqc-statistical-auditor}
}
```

---

## 8. License

Distributed under the [MIT License](LICENSE).
