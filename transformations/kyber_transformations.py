import numpy as np
import math
from typing import Dict, Tuple, Union, List

def compress_q(x: Union[int, np.ndarray], q: int = 3329, d: int = 10) -> Union[int, np.ndarray]:
    """
    Función Compress_d(x) según FIPS 203 (ML-KEM):
    Compress_d(x) = round((2^d / q) * (x mod q)) mod 2^d
    """
    scale = (1 << d) / float(q)
    res = np.round(scale * (x % q)).astype(int) % (1 << d)
    if isinstance(x, (int, np.integer)):
        return int(res)
    return res

def decompress_q(y: Union[int, np.ndarray], q: int = 3329, d: int = 10) -> Union[int, np.ndarray]:
    """
    Función Decompress_d(y) según FIPS 203 (ML-KEM):
    Decompress_d(y) = round((q / 2^d) * y) mod q
    """
    scale = float(q) / (1 << d)
    res = np.round(scale * y).astype(int) % q
    if isinstance(y, (int, np.integer)):
        return int(res)
    return res

def modular_reduce(x: Union[int, np.ndarray], q: int = 3329, mode: str = "exact") -> Union[int, np.ndarray]:
    """
    Aplica reducción modular sobre x.
    Modos:
    - 'exact': x mod q estándar en [0, q-1]
    - 'centered': x mod q en [-(q-1)//2, (q-1)//2]
    - 'biased': Simula una reducción imprecisa o con desbordamiento impreciso en implementación.
    """
    if mode == "exact":
        res = x % q
    elif mode == "centered":
        res = (x + (q // 2)) % q - (q // 2)
    elif mode == "biased":
        # Simula sesgo de redondeo/reducción imperfecta (ej. Barrett/Montgomery truncado)
        raw = x % q
        bias = np.where(raw > (q // 2), 1, 0) if isinstance(raw, np.ndarray) else (1 if raw > (q // 2) else 0)
        res = (raw - bias) % q
    else:
        raise ValueError(f"Modo de reducción desconocido: {mode}")
    return res

def coefficient_pack(poly: np.ndarray, q: int = 3329, d: int = 12) -> bytes:
    """
    Empaqueta un polinomio (o arreglo de coeficientes) en formato de d bits por coeficiente.
    """
    poly_flat = poly.flatten() % (1 << d)
    bit_str = ""
    for val in poly_flat:
        bit_str += f"{int(val):0{d}b}"[::-1]  # Little-endian bit ordering
    
    # Pad to full byte
    if len(bit_str) % 8 != 0:
        bit_str += "0" * (8 - (len(bit_str) % 8))
        
    byte_arr = bytearray()
    for i in range(0, len(bit_str), 8):
        byte_chunk = bit_str[i:i+8][::-1]
        byte_arr.append(int(byte_chunk, 2))
    return bytes(byte_arr)

def coefficient_unpack(bytestr: bytes, q: int = 3329, d: int = 12, length: int = 256) -> np.ndarray:
    """
    Desempaqueta una cadena de bytes a un arreglo de coeficientes de d bits.
    """
    bit_str = ""
    for b in bytestr:
        bit_str += f"{b:08b}"[::-1]
        
    coeffs = []
    for i in range(length):
        start = i * d
        end = start + d
        if end > len(bit_str):
            break
        chunk = bit_str[start:end][::-1]
        val = int(chunk, 2) % (1 << d)
        coeffs.append(val)
    return np.array(coeffs, dtype=int)

def simulate_kyber_rounding(poly: np.ndarray, q: int = 3329, d: int = 10) -> Dict:
    """
    Simula el proceso de compresión y descompresión (round-trip) sobre un polinomio.
    Calcula el error de redondeo Δ = (x_decomp - x_orig) mod q.
    """
    poly_mod = poly % q
    compressed = compress_q(poly_mod, q, d)
    decompressed = decompress_q(compressed, q, d)
    
    # Error centrado
    err = (decompressed - poly_mod + (q // 2)) % q - (q // 2)
    return {
        'original': poly_mod,
        'compressed': compressed,
        'decompressed': decompressed,
        'rounding_error': err
    }

def compute_entropy(data: np.ndarray, num_bins: int = None) -> float:
    """
    Calcula la Entropía de Shannon H(X) en bits.
    """
    flat = data.flatten()
    if num_bins is None:
        counts = np.bincount(flat)
    else:
        counts = np.bincount(flat, minlength=num_bins)
    probs = counts / float(np.sum(counts))
    nonzero = probs[probs > 0]
    return float(-np.sum(nonzero * np.log2(nonzero)))

def compute_statistical_distance(p: np.ndarray, q_dist: np.ndarray) -> float:
    """
    Calcula la Distancia Estadística (Total Variation Distance): SD(P, Q) = 0.5 * sum(|P_i - Q_i|)
    """
    p_norm = p / np.sum(p)
    q_norm = q_dist / np.sum(q_dist)
    return float(0.5 * np.sum(np.abs(p_norm - q_norm)))

def compute_kl_divergence(p: np.ndarray, q_dist: np.ndarray, eps: float = 1e-12) -> float:
    """
    Calcula la Divergencia de Kullback-Leibler D_KL(P || Q) en bits.
    """
    p_smooth = np.clip(p, eps, 1.0)
    q_smooth = np.clip(q_dist, eps, 1.0)
    p_smooth /= np.sum(p_smooth)
    q_smooth /= np.sum(q_smooth)
    return float(np.sum(p_smooth * np.log2(p_smooth / q_smooth)))

def compute_mutual_information(x: np.ndarray, y: np.ndarray, bins_x: int = None, bins_y: int = None) -> float:
    """
    Calcula la Información Mutua I(X; Y) = H(X) + H(Y) - H(X, Y) en bits.
    """
    flat_x = x.flatten()
    flat_y = y.flatten()
    
    if bins_x is None:
        bins_x = int(np.max(flat_x)) + 1 if len(flat_x) > 0 else 1
    if bins_y is None:
        bins_y = int(np.max(flat_y)) + 1 if len(flat_y) > 0 else 1
        
    hist2d, _, _ = np.histogram2d(flat_x, flat_y, bins=[bins_x, bins_y])
    pxy = hist2d / np.sum(hist2d)
    
    px = np.sum(pxy, axis=1)
    py = np.sum(pxy, axis=0)
    
    px_nz = px[px > 0]
    py_nz = py[py > 0]
    hx = -np.sum(px_nz * np.log2(px_nz))
    hy = -np.sum(py_nz * np.log2(py_nz))
    
    pxy_nz = pxy[pxy > 0]
    hxy = -np.sum(pxy_nz * np.log2(pxy_nz))
    
    mi = max(0.0, float(hx + hy - hxy))
    return mi
