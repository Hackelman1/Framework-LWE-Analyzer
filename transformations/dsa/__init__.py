"""
Módulo de Auditoría de Transformaciones para ML-DSA / Dilithium (FIPS 204).
"""
from transformations.dsa.decompose import decompose_fips204, audit_decompose_transformation

__all__ = ['decompose_fips204', 'audit_decompose_transformation']
