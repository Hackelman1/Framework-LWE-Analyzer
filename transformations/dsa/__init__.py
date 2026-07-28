"""
Módulo de Auditoría de Transformaciones para ML-DSA / Dilithium (FIPS 204).
"""
from transformations.dsa.decompose import decompose_fips204, audit_decompose_transformation
from transformations.dsa.power2round import power2round_fips204, audit_power2round_transformation
from transformations.dsa.hint import make_hint_fips204, use_hint_fips204, audit_hint_transformation

__all__ = [
    'decompose_fips204',
    'audit_decompose_transformation',
    'power2round_fips204',
    'audit_power2round_transformation',
    'make_hint_fips204',
    'use_hint_fips204',
    'audit_hint_transformation'
]


