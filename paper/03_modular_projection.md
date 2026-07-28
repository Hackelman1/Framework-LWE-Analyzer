## 3. Modular Projection Model $\mathbb{Z}_q \to \mathbb{Z}_m$ and Generalized Decompositions

### 3.1 Linear Modular Projection
Consider the homomorphic projection $\pi_m: \mathbb{Z}_q \to \mathbb{Z}_m$ defined by the modulo $m$ operator:
$$A_m = A \bmod m, \quad b_m = b \bmod m, \quad s_m = s \bmod m$$

### 3.2 Observable Effective Noise
A public observer computes the projected residual combination:
$$e_{\text{effective}} = (b_m - A_m s_m) \bmod m$$

In unreduced arithmetic over the integers $\mathbb{Z}$, the M-LWE sample relation satisfies the exact identity:
$$A s + e = k q + b$$
where $k = \lfloor (A s + e)/q \rfloor \in \mathbb{Z}^{m_{\text{samples}}}$ is the integer modular wrapping term (quotient).

Projecting modulo $m$:
$$e_{\text{effective}} \equiv (e \bmod m - k (q \bmod m)) \pmod m$$
This proves that the observable noise in linear modular projections is the combination (via discrete circular convolution) of the reduced original noise $e \bmod m$ and the modulated wrapping variable $-k (q \bmod m) \pmod m$.

### 3.3 Extension to Implementation Transformations (ML-KEM / ML-DSA)
In real-world FIPS 203 and FIPS 204 standards, projections do not occur solely via linear modular reductions $\bmod m$, but also through non-linear decomposition and bit truncation operators:
1. **Public Key Truncation (`Power2Round`)**: Maps $t \in \mathbb{Z}_q$ to $(t_1, t_0)$ where the projected residue $t_0 = t \bmod 2^d \in [-2^{d-1}+1, 2^{d-1}]$ acts as effective compression noise.
2. **Commitment Decomposition (`Decompose`)**: Maps $r \in \mathbb{Z}_q$ to $(r_1, r_0)$ with $r_0 \in [-\gamma_2, \gamma_2]$, isolating the low-part projected residue.
3. **Carry Hints (`MakeHint`)**: Modulates the discrepancy between high-part projections $\text{HighBits}(z_0 + z_1)$ and $\text{HighBits}(z_1)$, representing a discrete boolean projection of the modular carry.
