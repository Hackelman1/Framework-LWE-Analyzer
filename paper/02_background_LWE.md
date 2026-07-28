## 2. Mathematical Background

### 2.1 LWE, M-LWE Definitions and Notation
Let $q \ge 3$ be an odd integer and $n = 256$ the degree of the defining ring polynomial $R_q = \mathbb{Z}_q[X]/(X^n + 1)$. An LWE or Module-LWE (M-LWE) instance generates samples over $\mathbb{Z}_q$ or $R_q^k$ of the form:
$$b = A s_1 + s_2 \pmod q$$
where:
- $s_1 \in R_q^l$ and $s_2 \in R_q^k$ are secret key and noise vectors.
- $A \in R_q^{k \times l}$ is the public uniform matrix $A \leftarrow U(R_q^{k \times l})$.
- $b \in R_q^k$ is the public observation vector.

In **ML-KEM (FIPS 203)**, $q = 3329$ and error terms follow a Centered Binomial Distribution. In **ML-DSA (FIPS 204)**, $q = 8380417$ and secret key vectors are sampled from a bounded discrete uniform distribution.

### 2.2 Secret and Noise Distributions

#### 1. Centered Binomial Distribution ($\text{CBD}$)
Used in ML-KEM, the distribution $\text{CBD}(\eta)$ is defined as the difference of two independent binomial random variables:
$$e = \sum_{i=1}^\eta a_i - \sum_{i=1}^\eta b_i, \quad a_i, b_i \leftarrow U(\{0, 1\})$$
The theoretical probability mass function (PMF) for $e \in [-\eta, \eta]$ satisfies $P(e = k) = \frac{1}{4^\eta} \binom{2\eta}{\eta + k}$. Upon modular reduction $e \bmod m$, if $m > 2\eta + 1$, the support does not wrap around and the distribution preserves its statistical asymmetry.

#### 2. Bounded Discrete Uniform Distribution $U([-\eta, \eta])$
Used in ML-DSA (FIPS 204) for secret key vectors $S_1$ and $S_2$, where coefficients are chosen equiprobably from a small integer range:
$$S_{1,i}, S_{2,i} \sim U([-\eta, \eta]), \quad \text{with } \eta \in \{2, 4\}$$
The theoretical PMF for each coefficient is $P(S = k) = \frac{1}{2\eta + 1}$ for all $k \in [-\eta, \eta]$.

### 2.3 ML-DSA (FIPS 204) Arithmetic Parameters
Implementation-level transformations in ML-DSA operate over the primary modulus $q = 8380417 = 2^{23} - 2^{13} + 1$ and employ the following constants across security levels:
- **Public Key Truncation ($d$)**: $d = 13$ bits, with residue space $2^d = 8192$.
- **Decomposition Parameters ($\gamma_2$)**: $\gamma_2 = 95232 = (q-1)/88$ (ML-DSA-44) or $\gamma_2 = 261888 = (q-1)/32$ (ML-DSA-65/87).
- **Masking Bounds ($\gamma_1$)**: $\gamma_1 = 2^{17} = 131072$ (ML-DSA-44) or $\gamma_1 = 2^{19} = 524288$ (ML-DSA-65/87).
