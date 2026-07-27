import math
import numpy as np
from typing import Dict, List, Set

class SubgroupAnalysis:
    """
    Módulo 2 de la Fase 4: Análisis del Subgrupo Generado G(q,m) = <q> en Z_m.
    Evalúa la capacidad de enmascaramiento basada en:
    |G(q,m)| = m / gcd(q,m)
    """

    @staticmethod
    def generated_subgroup(q: int, m: int) -> List[int]:
        """
        Devuelve el conjunto de elementos en el subgrupo generado G(q,m) = {k * q mod m | k in Z}.
        """
        elements = set()
        for k in range(m):
            elements.add((k * q) % m)
        return sorted(list(elements))

    @staticmethod
    def subgroup_size(q: int, m: int) -> int:
        """
        Calcula el tamaño del subgrupo generado: |G(q,m)| = m / gcd(q,m).
        """
        return m // math.gcd(q, m)

    @classmethod
    def analyze_masking_capacity(cls, q: int, m: int) -> Dict:
        """
        Calcula métricas algebraicas de la capacidad de mezcla del término de envoltorio.
        """
        g_elements = cls.generated_subgroup(q, m)
        gcd_val = math.gcd(q, m)
        size_g = len(g_elements)
        is_full = (gcd_val == 1)

        max_subgroup_entropy = float(np.log2(size_g))
        max_full_entropy = float(np.log2(m))
        masking_ratio = float(size_g / m)

        return {
            'q': q,
            'm': m,
            'gcd': gcd_val,
            'subgroup': g_elements,
            'subgroup_size': size_g,
            'is_full_subgroup': is_full,
            'max_subgroup_entropy': max_subgroup_entropy,
            'max_full_entropy': max_full_entropy,
            'masking_ratio': masking_ratio
        }
