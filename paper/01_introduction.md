# Modular Projection Effects in LWE: Algebraic Conditions for Statistical Noise Uniformization and Implementation Auditing in ML-KEM and ML-DSA

**Author**: Hackelman  
**Date**: July 28, 2026  
**Classification**: Mathematical Cryptography / Lattice-Based Cryptography / Applied Stochastics  

---

## 1. Introduction

### Context and Motivation
Lattice-based cryptographic schemes standardized by NIST in **ML-KEM (Kyber / FIPS 203)** and **ML-DSA (Dilithium / FIPS 204)** base their security on the hardness of the **Learning With Errors (LWE)**, **Module-LWE (M-LWE)**, and **Module Short Integer Solution (M-SIS)** problems over primary modular rings $\mathbb{Z}_q$. Public observations $b = A s + e \pmod q$ mask secret key vectors $s$ via non-uniform centered noise $e$ (typically Centered Binomial Distributions, CBD, or bounded uniform distributions).

In algebraic analysis, resistance testing, and implementation auditing, projective homomorphic reductions to smaller residual rings $\mathbb{Z}_m$ ($m \ll q$) as well as arithmetic decomposition, truncation, and rounding functions are frequently evaluated. A fundamental question arises: **Does observable noise or residual structure under these operations retain the non-uniformity of the original distribution, or does it undergo statistical uniformization? Furthermore, do implementation-level transformations leak mutual information regarding secret key vectors?**

This work presents the complete mathematical characterization and empirical validation of the **LWE Modular Uniformization Theorem**. We extend the framework to perform a comprehensive statistical audit of implementation transformations across **ML-KEM (FIPS 203)** and **ML-DSA (FIPS 204)**—covering compression, byte packing, residue decomposition (`Decompose`), public key rounding (`Power2Round`), and hint vector generation (`MakeHint` / `UseHint`). Evaluated across $N = 500,000$ samples with Miller-Madow bias-corrected mutual information, add-one smoothed permutation tests, internal Bonferroni sweep aggregation, and Benjamini-Hochberg False Discovery Rate (FDR) control across $M = 23$ canonical leakage hypotheses, we demonstrate that actual implementation operators preserve statistical noise independence and leak zero secret information.
