from dataclasses import dataclass

@dataclass
class KyberParams:
    name: str
    k: int
    q: int = 3329
    n: int = 256
    eta1: int = 2
    eta2: int = 2

KYBER_512 = KyberParams(name="Kyber512", k=2, eta1=3, eta2=2)
KYBER_768 = KyberParams(name="Kyber768", k=3, eta1=2, eta2=2)
KYBER_1024 = KyberParams(name="Kyber1024", k=4, eta1=2, eta2=2)
