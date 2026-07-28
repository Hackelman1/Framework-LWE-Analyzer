from typing import List, Dict, Any
from src.experiments import ExperimentRunner
from transformations.dsa.audit_utils import aggregate_sweep_p_value


def run_lwe_suite() -> List[Dict[str, Any]]:
    """Ejecuta la suite de Experimentos LWE (Experimentos A a P - 16 Experimentos)

    y retorna la lista de resultados con sus correspondientes empirical_p_value.
    """
    runner = ExperimentRunner(seed=42)
    results = []

    res_a = runner.run_experiment_a()
    res_a["experiment_id"] = "Exp_A"
    results.append(res_a)

    res_b = runner.run_experiment_b()
    res_b["experiment_id"] = "Exp_B"
    results.append(res_b)

    res_c = runner.run_experiment_c()
    res_c["experiment_id"] = "Exp_C"
    results.append(res_c)

    res_d = runner.run_experiment_d()
    res_d["experiment_id"] = "Exp_D"
    results.append(res_d)

    res_e = runner.run_experiment_e()
    res_e["experiment_id"] = "Exp_E"
    results.append(res_e)

    res_f = runner.run_experiment_f()
    res_f["experiment_id"] = "Exp_F"
    results.append(res_f)

    res_g = runner.run_experiment_g()
    res_g["experiment_id"] = "Exp_G"
    results.append(res_g)

    res_h = runner.run_experiment_h()
    res_h["experiment_id"] = "Exp_H"
    results.append(res_h)

    res_i = runner.run_experiment_i()
    res_i["experiment_id"] = "Exp_I"
    results.append(res_i)

    res_j1 = runner.run_experiment_j_part1()
    res_j2 = runner.run_experiment_j_part2()
    p_j = aggregate_sweep_p_value([res_j1["empirical_p_value"], res_j2["empirical_p_value"]])
    res_j = {
        "experiment_id": "Exp_J",
        "empirical_p_value": float(p_j),
        "part1": res_j1,
        "part2": res_j2
    }
    results.append(res_j)

    res_k = runner.run_experiment_k()
    res_k["experiment_id"] = "Exp_K"
    results.append(res_k)

    res_l = runner.run_experiment_l()
    res_l["experiment_id"] = "Exp_L"
    results.append(res_l)

    res_m = runner.run_experiment_m()
    res_m["experiment_id"] = "Exp_M"
    results.append(res_m)

    res_n = runner.run_experiment_n()
    res_n["experiment_id"] = "Exp_N"
    results.append(res_n)

    res_o = runner.run_experiment_o()
    res_o["experiment_id"] = "Exp_O"
    results.append(res_o)

    res_p = runner.run_experiment_p()
    res_p["experiment_id"] = "Exp_P"
    results.append(res_p)

    return results
