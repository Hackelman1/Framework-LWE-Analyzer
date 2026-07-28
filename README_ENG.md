[Español](README.md) | **English**

# Statistical Evaluation and Audit Framework for LWE / ML-KEM / ML-DSA (Release v2.0)
[![DOI](https://zenodo.org/badge/1313642539.svg)](https://doi.org/10.5281/zenodo.21622274)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Release v2.0.0](https://img.shields.io/badge/release-v2.0.0-green.svg)](https://github.com/Hackelman1/pqc-statistical-auditor)


Official v2.0.0 release of the theoretical and experimental framework for analyzing statistical noise uniformization in Learning With Errors (LWE), Ring-LWE, Module-LWE, and comprehensive statistical auditing of real implementation transformations in **ML-KEM (FIPS 203)** and **ML-DSA (FIPS 204)**.

---

## 1. Scope & Key Discoveries

1. **LWE Modular Uniformization Theorem**: Contractive statistical distance bound under circular convolution:
   $$\delta(P(e_{\text{effective}}), U(\mathbb{Z}_m)) \le \delta(P(k q \bmod m), U(\mathbb{Z}_m))$$
2. **Algebraic Criteria**: Complete effective noise uniformization requires $\gcd(q, m) = 1$ and sufficient dispersion of the modular wrapping term $k = \lfloor (A s + e)/q \rfloor \bmod m$.
3. **Noise-Free Proof ($e=0$)**: Mathematical and empirical proof that uniformization is driven intrinsically by the wrapping term $k$, independently of the noise magnitude $e$.
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

### ML-DSA (FIPS 204) Statistical Audit Results — Sample $N = 500,000$

| Scheme | Transformation | Parameters | Entropy $H$ (bits) | Max $H$ | $\chi^2$ $p$-value | $I(S_1; \text{out})$ | $I(S_2; \text{out})$ | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **ML-DSA-44** | `Decompose` | $\gamma_2=95232, \eta=2$ | $17.2347$ | $17.5392$ | $0.4364$ | $0.000000$ | $0.000000$ | **PASS** |
| **ML-DSA-65/87** | `Decompose` | $\gamma_2=261888, \eta=4$ | $18.1350$ | $18.9986$ | $0.1689$ | $0.000000$ | $0.000000$ | **PASS** |
| **ML-DSA-44** | `Power2Round` | $d=13, \eta=2$ | $12.9884$ | $13.0000$ | $0.9207$ | $0.000519$ | $0.001273$ | **PASS** |
| **ML-DSA-65/87** | `Power2Round` | $d=13, \eta=4$ | $12.9882$ | $13.0000$ | $0.5779$ | $0.002707$ | $0.003116$ | **PASS** |
| **ML-DSA-44** | `MakeHint` | $\gamma_2=95232, \eta=2$ | $0.0833$ | $1.0000$ | $0.8672$ | $0.000000$ | $0.000000$ | **PASS** |
| **ML-DSA-65/87** | `MakeHint` | $\gamma_2=261888, \eta=4$ | $0.0258$ | $1.0000$ | $0.6950$ | $0.000000$ | $0.000000$ | **PASS** |

---

## 6. What This Framework DOES and DOES NOT Prove

- **DOES Prove**:
  - Modular projections with $\gcd(q, m) = 1$ destroy the observable statistical structure of LWE, ML-KEM, and ML-DSA error terms.
  - Real implementation transformations of compression, rounding, decomposition, and hint generation in Kyber (FIPS 203) and ML-DSA (FIPS 204) preserve high uniformity and afford no statistical advantage to an adversary.
- **DOES NOT Prove**:
  - Any cryptographic security break or key recovery vulnerability in standardized ML-KEM / Kyber (FIPS 203) or ML-DSA / Dilithium (FIPS 204).
  - Physical side-channel vulnerabilities (SPA/DPA) outside the data-level statistical noise model.

---

## 7. Citation

```bibtex
@software{Peinador_PQC_Statistical_Auditor_2026,
  author = {Peinador, Ricardo},
  title = {Modular Projection Effects and Implementation Audit in LWE, ML-KEM, and ML-DSA},
  year = {2026},
  version = {2.0.0},
  url = {https://github.com/pqc-statistical-auditor/pqc-statistical-auditor}
}
```

---

## 8. License

Distributed under the [MIT License](LICENSE).
