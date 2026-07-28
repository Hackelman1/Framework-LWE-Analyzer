from typing import List, Dict, Any
from schemes.module_lwe.kyber_transform_audit import KyberTransformAuditor
from schemes.module_lwe.parameters import KYBER_512
from transformations.dsa.audit_utils import aggregate_sweep_p_value, compute_mutual_information_robust


def run_kem_suite() -> List[Dict[str, Any]]:
    """Ejecuta la suite de auditoría ML-KEM / Kyber (FIPS 203) (Experimentos T a W - 4 Experimentos)."""
    auditor = KyberTransformAuditor(params=KYBER_512, seed=42)

    # Exp T - Compresión
    res_t = auditor.audit_compression_bias(d=10, trials=50)
    res_t["experiment_id"] = "Exp_T_Kyber_Compress"

    # Exp U - Redondeo
    res_u = auditor.audit_rounding_bias(d=10, trials=50)
    res_u["experiment_id"] = "Exp_U_Kyber_Rounding"

    # Exp V - Reducción Modular
    res_v = auditor.audit_modular_reduction(trials=50, reduction_type="biased")
    res_v["experiment_id"] = "Exp_V_Kyber_ModularReduction"

    # Exp W - Pack/Unpack
    res_w = auditor.audit_pack_unpack_leakage(d=12, trials=50)
    res_w["experiment_id"] = "Exp_W_Kyber_PackUnpack"

    return [res_t, res_u, res_v, res_w]
