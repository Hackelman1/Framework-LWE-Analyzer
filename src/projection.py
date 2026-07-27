import numpy as np

class AlgebraicProjection:
    """
    Módulo 2: Proyección Algebraica desde Z_q hacia Z/6Z.
    Transforma la instancia LWE (A, b, s, e) mod q en (A_6, b_6, s_6, e_6) mod 6.
    """

    def __init__(self, target_modulus: int = 6):
        self.target_modulus = target_modulus

    def project(self, lwe_instance: dict) -> dict:
        """
        Aplica la proyección mod target_modulus (6) a los componentes de la instancia LWE.
        :param lwe_instance: Diccionario con 'A', 'b', 's', 'e', 'q'
        :return: Diccionario proyectado con 'A6', 'b6', 's6', 'e6'
        """
        mod = self.target_modulus
        A = lwe_instance['A']
        b = lwe_instance['b']
        s = lwe_instance['s']
        e = lwe_instance['e']
        q = lwe_instance['q']

        A6 = A % mod
        b6 = b % mod
        s6 = s % mod
        
        # Para el ruido e: en Z_q, e se representa en [0, q-1] o en [-eta, eta].
        # Si se parte de e (original CBD, ej. -2 a +2): e_mod_6 = e % mod.
        # También el ruido efectivo percibido proyectando b - A*s mod q a mod 6:
        # e_proj = (b % mod - (A % mod).dot(s % mod)) % mod
        e6 = e % mod
        e_effective6 = (b6 - A6.dot(s6)) % mod

        return {
            'A6': A6,
            'b6': b6,
            's6': s6,
            'e6': e6,
            'e_effective6': e_effective6,
            'target_modulus': mod,
            'original_q': q
        }
